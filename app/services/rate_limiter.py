from datetime import datetime, timedelta
from typing import Dict


class RateLimiter:
    """In-memory per-source rate limiter for scheduler triggers."""

    def __init__(self, interval_seconds: int = 5):
        self.interval = timedelta(seconds=interval_seconds)
        self.last_seen: Dict[int, datetime] = {}

    def allow(self, source_id: int) -> bool:
        now = datetime.utcnow()
        last = self.last_seen.get(source_id)
        if last and (now - last) < self.interval:
            return False
        self.last_seen[source_id] = now
        return True
