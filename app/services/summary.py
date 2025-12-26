from typing import Dict

from sqlalchemy.orm import Session

from app.models.entities import IngestionRun


class RunSummaryService:
    """Aggregates run counts by status."""

    def __init__(self, db: Session):
        self.db = db

    def counts(self) -> Dict[str, int]:
        results = self.db.query(IngestionRun.status, IngestionRun.run_id).all()
        counts: Dict[str, int] = {}
        for status, _ in results:
            counts[status] = counts.get(status, 0) + 1
        return counts
