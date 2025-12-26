import threading
import time
from datetime import datetime, timezone
from typing import Dict

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.entities import IngestionRun, SourceConfig
from app.scheduler.timeout_monitor import TimeoutMonitor
from app.services.rate_limiter import RateLimiter
from app.services.run_cleanup import RunCleanupService
from app.services.run_health import RunHealthService
from app.services.ingestion_service import IngestionService
from app.services.run_queue import RunQueue
from app.services.run_state import RunStatus
from app.services.monitor_service import MonitorService
from app.storage.retention import RetentionPolicy
from app.storage.retention_task import RetentionTask
from app.services.queue_metrics import QueueMetrics


class Scheduler:
    """Interval-based scheduler that triggers enabled sources with schedules and dispatches queued runs."""

    def __init__(self, session_factory, interval_seconds: int = 10):
        self.session_factory = session_factory
        self.interval_seconds = interval_seconds
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._last_run: Dict[int, datetime] = {}
        self.logger = get_logger(__name__)
        self.rate_limiter = RateLimiter(interval_seconds=interval_seconds)

    def start(self):
        if not self._thread.is_alive():
            self._thread.start()
            self.logger.info("Scheduler started")

    def stop(self):
        self._stop_event.set()
        self._thread.join(timeout=5)
        self.logger.info("Scheduler stopped")

    def _run_loop(self):
        while not self._stop_event.is_set():
            try:
                self._check_sources()
                self._drain_queue()
                self._report_health()
            except Exception:  # pragma: no cover - background safeguard
                self.logger.exception("Scheduler iteration failed")
            time.sleep(self.interval_seconds)

    def _check_sources(self):
        session: Session = self.session_factory()
        try:
            sources = (
                session.query(SourceConfig)
                .filter(SourceConfig.enabled == True, SourceConfig.schedule != None)
                .all()
            )
            for source in sources:
                schedule_conf = source.schedule_dict() or {}
                interval = schedule_conf.get("interval_seconds")
                if not interval:
                    continue
                last_run = self._last_run.get(source.id)
                now = datetime.now(timezone.utc)
                if not last_run or (now - last_run).total_seconds() >= interval:
                    self._last_run[source.id] = now
                    if not self.rate_limiter.allow(source.id):
                        continue
                    self.logger.info(
                        "Triggering scheduled run", extra={"source_id": source.id, "run_id": "scheduler"}
                    )
                    service = IngestionService(session)
                    try:
                        service.trigger_run(source.id)
                    except Exception:
                        self.logger.exception("Scheduled run failed", extra={"source_id": source.id})
        finally:
            session.close()

    def _drain_queue(self):
        session: Session = self.session_factory()
        try:
            TimeoutMonitor(session).sweep()
            RunCleanupService(session).cleanup()
            RetentionPolicy(session).enforce()
            RetentionTask(session).run()
            sources = session.query(SourceConfig).filter(SourceConfig.enabled == True).all()
            for source in sources:
                queue = RunQueue(session)
                if queue.has_running(source.id):
                    continue
                pending = queue.next_for_source(source.id)
                if pending:
                    self.logger.info("Dispatching queued run", extra={"source_id": source.id, "run_id": pending.run_id})
                    service = IngestionService(session)
                    try:
                        service._execute_run(pending, source)
                    except Exception:
                        self.logger.exception("Queued run failed", extra={"source_id": source.id})
        finally:
            session.close()

    def _report_health(self):
        session: Session = self.session_factory()
        try:
            monitor = MonitorService(session).snapshot()
            self.logger.info("Monitor snapshot", extra={"run_id": "-", "source_id": "-", "payload": monitor})
        finally:
            session.close()
