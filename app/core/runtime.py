from dataclasses import dataclass
from datetime import timedelta


@dataclass
class RuntimePolicy:
    allow_queue_on_busy: bool = True
    max_retries: int = 2
    retry_backoff_seconds: int = 2
    run_timeout_seconds: int = 60
    cancel_running: bool = True

    @property
    def timeout_delta(self) -> timedelta:
        return timedelta(seconds=self.run_timeout_seconds)
