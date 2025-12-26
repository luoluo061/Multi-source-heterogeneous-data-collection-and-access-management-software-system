from typing import Dict

from sqlalchemy.orm import Session

from app.models.entities import IngestionRun
from app.services.run_state import RunStatus


class QueueMetrics:
    """Computes queue depth per source."""

    def __init__(self, db: Session):
        self.db = db

    def depth(self) -> Dict[int, int]:
        rows = (
            self.db.query(IngestionRun.source_id, IngestionRun.run_id)
            .filter(IngestionRun.status == RunStatus.PENDING.value)
            .all()
        )
        counts: Dict[int, int] = {}
        for source_id, _ in rows:
            counts[source_id] = counts.get(source_id, 0) + 1
        return counts
