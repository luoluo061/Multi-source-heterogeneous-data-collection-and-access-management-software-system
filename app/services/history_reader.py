from pathlib import Path
from typing import List

from app.core.config import settings


class HistoryReader:
    """Reads run history lines written by AuditLogger/HistoryTracker."""

    def __init__(self, history_path: Path | None = None):
        self.path = history_path or settings.log_dir / "run_history.jsonl"

    def read(self, run_id: str) -> List[str]:
        if not self.path.exists():
            return []
        lines = []
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                if run_id in line:
                    lines.append(line.strip())
        return lines
