import random
import time
from typing import Iterable


class Backoff:
    """Exponential backoff generator with jitter."""

    def __init__(self, base: float = 1.0, factor: float = 2.0, max_interval: float = 30.0, max_retries: int = 3):
        self.base = base
        self.factor = factor
        self.max_interval = max_interval
        self.max_retries = max_retries

    def intervals(self) -> Iterable[float]:
        current = self.base
        for _ in range(self.max_retries):
            jitter = random.uniform(0, current)
            yield min(self.max_interval, current + jitter)
            current *= self.factor

    def sleep_cycle(self) -> None:
        for interval in self.intervals():
            time.sleep(interval)
