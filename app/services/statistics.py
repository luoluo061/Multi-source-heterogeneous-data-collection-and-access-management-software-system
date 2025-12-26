from dataclasses import dataclass


@dataclass
class RunStatistics:
    records: int = 0
    bytes_total: int = 0

    def update(self, payload: bytes) -> None:
        self.records += 1
        self.bytes_total += len(payload)

    def to_message(self) -> str:
        return f"records={self.records}, bytes={self.bytes_total}"
