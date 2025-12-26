from typing import Dict

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.entities import RawRecord


class RecordStatsService:
    """Aggregates record statistics for monitoring."""

    def __init__(self, db: Session):
        self.db = db

    def by_format(self) -> Dict[str, int]:
        rows = self.db.query(RawRecord.format, func.count(RawRecord.record_id)).group_by(RawRecord.format).all()
        return {fmt: count for fmt, count in rows}

    def by_status(self) -> Dict[str, int]:
        rows = (
            self.db.query(RawRecord.validation_status, func.count(RawRecord.record_id))
            .group_by(RawRecord.validation_status)
            .all()
        )
        return {status: count for status, count in rows}

    def totals(self) -> Dict[str, int]:
        return {"records": self.db.query(func.count(RawRecord.record_id)).scalar() or 0}
