from typing import Any, Dict, Optional


class HttpRequestBuilder:
    """Normalizes HTTP request options from adapter params."""

    def __init__(self, params: dict):
        self.params = params

    def method(self) -> str:
        method = (self.params.get("method") or "GET").upper()
        if method not in {"GET", "POST"}:
            raise ValueError("Unsupported method")
        return method

    def url(self) -> str:
        url = self.params.get("url")
        if not url:
            raise ValueError("Missing url")
        return url

    def headers(self) -> Dict[str, str]:
        headers = self.params.get("headers", {}) or {}
        token = self.params.get("token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def query(self) -> Dict[str, Any]:
        return self.params.get("query", {}) or {}

    def body(self) -> Optional[Any]:
        return self.params.get("body")
