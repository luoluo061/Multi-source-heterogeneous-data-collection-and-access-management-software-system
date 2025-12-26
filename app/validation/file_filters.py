from pathlib import Path
from typing import Iterable, List


class FileFilter:
    """Filters files by extension and optional minimum size."""

    def __init__(self, allow_extensions: Iterable[str] | None = None, min_size: int = 1):
        self.allow_extensions = {ext.lower() for ext in allow_extensions or []}
        self.min_size = min_size

    def allowed(self, file_path: Path) -> bool:
        if self.allow_extensions and file_path.suffix.lower() not in self.allow_extensions:
            return False
        if file_path.stat().st_size < self.min_size:
            return False
        return True
