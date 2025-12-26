from pydantic import BaseModel


class ConfigSnapshot(BaseModel):
    database_url: str
    storage_mode: str
    dedupe_mode: str
    retention_days: int
    scheduler_interval_seconds: int
    max_payload_size_bytes: int
