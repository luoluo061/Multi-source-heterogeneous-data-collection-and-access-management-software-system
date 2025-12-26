from typing import Dict

from sqlalchemy.orm import Session

from app.models.entities import IngestionRun


class SourceStatsService:
    """Aggregates per-source statistics from runs."""

    def __init__(self, db: Session):
        self.db = db

    def stats_for_source(self, source_id: int) -> Dict[str, int]:
        runs = self.db.query(IngestionRun).filter(IngestionRun.source_id == source_id).all()
        totals = {"runs": 0, "success": 0, "failed": 0, "canceled": 0, "records": 0, "bytes": 0}
        for run in runs:
            totals["runs"] += 1
            if run.status == "SUCCESS":
                totals["success"] += 1
            if run.status == "FAILED":
                totals["failed"] += 1
            if run.status == "CANCELED":
                totals["canceled"] += 1
            totals["records"] += run.records_count or 0
            totals["bytes"] += run.bytes_total or 0
        return totals
