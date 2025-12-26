import json
import os
import tempfile
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.core.error_codes import ErrorCode
from app.core.errors import StorageError
from app.storage.storage_mode import StorageMode


class FileSystemStorage:
    """Stores payloads on disk with atomic writes and dedupe options."""

    def __init__(self, base_dir: Path | None = None, dedupe_mode: str = "store"):
        self.base_dir = base_dir or settings.data_dir / "raw"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.dedupe_mode = dedupe_mode

    def _extension(self, content_type: Optional[str]) -> str:
        if not content_type:
            return "bin"
        if "json" in content_type:
            return "json"
        if "csv" in content_type:
            return "csv"
        if "text" in content_type or "plain" in content_type:
            return "txt"
        return "bin"

    def _target_path(self, run_id: str, source_id: int, ext: str) -> Path:
        run_dir = self.base_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir / f"{source_id}_{len(list(run_dir.glob('*')))}.{ext}"

    def write_payload(self, run_id: str, source_id: int, payload: bytes, content_type: Optional[str], checksum: str) -> Path:
        ext = self._extension(content_type)
        target = self._target_path(run_id, source_id, ext)
        if self.dedupe_mode == "skip" and target.exists():
            return target
        try:
            with tempfile.NamedTemporaryFile(delete=False, dir=target.parent, suffix=".tmp") as tmp:
                tmp.write(payload)
                tmp.flush()
                os.fsync(tmp.fileno())
                temp_path = Path(tmp.name)
            temp_path.rename(target)
            return target
        except Exception as exc:
            raise StorageError(f"File write failed: {exc}", ErrorCode.STORAGE_FAILED) from exc
