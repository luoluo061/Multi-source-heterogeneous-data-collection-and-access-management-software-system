from datetime import datetime, timezone
from typing import Dict

from app.core.logging import get_logger


class AuditLogger:
    """Structured audit logging for run lifecycle events."""

    def __init__(self, name: str = __name__):
        self.logger = get_logger(name)

    def emit(self, event: str, *, run_id: str, source_id: int, payload: Dict | None = None) -> None:
        payload = payload or {}
        self.logger.info(
            f"audit:{event}",
            extra={
                "run_id": run_id,
                "source_id": source_id,
                "payload": payload,
                "ts": datetime.now(timezone.utc).isoformat(),
            },
        )
