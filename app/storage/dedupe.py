from app.storage.dedupe_index import DedupeIndex
from pathlib import Path


class DedupeStrategy:
    """Determines whether to skip storing based on checksum."""

    def __init__(self, mode: str = "store", state_path: Path | None = None):
        self.mode = mode
        self.index = DedupeIndex(state_path or Path(".state/dedupe_index.json"))

    def should_store(self, checksum: str) -> bool:
        if self.mode == "skip":
            if self.index.contains(checksum):
                return False
        self.index.add(checksum)
        self.index.save()
        return True
