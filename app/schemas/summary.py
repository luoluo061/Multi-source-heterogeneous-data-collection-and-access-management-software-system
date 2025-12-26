from typing import Dict

from pydantic import BaseModel


class RunSummary(BaseModel):
    counts: Dict[str, int]
