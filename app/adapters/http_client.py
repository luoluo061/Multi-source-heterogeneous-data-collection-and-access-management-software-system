import time
from typing import Dict, Optional

import httpx

from app.core.config import settings
from app.core.error_codes import ErrorCode
from app.core.errors import AdapterError, RetryableError


class HttpClient:
    """HTTP client with simple retry/backoff for transient network errors."""

    def __init__(self, timeout: float = 10.0, max_retries: int | None = None, backoff_seconds: int | None = None):
        self.timeout = timeout
        self.max_retries = settings.max_retries if max_retries is None else max_retries
        self.backoff_seconds = settings.retry_backoff_seconds if backoff_seconds is None else backoff_seconds

    def request(self, method: str, url: str, *, headers: Optional[Dict[str, str]] = None, params=None, json=None, data=None):
        attempt = 0
        while True:
            try:
                response = httpx.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    json=json,
                    data=data,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                return response
            except httpx.RequestError as exc:
                attempt += 1
                if attempt > self.max_retries:
                    raise AdapterError(f"HTTP request failed after retries: {exc}", ErrorCode.RETRYABLE) from exc
                time.sleep(self.backoff_seconds)
            except httpx.HTTPStatusError as exc:
                # Non-retryable status errors
                raise AdapterError(f"HTTP status error: {exc}", ErrorCode.ADAPTER_RUNTIME) from exc
