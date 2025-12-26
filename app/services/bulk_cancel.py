from typing import List

from sqlalchemy.orm import Session

from app.models.entities import IngestionRun
from app.services.run_state import RunStatus


class BulkCancelService:
    """Cancels pending runs for a source."""

    def __init__(self, db: Session):
        self.db = db

    def cancel_pending(self, source_id: int) -> List[str]:
        runs = (
            self.db.query(IngestionRun)
            .filter(IngestionRun.source_id == source_id, IngestionRun.status == RunStatus.PENDING.value)
            .all()
        )
        ids = []
        for run in runs:
            run.status = RunStatus.CANCELED.value
            ids.append(run.run_id)
        self.db.commit()
        return ids
