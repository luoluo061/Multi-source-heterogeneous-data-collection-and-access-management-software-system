from typing import Dict

from sqlalchemy.orm import Session

from app.services.queue_metrics import QueueMetrics
from app.services.run_health import RunHealthService


class MonitorService:
    """Bundles health and queue metrics for periodic reporting."""

    def __init__(self, db: Session):
        self.db = db

    def snapshot(self) -> Dict:
        health = RunHealthService(self.db).snapshot()
        queues = QueueMetrics(self.db).depth()
        return {"health": health, "queues": queues}
