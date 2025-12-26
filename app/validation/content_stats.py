import json
from dataclasses import dataclass
from typing import Dict


@dataclass
class ContentStats:
    lines: int
    preview: str

    def to_json(self) -> str:
        return json.dumps({"lines": self.lines, "preview": self.preview})


class ContentInspector:
    """Computes basic content statistics for traceability."""

    @staticmethod
    def analyze(payload: bytes) -> ContentStats:
        text = payload.decode("utf-8", errors="ignore")
        lines = text.splitlines()
        preview = "\n".join(lines[:3])[:200]
        return ContentStats(lines=len(lines), preview=preview)
