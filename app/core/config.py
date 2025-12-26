from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-level settings with defaults suitable for local runs."""

    database_url: str = "sqlite:///./data/app.db"
    log_dir: Path = Path("logs")
    data_dir: Path = Path("data")
    max_payload_size_bytes: int = 5 * 1024 * 1024
    scheduler_interval_seconds: int = 10
    allow_queue_on_busy: bool = True
    run_timeout_seconds: int = 90
    retry_backoff_seconds: int = 2
    max_retries: int = 2
    storage_mode: str = "db"  # db | file
    dedupe_mode: str = "store"  # store | skip
    retention_days: int = 7

    model_config = SettingsConfigDict(env_prefix="INGEST_")


settings = Settings()
settings.log_dir.mkdir(parents=True, exist_ok=True)
settings.data_dir.mkdir(parents=True, exist_ok=True)
