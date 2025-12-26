from datetime import datetime
from typing import Optional, Tuple


def parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def build_run_filters(
    source_id: Optional[int] = None,
    status: Optional[str] = None,
    from_ts: Optional[str] = None,
    to_ts: Optional[str] = None,
) -> Tuple[Optional[int], Optional[str], Optional[datetime], Optional[datetime]]:
    return source_id, status, parse_datetime(from_ts), parse_datetime(to_ts)
