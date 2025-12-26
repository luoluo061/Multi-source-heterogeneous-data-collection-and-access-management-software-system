from app.core.logging import get_logger
from app.services.metrics import RunMetrics


class RunMetricsLogger:
    """Logs run metrics at completion time."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def log(self, run_id: str, source_id: int, metrics: RunMetrics):
        payload = {
            "records": getattr(metrics, "records_count", None),
            "bytes": getattr(metrics, "bytes_total", None),
            "duration_ms": metrics.duration_ms,
        }
        self.logger.info("run_metrics", extra={"run_id": run_id, "source_id": source_id, "payload": payload})
