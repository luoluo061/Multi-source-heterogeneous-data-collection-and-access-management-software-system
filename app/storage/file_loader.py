from pathlib import Path
from typing import Optional

from app.core.logging import get_logger


class FileLoader:
    """Reads payload files with graceful error handling."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def read(self, path_str: str) -> Optional[bytes]:
        path = Path(path_str)
        try:
            if path.exists():
                return path.read_bytes()
        except Exception:
            self.logger.exception("Failed to read payload file", extra={"run_id": "-", "source_id": "-", "payload": path_str})
        return None
