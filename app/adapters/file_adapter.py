import hashlib
from pathlib import Path
from typing import List, Optional, Tuple

from app.adapters.base import SourceAdapter
from app.adapters.file_strategy import FileStrategy
from app.adapters.raw_payload import RawPayload
from app.core.error_codes import ErrorCode
from app.core.errors import AdapterConfigurationError, AdapterError
from app.storage.index_store import FileIndexStore
from app.validation.file_filters import FileFilter
from app.validation.encoding import EncodingDetector


class FileSource(SourceAdapter):
    """Reads files from a directory with incremental checkpoints and encoding detection."""

    def __init__(self, params: dict):
        super().__init__(params)
        self.index_store = FileIndexStore(Path(params.get("state_path", ".state/file_index.json")))

    def _should_skip(self, file_path: Path, strategy: str) -> bool:
        if strategy == "mtime":
            return self.index_store.is_seen_mtime(file_path)
        return self.index_store.is_seen_checksum(file_path)

    def _remember(self, file_path: Path, strategy: str, checksum: Optional[str] = None) -> None:
        if strategy == "mtime":
            self.index_store.record_mtime(file_path)
        else:
            if checksum:
                self.index_store.record_checksum(file_path, checksum)

    def _read_file(self, file_path: Path) -> Tuple[bytes, str]:
        raw_bytes = file_path.read_bytes()
        encoding = EncodingDetector.detect(raw_bytes)
        try:
            text = raw_bytes.decode(encoding, errors="ignore")
            return text.encode("utf-8"), encoding
        except Exception as exc:
            raise AdapterError(f"Failed to decode file {file_path}: {exc}", ErrorCode.ADAPTER_RUNTIME) from exc

    def fetch(self) -> List[dict]:
        directory = Path(self.params.get("directory", ""))
        pattern = self.params.get("pattern", "*.csv")
        strategy = FileStrategy(self.params.get("incremental", "mtime"))
        strategy.validate()
        max_size = int(self.params.get("max_size_bytes", 5 * 1024 * 1024))
        filter_ext = FileFilter(allow_extensions=self.params.get("extensions"))
        if not directory.exists():
            raise AdapterConfigurationError(f"Directory {directory} does not exist")

        results: List[dict] = []
        for file_path in directory.glob(pattern):
            if not file_path.is_file():
                continue
            if file_path.stat().st_size > max_size:
                continue
            if not filter_ext.allowed(file_path):
                continue
            if self._should_skip(file_path, strategy.mode):
                continue
            payload, encoding = self._read_file(file_path)
            checksum = hashlib.sha256(payload).hexdigest()
            results.append(
                RawPayload(
                    body=payload,
                    content_type=f"text/{file_path.suffix.strip('.') or 'plain'}; charset=utf-8",
                    url=str(file_path),
                    status_code=200,
                    encoding=encoding,
                    checksum=checksum,
                ).__dict__
            )
            self._remember(file_path, strategy.mode, checksum=checksum)
        self.index_store.save()
        return results
