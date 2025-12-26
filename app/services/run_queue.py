from typing import Optional

from sqlalchemy.orm import Session

from app.models.entities import IngestionRun
from app.services.run_state import RunStatus


class RunQueue:
    """Simple queue interface to fetch and update pending runs."""

    def __init__(self, db: Session):
        self.db = db

    def next_for_source(self, source_id: int) -> Optional[IngestionRun]:
        return (
            self.db.query(IngestionRun)
            .filter(IngestionRun.source_id == source_id, IngestionRun.status == RunStatus.PENDING.value)
            .order_by(IngestionRun.started_at.asc())
            .first()
        )

    def mark_running(self, run: IngestionRun) -> None:
        run.status = RunStatus.RUNNING.value
        self.db.commit()

    def has_running(self, source_id: int) -> bool:
        return (
            self.db.query(IngestionRun)
            .filter(IngestionRun.source_id == source_id, IngestionRun.status == RunStatus.RUNNING.value)
            .first()
            is not None
        )
