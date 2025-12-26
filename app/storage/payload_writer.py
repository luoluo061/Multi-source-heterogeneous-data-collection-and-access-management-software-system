from typing import List

from sqlalchemy.orm import Session

from app.core.error_codes import ErrorCode
from app.core.errors import StorageError
from app.models.entities import RawRecord


class PayloadWriter:
    """Persists normalized raw payloads with metadata."""

    def __init__(self, db: Session):
        self.db = db

    def write_many(self, records: List[dict]) -> List[RawRecord]:
        stored = []
        try:
            for item in records:
                record = RawRecord(
                    run_id=item["run_id"],
                    source_id=item["source_id"],
                    format=item["format"],
                    raw_size=item["raw_size"],
                    payload=item["payload"].decode("utf-8", errors="replace"),
                    checksum=item["checksum"],
                    validation_status=item["validation_status"],
                    validation_message=item["validation_message"],
                    content_type=item.get("content_type"),
                    source_uri=item.get("source_uri"),
                    status_code=item.get("status_code"),
                    row_count=item.get("row_count"),
                    columns=item.get("columns"),
                )
                self.db.add(record)
                stored.append(record)
            self.db.commit()
            return stored
        except Exception as exc:
            self.db.rollback()
            raise StorageError(f"Failed to persist raw records: {exc}", ErrorCode.STORAGE_FAILED) from exc
