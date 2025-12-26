from typing import List

from sqlalchemy.orm import Session

from app.storage.storage_engine import StorageEngine
from app.storage.raw_storage import persist_raw_records


class PayloadService:
    """Coordinates storage mode selection and persistence."""

    def __init__(self, db: Session, storage_engine: StorageEngine | None = None):
        self.db = db
        self.storage_engine = storage_engine or StorageEngine()

    def persist(self, run_id: str, source_id: int, records: List[dict]):
        stored_records = self.storage_engine.persist_payloads(records)
        return persist_raw_records(self.db, run_id=run_id, source_id=source_id, items=stored_records)
