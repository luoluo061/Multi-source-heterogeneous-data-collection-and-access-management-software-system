from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.entities import IngestionRun
from app.services.run_state import RunStatus


class RunCleanupService:
    """Cleans stale pending runs older than a grace period."""

    def __init__(self, db: Session, grace_minutes: int = 60):
        self.db = db
        self.grace_minutes = grace_minutes
        self.logger = get_logger(__name__)

    def cleanup(self) -> None:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=self.grace_minutes)
        stale = (
            self.db.query(IngestionRun)
            .filter(IngestionRun.status == RunStatus.PENDING.value, IngestionRun.started_at < cutoff)
            .all()
        )
        for run in stale:
            run.status = RunStatus.CANCELED.value
            run.error_message = "Stale pending run canceled by cleanup"
            self.logger.info("Canceling stale run", extra={"run_id": run.run_id, "source_id": run.source_id})
        self.db.commit()
