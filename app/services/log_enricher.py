from typing import Dict

from app.core.logging import get_logger


class LogEnricher:
    """Adds structured context to log output."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def emit(self, run_id: str, source_id: int, context: Dict) -> None:
        self.logger.info("context_enriched", extra={"run_id": run_id, "source_id": source_id, "payload": context})

    def complete(self, run_id: str, source_id: int, stats: Dict) -> None:
        self.logger.info("context_complete", extra={"run_id": run_id, "source_id": source_id, "payload": stats})

    def failure(self, run_id: str, source_id: int, error: str) -> None:
        self.logger.error("context_failure", extra={"run_id": run_id, "source_id": source_id, "payload": {"error": error}})
