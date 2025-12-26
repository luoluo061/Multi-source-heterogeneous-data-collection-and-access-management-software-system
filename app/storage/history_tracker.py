import json
from pathlib import Path
from typing import Dict


class HistoryTracker:
    """Persists lightweight run history for audit/analysis outside the DB."""

    def __init__(self, path: Path = Path("logs/run_history.jsonl")):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, entry: Dict) -> None:
        line = json.dumps(entry, ensure_ascii=False)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
