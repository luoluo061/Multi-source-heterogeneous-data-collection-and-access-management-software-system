from typing import List

from sqlalchemy.orm import Session

from app.models.entities import IngestionRun, RawRecord


class RetentionRules:
    """Applies retention by count per source."""

    def __init__(self, db: Session, max_runs_per_source: int = 500):
        self.db = db
        self.max_runs_per_source = max_runs_per_source

    def enforce_by_count(self):
        sources = [row[0] for row in self.db.query(IngestionRun.source_id).distinct().all()]
        for source_id in sources:
            runs = (
                self.db.query(IngestionRun)
                .filter(IngestionRun.source_id == source_id)
                .order_by(IngestionRun.started_at.desc())
                .all()
            )
            if len(runs) <= self.max_runs_per_source:
                continue
            to_delete = runs[self.max_runs_per_source :]
            run_ids = [r.run_id for r in to_delete]
            self.db.query(RawRecord).filter(RawRecord.run_id.in_(run_ids)).delete(synchronize_session=False)
            self.db.query(IngestionRun).filter(IngestionRun.run_id.in_(run_ids)).delete(synchronize_session=False)
        self.db.commit()
