from typing import Dict

from pydantic import BaseModel


class DiagnosticsSnapshot(BaseModel):
    runtime: Dict
    health: Dict
    queues: Dict
    record_totals: Dict
    record_status: Dict
