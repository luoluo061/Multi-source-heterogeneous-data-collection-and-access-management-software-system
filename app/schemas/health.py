from typing import Dict

from pydantic import BaseModel


class RunHealth(BaseModel):
    counts: Dict[str, int]
