from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict


@dataclass
class RunContext:
    run_id: str
    source_id: int
    started_at: datetime
    schedule_triggered: bool = False
    metadata: Dict | None = None

    def as_dict(self) -> Dict:
        data = asdict(self)
        data["started_at"] = self.started_at.isoformat()
        return data


def new_context(run_id: str, source_id: int, schedule_triggered: bool = False, metadata: Dict | None = None) -> RunContext:
    return RunContext(run_id=run_id, source_id=source_id, started_at=datetime.now(timezone.utc), schedule_triggered=schedule_triggered, metadata=metadata)
