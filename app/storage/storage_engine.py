from typing import List

from app.core.config import settings
from app.storage.dedupe import DedupeStrategy
from app.storage.file_system import FileSystemStorage
from app.storage.storage_mode import StorageMode


class StorageEngine:
    """Selects storage mode for raw payload persistence."""

    def __init__(self, mode: str | None = None, dedupe_mode: str | None = None):
        self.mode = StorageMode(mode or settings.storage_mode)
        self.dedupe = DedupeStrategy(dedupe_mode or settings.dedupe_mode)
        self.file_storage = FileSystemStorage(dedupe_mode=self.dedupe.mode)

    def persist_payloads(self, records: List[dict]) -> List[dict]:
        if self.mode == StorageMode.DB:
            return records
        stored: List[dict] = []
        for record in records:
            if not self.dedupe.should_store(record["checksum"]):
                continue
            path = self.file_storage.write_payload(
                run_id=record["run_id"],
                source_id=record["source_id"],
                payload=record["payload"],
                content_type=record.get("content_type"),
                checksum=record["checksum"],
            )
            record["payload_path"] = str(path)
            # strip large payload when using file mode to avoid DB bloat
            record["payload"] = b""
            stored.append(record)
        return stored
