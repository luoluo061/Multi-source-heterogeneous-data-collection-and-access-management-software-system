import time
from datetime import datetime, timezone
from typing import Callable, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.error_codes import ErrorCode
from app.core.errors import AdapterError, RetryableError, SourceBusyError, SourceNotFoundError
from app.core.runtime import RuntimePolicy
from app.models.entities import IngestionRun, SourceConfig
from app.services.run_validator import RunValidator
from app.services.metrics import RunMetrics
from app.services.run_state import RunStatus


class RunManager:
    """Handles run lifecycle, concurrency control, retries, cancellation, and metrics."""

    def __init__(self, db: Session, runtime: Optional[RuntimePolicy] = None):
        self.db = db
        self.runtime = runtime or RuntimePolicy(
            allow_queue_on_busy=settings.allow_queue_on_busy,
            max_retries=settings.max_retries,
            retry_backoff_seconds=settings.retry_backoff_seconds,
            run_timeout_seconds=settings.run_timeout_seconds,
        )

    def create_run(self, source_id: int) -> IngestionRun:
        source = self.db.query(SourceConfig).filter(SourceConfig.id == source_id, SourceConfig.enabled == True).first()
        if not source:
            raise SourceNotFoundError("Source not found or disabled", ErrorCode.SOURCE_NOT_FOUND)

        active_run = (
            self.db.query(IngestionRun)
            .filter(
                and_(
                    IngestionRun.source_id == source_id,
                    IngestionRun.status.in_([RunStatus.PENDING.value, RunStatus.RUNNING.value]),
                )
            )
            .first()
        )
        if active_run and not self.runtime.allow_queue_on_busy:
            raise SourceBusyError("Source has an active run", ErrorCode.SOURCE_BUSY)

        run = IngestionRun(
            run_id=str(int(time.time() * 1000)),
            source_id=source_id,
            status=RunStatus.PENDING.value,
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def start_run(self, run: IngestionRun) -> None:
        RunValidator.ensure_transition(RunStatus(run.status), RunStatus.RUNNING)
        run.status = RunStatus.RUNNING.value
        run.error_code = ErrorCode.UNKNOWN
        run.error_message = None
        run.records_count = 0
        run.bytes_total = 0
        run.duration_ms = 0
        self.db.commit()

    def request_cancel(self, run_id: str) -> bool:
        run = self.db.query(IngestionRun).filter(IngestionRun.run_id == run_id).first()
        if not run:
            return False
        if run.status in [RunStatus.SUCCESS.value, RunStatus.FAILED.value, RunStatus.CANCELED.value]:
            return False
        run.cancellation_requested = True
        self.db.commit()
        return True

    def should_cancel(self, run: IngestionRun) -> bool:
        return bool(run.cancellation_requested)

    def execute_with_retry(self, func: Callable[[], None], metrics: RunMetrics, run: IngestionRun) -> None:
        attempts = 0
        start_time = datetime.now(timezone.utc)
        while True:
            if self.should_cancel(run):
                raise SourceBusyError("Run canceled", ErrorCode.CANCELED)
            if (datetime.now(timezone.utc) - start_time) > self.runtime.timeout_delta:
                raise AdapterError("Run timed out", ErrorCode.TIMEOUT)
            try:
                func()
                return
            except RetryableError as exc:
                attempts += 1
                if attempts > self.runtime.max_retries:
                    raise AdapterError(f"Retry attempts exceeded: {exc}", ErrorCode.RETRYABLE) from exc
                time.sleep(self.runtime.retry_backoff_seconds)
            except AdapterError:
                raise

    def finalize_run(
        self,
        run: IngestionRun,
        metrics: RunMetrics,
        status: RunStatus,
        error_code: str = ErrorCode.UNKNOWN,
        error_message: Optional[str] = None,
    ) -> None:
        run.status = status.value
        run.error_code = error_code
        run.error_message = error_message
        run.records_count = metrics.records_count
        run.bytes_total = metrics.bytes_total
        run.duration_ms = metrics.duration_ms
        run.finished_at = metrics.finished_at or datetime.now(timezone.utc)
        self.db.commit()
