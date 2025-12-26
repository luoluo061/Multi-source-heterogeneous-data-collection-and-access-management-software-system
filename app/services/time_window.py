from datetime import datetime
from typing import Optional, Tuple


class TimeWindow:
    """Parses ISO8601 time windows."""

    @staticmethod
    def parse(from_text: Optional[str], to_text: Optional[str]) -> Tuple[Optional[datetime], Optional[datetime]]:
        return TimeWindow._parse_dt(from_text), TimeWindow._parse_dt(to_text)

    @staticmethod
    def _parse_dt(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except Exception:
            return None
