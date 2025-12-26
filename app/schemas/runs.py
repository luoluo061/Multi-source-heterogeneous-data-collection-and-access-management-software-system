from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RunRead(BaseModel):
    run_id: str
    source_id: int
    status: str
    message: Optional[str]
    error_code: Optional[str]
    error_message: Optional[str]
    records_count: int
    bytes_total: int
    duration_ms: int
    started_at: datetime
    finished_at: Optional[datetime]

    class Config:
        orm_mode = True


class TriggerResponse(BaseModel):
    run_id: str
    status: str


class RunListResponse(BaseModel):
    items: List[RunRead]
