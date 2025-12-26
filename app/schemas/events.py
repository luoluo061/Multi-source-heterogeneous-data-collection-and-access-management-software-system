from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class RunEventRead(BaseModel):
    event_id: int
    run_id: str
    ts: datetime
    stage: str
    event_type: str
    message: str
    error_code: Optional[str]

    class Config:
        orm_mode = True


class RunEventsPage(BaseModel):
    page: int
    page_size: int
    total: int
    items: List[RunEventRead]
