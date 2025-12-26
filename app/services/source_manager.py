import json
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.entities import SourceConfig


class SourceManager:
    """Encapsulates CRUD operations for sources."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, payload) -> SourceConfig:
        source = SourceConfig(
            name=payload.name,
            type=payload.type,
            enabled=payload.enabled,
            params=json.dumps(payload.params),
            schedule=json.dumps(payload.schedule) if payload.schedule else None,
        )
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source

    def update(self, source_id: int, payload) -> Optional[SourceConfig]:
        source = self.db.query(SourceConfig).filter(SourceConfig.id == source_id).first()
        if not source:
            return None
        if payload.name is not None:
            source.name = payload.name
        if payload.type is not None:
            source.type = payload.type
        if payload.enabled is not None:
            source.enabled = payload.enabled
        if payload.params is not None:
            source.params = json.dumps(payload.params)
        if payload.schedule is not None:
            source.schedule = json.dumps(payload.schedule)
        self.db.commit()
        self.db.refresh(source)
        return source

    def list(self) -> List[SourceConfig]:
        return self.db.query(SourceConfig).all()
