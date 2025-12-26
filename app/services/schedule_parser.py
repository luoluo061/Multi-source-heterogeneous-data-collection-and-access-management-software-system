from typing import Dict


class ScheduleParser:
    """Parses schedule configuration dictionaries."""

    @staticmethod
    def interval_seconds(schedule: Dict | None) -> int:
        if not schedule:
            return 0
        try:
            interval = int(schedule.get("interval_seconds", 0))
            return max(interval, 0)
        except Exception:
            return 0
