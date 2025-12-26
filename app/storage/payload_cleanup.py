from pathlib import Path
from typing import List

from app.core.logging import get_logger


class PayloadCleanup:
    """Deletes payload files for removed runs."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def delete_paths(self, paths: List[str]) -> None:
        for path_str in paths:
            if not path_str:
                continue
            path = Path(path_str)
            if path.exists():
                try:
                    path.unlink()
                except Exception:
                    self.logger.exception("Failed to delete payload path", extra={"run_id": "-", "source_id": "-", "payload": path_str})
