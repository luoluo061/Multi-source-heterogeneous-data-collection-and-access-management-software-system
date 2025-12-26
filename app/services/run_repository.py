from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.entities import IngestionRun, SourceConfig
from app.services.run_state import RunStatus


class RunRepository:
    """Encapsulates run and source queries."""

    def __init__(self, db: Session):
        self.db = db

    def get_source(self, source_id: int) -> Optional[SourceConfig]:
        return self.db.query(SourceConfig).filter(SourceConfig.id == source_id, SourceConfig.enabled == True).first()

    def get_active_run(self, source_id: int) -> Optional[IngestionRun]:
        return (
            self.db.query(IngestionRun)
            .filter(
                and_(
                    IngestionRun.source_id == source_id,
                    IngestionRun.status.in_([RunStatus.PENDING.value, RunStatus.RUNNING.value]),
                )
            )
            .first()
        )

    def get_pending_runs(self, source_id: int, limit: int = 10) -> List[IngestionRun]:
        return (
            self.db.query(IngestionRun)
            .filter(IngestionRun.source_id == source_id, IngestionRun.status == RunStatus.PENDING.value)
            .order_by(IngestionRun.started_at.asc())
            .limit(limit)
            .all()
        )

    def list_runs(
        self,
        *,
        source_id: Optional[int] = None,
        status: Optional[str] = None,
        from_ts: Optional[datetime] = None,
        to_ts: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[IngestionRun]:
        query = self.db.query(IngestionRun)
        if source_id is not None:
            query = query.filter(IngestionRun.source_id == source_id)
        if status is not None:
            query = query.filter(IngestionRun.status == status)
        if from_ts is not None:
            query = query.filter(IngestionRun.started_at >= from_ts)
        if to_ts is not None:
            query = query.filter(IngestionRun.started_at <= to_ts)
        return query.order_by(IngestionRun.started_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
