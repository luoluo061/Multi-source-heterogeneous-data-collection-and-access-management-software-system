from app.core.config import settings


class ConfigService:
    """Exposes safe configuration for API clients."""

    def snapshot(self) -> dict:
        return {
            "database_url": settings.database_url,
            "storage_mode": settings.storage_mode,
            "dedupe_mode": settings.dedupe_mode,
            "retention_days": settings.retention_days,
            "scheduler_interval_seconds": settings.scheduler_interval_seconds,
            "max_payload_size_bytes": settings.max_payload_size_bytes,
        }
