from pathlib import Path
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.models.entities import RawRecord
from app.storage.file_loader import FileLoader


class PayloadReader:
    """Reads payloads from DB or filesystem depending on stored path."""

    def __init__(self, db: Session):
        self.db = db
        self.file_loader = FileLoader()

    def fetch(self, record_id: int) -> Tuple[Optional[bytes], Optional[str]]:
        record = self.db.query(RawRecord).filter(RawRecord.record_id == record_id).first()
        if not record:
            return None, None
        if record.payload_path:
            data = self.file_loader.read(record.payload_path)
            return data, record.content_type
        return record.payload.encode("utf-8"), record.content_type
