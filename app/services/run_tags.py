from typing import Dict, List

from app.core.logging import get_logger


class RunTags:
    """Adds lightweight tags to runs for observability."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def attach(self, run_id: str, source_id: int, tags: List[str] | None = None, attributes: Dict | None = None) -> None:
        tags = tags or []
        attributes = attributes or {}
        payload = {"tags": tags, "attributes": attributes}
        self.logger.info("run_tags", extra={"run_id": run_id, "source_id": source_id, "payload": payload})

    def annotate(self, run_id: str, source_id: int, note: str) -> None:
        self.logger.info("run_note", extra={"run_id": run_id, "source_id": source_id, "payload": {"note": note}})
