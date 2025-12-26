from dataclasses import dataclass, asdict
from typing import Dict

from app.core.logging import get_logger


@dataclass
class TraceContext:
    run_id: str
    source_id: int
    correlation_id: str

    def as_dict(self) -> Dict:
        return asdict(self)


class TraceEmitter:
    """Emits correlation identifiers for tracing across logs."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def emit(self, context: TraceContext) -> None:
        self.logger.info("trace_context", extra={"run_id": context.run_id, "source_id": context.source_id, "payload": context.as_dict()})
