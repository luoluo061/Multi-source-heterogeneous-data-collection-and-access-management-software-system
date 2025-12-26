from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class RawRecordRead(BaseModel):
    record_id: int
    run_id: str
    source_id: int
    ingest_time: datetime
    format: str
    raw_size: int
    checksum: str
    validation_status: str
    validation_message: Optional[str]
    content_type: Optional[str]
    source_uri: Optional[str]
    status_code: Optional[int]
    row_count: Optional[int]
    columns: Optional[str]
    metadata_json: Optional[str]
    payload_path: Optional[str]

    class Config:
        orm_mode = True


class RecordsResponse(BaseModel):
    items: List[RawRecordRead]


class RecordReadSingle(RawRecordRead):
    payload: Optional[str] = None


class RecordsPage(BaseModel):
    page: int
    page_size: int
    total: int
    items: List[RawRecordRead]
