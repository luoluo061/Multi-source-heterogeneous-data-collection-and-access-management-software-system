from typing import Dict

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.entities import IngestionRun
from app.services.run_state import RunStatus


class RunHealthService:
    """Reports basic health metrics for active runs."""

    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)

    def snapshot(self) -> Dict[str, int]:
        counts = {"running": 0, "pending": 0, "failed": 0}
        for status, key in [
            (RunStatus.RUNNING.value, "running"),
            (RunStatus.PENDING.value, "pending"),
            (RunStatus.FAILED.value, "failed"),
        ]:
            total = self.db.query(IngestionRun).filter(IngestionRun.status == status).count()
            counts[key] = total
        self.logger.info("Run health snapshot", extra={"run_id": "-", "source_id": "-", "payload": counts})
        return counts
