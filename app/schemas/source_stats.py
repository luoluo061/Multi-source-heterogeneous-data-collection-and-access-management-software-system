from typing import Dict

from pydantic import BaseModel


class SourceStats(BaseModel):
    totals: Dict[str, int]
