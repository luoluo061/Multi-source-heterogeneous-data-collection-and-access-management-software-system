import hashlib
from typing import List

from sqlalchemy.orm import Session

from app.models.entities import RawRecord


def persist_raw_records(
    db: Session,
    *,
    run_id: str,
    source_id: int,
    items: List[dict],
) -> List[RawRecord]:
    stored = []
    for item in items:
        payload_bytes = item["payload"]
        checksum = hashlib.sha256(payload_bytes).hexdigest()
        record = RawRecord(
            run_id=run_id,
            source_id=source_id,
            format=item["format"],
            raw_size=item["raw_size"],
            payload=payload_bytes.decode("utf-8", errors="replace"),
            checksum=checksum,
            validation_status=item["validation_status"],
            validation_message=item["validation_message"],
            error_code=item.get("validation_code"),
            validation_details=item.get("validation_details"),
            content_type=item.get("content_type"),
            source_uri=item.get("source_uri"),
            status_code=item.get("status_code"),
            row_count=item.get("row_count"),
            columns=item.get("columns"),
            metadata_json=item.get("metadata_json"),
            payload_path=item.get("payload_path"),
        )
        db.add(record)
        stored.append(record)
    db.commit()
    return stored
