from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.entities import IngestionRun, RawRecord
from app.storage.payload_cleanup import PayloadCleanup


class RetentionPolicy:
    """Deletes run metadata and records older than a retention window."""

    def __init__(self, db: Session, days: int = 7):
        self.db = db
        self.days = days
        self.logger = get_logger(__name__)

    def enforce(self) -> None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.days)
        old_runs = self.db.query(IngestionRun).filter(IngestionRun.started_at < cutoff).all()
        run_ids = [run.run_id for run in old_runs]
        payload_paths = [rec.payload_path for rec in self.db.query(RawRecord.payload_path).filter(RawRecord.run_id.in_(run_ids))]
        if not run_ids:
            return
        self.db.query(RawRecord).filter(RawRecord.run_id.in_(run_ids)).delete(synchronize_session=False)
        self.db.query(IngestionRun).filter(IngestionRun.run_id.in_(run_ids)).delete(synchronize_session=False)
        self.db.commit()
        PayloadCleanup().delete_paths([p[0] if isinstance(p, tuple) else p for p in payload_paths])
        self.logger.info("Retention enforced", extra={"run_id": "-", "source_id": "-", "payload": {"deleted_runs": len(run_ids)}})
