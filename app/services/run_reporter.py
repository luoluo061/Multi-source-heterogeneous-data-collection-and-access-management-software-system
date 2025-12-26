from typing import Dict

from app.core.audit import AuditLogger
from app.services.run_state import RunStatus
from app.storage.history_tracker import HistoryTracker


class RunReporter:
    """Emits audit logs for lifecycle events."""

    def __init__(self, audit: AuditLogger | None = None, history: HistoryTracker | None = None):
        self.audit = audit or AuditLogger(__name__)
        self.history = history or HistoryTracker()

    def started(self, run_id: str, source_id: int) -> None:
        payload = {"event": "started", "run_id": run_id, "source_id": source_id}
        self.audit.emit("started", run_id=run_id, source_id=source_id)
        self.history.append(payload)

    def finished(self, run_id: str, source_id: int, status: RunStatus, metrics: Dict) -> None:
        payload = {"event": "finished", "run_id": run_id, "source_id": source_id, "status": status.value, **metrics}
        self.audit.emit("finished", run_id=run_id, source_id=source_id, payload=payload)
        self.history.append(payload)

    def canceled(self, run_id: str, source_id: int) -> None:
        payload = {"event": "canceled", "run_id": run_id, "source_id": source_id}
        self.audit.emit("canceled", run_id=run_id, source_id=source_id)
        self.history.append(payload)
