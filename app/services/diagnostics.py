from typing import Dict

from app.services.monitor_service import MonitorService
from app.services.runtime_info import RuntimeInfo
from app.services.record_stats import RecordStatsService
from app.services.version_info import VersionInfo


class DiagnosticsService:
    """Aggregates diagnostic information for operators."""

    def __init__(self, db):
        self.db = db

    def snapshot(self) -> Dict:
        runtime = RuntimeInfo().as_dict()
        monitor = MonitorService(self.db).snapshot()
        stats = RecordStatsService(self.db)
        return {
            "runtime": runtime,
            "health": monitor.get("health"),
            "queues": monitor.get("queues"),
            "record_totals": stats.totals(),
            "record_status": stats.by_status(),
            "versions": VersionInfo.snapshot(),
        }
