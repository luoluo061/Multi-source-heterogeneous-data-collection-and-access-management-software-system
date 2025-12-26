from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.models.entities import IngestionRun
from app.services.run_state import RunStatus


class TimeoutMonitor:
    """Marks long-running runs as FAILED due to timeout."""

    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)

    def sweep(self) -> None:
        now = datetime.now(timezone.utc)
        timeout_seconds = settings.run_timeout_seconds
        candidates = (
            self.db.query(IngestionRun)
            .filter(IngestionRun.status == RunStatus.RUNNING.value)
            .all()
        )
        for run in candidates:
            if not run.started_at:
                continue
            elapsed = (now - run.started_at).total_seconds()
            if elapsed >= timeout_seconds:
                run.status = RunStatus.FAILED.value
                run.error_code = "TIMEOUT"
                run.error_message = f"Run exceeded timeout of {timeout_seconds}s"
                run.finished_at = now
                self.logger.info("Marking run as timeout", extra={"run_id": run.run_id, "source_id": run.source_id})
        self.db.commit()
