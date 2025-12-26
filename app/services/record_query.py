from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.entities import RawRecord
from app.services.time_window import TimeWindow
from app.services.record_filter import RecordFilter
from app.services.payload_reader import PayloadReader
from app.services.record_limiter import RecordLimiter


class RecordQueryService:
    """Provides filtered access to raw records and payloads."""

    def __init__(self, db: Session):
        self.db = db

    def _parse_dt(self, text: Optional[str]) -> Optional[datetime]:
        if not text:
            return None
        try:
            return datetime.fromisoformat(text)
        except Exception:
            return None

    def list_records(
        self,
        *,
        run_id: Optional[str],
        source_id: Optional[int],
        fmt: Optional[str],
        validation_status: Optional[str],
        from_time: Optional[str],
        to_time: Optional[str],
        sort: str,
        page: int,
        page_size: int,
    ) -> Tuple[int, List[RawRecord]]:
        start, end = TimeWindow.parse(from_time, to_time)
        record_filter = RecordFilter(
            run_id=run_id,
            source_id=source_id,
            fmt=fmt,
            validation_status=validation_status,
            start=start,
            end=end,
        )
        query = record_filter.apply(self.db.query(RawRecord))
        page_size = RecordLimiter().clamp(page_size)
        total = query.count()
        if sort == "asc":
            query = query.order_by(RawRecord.ingest_time.asc())
        else:
            query = query.order_by(RawRecord.ingest_time.desc())
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return total, items

    def get_record(self, record_id: int) -> Optional[RawRecord]:
        return self.db.query(RawRecord).filter(RawRecord.record_id == record_id).first()

    def get_payload(self, record_id: int) -> Tuple[Optional[bytes], Optional[str]]:
        reader = PayloadReader(self.db)
        return reader.fetch(record_id)
