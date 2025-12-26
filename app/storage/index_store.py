import json
from pathlib import Path
from typing import Dict


class FileIndexStore:
    """Simple JSON-based index for tracking processed files."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.state = {"mtime": {}, "checksum": {}}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                self.state = json.loads(self.path.read_text())
            except Exception:
                self.state = {"mtime": {}, "checksum": {}}

    def is_seen_mtime(self, file_path: Path) -> bool:
        key = str(file_path)
        recorded = self.state["mtime"].get(key)
        current = file_path.stat().st_mtime
        return recorded is not None and recorded >= current

    def record_mtime(self, file_path: Path) -> None:
        self.state["mtime"][str(file_path)] = file_path.stat().st_mtime

    def is_seen_checksum(self, file_path: Path) -> bool:
        key = str(file_path)
        recorded = self.state["checksum"].get(key)
        if not recorded:
            return False
        current = file_path.read_bytes()
        return recorded == current

    def record_checksum(self, file_path: Path, checksum: str) -> None:
        self.state["checksum"][str(file_path)] = checksum

    def save(self) -> None:
        self.path.write_text(json.dumps(self.state))
