from dataclasses import dataclass
from typing import Dict


@dataclass
class RunFlags:
    manual_trigger: bool = True
    scheduled: bool = False

    def to_payload(self) -> Dict:
        return {"manual_trigger": self.manual_trigger, "scheduled": self.scheduled}

    @classmethod
    def from_schedule(cls) -> "RunFlags":
        return cls(manual_trigger=False, scheduled=True)

    @classmethod
    def from_manual(cls) -> "RunFlags":
        return cls(manual_trigger=True, scheduled=False)

    def merge(self, extra: Dict) -> Dict:
        payload = self.to_payload()
        payload.update(extra)
        return payload
