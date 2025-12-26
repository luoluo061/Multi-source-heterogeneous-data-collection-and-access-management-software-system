from typing import List

from pydantic import BaseModel


class RunHistoryLine(BaseModel):
    raw: str


class RunHistoryResponse(BaseModel):
    run_id: str
    lines: List[RunHistoryLine]
