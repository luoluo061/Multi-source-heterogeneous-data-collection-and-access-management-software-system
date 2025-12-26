from typing import Dict

from pydantic import BaseModel


class RecordStats(BaseModel):
    totals: Dict[str, int]
    by_format: Dict[str, int]
    by_status: Dict[str, int]
