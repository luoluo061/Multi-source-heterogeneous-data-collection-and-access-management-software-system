from typing import List

from pydantic import BaseModel


class TimelineEntry(BaseModel):
    label: str
    ts: str
    message: str
    stage: str


class RunTimeline(BaseModel):
    run_id: str
    items: List[TimelineEntry]
