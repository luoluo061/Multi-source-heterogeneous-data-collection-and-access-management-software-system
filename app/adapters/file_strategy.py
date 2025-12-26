from pathlib import Path
from typing import Callable


class FileStrategy:
    """Chooses the incremental strategy for file scanning."""

    def __init__(self, mode: str):
        self.mode = mode

    def should_use_mtime(self) -> bool:
        return self.mode == "mtime"

    def should_use_checksum(self) -> bool:
        return self.mode == "checksum"

    def validate(self):
        if self.mode not in {"mtime", "checksum"}:
            raise ValueError("Invalid incremental mode")

    def describe(self) -> str:
        return f"incremental={self.mode}"
