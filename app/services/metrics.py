from dataclasses import dataclass
from datetime import datetime


@dataclass
class RunMetrics:
    records_count: int = 0
    bytes_total: int = 0
    started_at: datetime | None = None
    finished_at: datetime | None = None

    @property
    def duration_ms(self) -> int:
        if not self.started_at or not self.finished_at:
            return 0
        return int((self.finished_at - self.started_at).total_seconds() * 1000)

    def add_payload(self, payload: bytes) -> None:
        self.records_count += 1
        self.bytes_total += len(payload)
