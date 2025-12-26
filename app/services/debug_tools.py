import json
from typing import Dict

from app.core.logging import get_logger
from app.models.entities import SourceConfig


class DebugTools:
    """Utility hooks for emitting structured debug information."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def snapshot_source(self, source: SourceConfig) -> None:
        snapshot = {
            "id": source.id,
            "type": source.type,
            "enabled": source.enabled,
            "has_schedule": bool(source.schedule),
        }
        self.logger.info("source_snapshot", extra={"run_id": "-", "source_id": source.id, "payload": snapshot})

    def dump_run_context(self, run_id: str, context: Dict) -> None:
        safe_context = json.dumps(context, ensure_ascii=False)
        self.logger.info("run_context", extra={"run_id": run_id, "source_id": context.get("source_id", "-"), "payload": safe_context})
