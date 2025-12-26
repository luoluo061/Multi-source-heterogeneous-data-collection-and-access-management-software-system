import json
from pathlib import Path
from typing import Set


class DedupeIndex:
    """Persists checksums to disk to survive restarts."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._checksums: Set[str] = set()
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text())
                self._checksums = set(data.get("checksums", []))
            except Exception:
                self._checksums = set()

    def save(self):
        self.path.write_text(json.dumps({"checksums": list(self._checksums)}))

    def add(self, checksum: str):
        self._checksums.add(checksum)

    def contains(self, checksum: str) -> bool:
        return checksum in self._checksums
