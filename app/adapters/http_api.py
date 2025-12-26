import json
from typing import Dict, List, Optional

from app.adapters.base import SourceAdapter
from app.adapters.http_auth import HttpAuth
from app.adapters.http_client import HttpClient
from app.adapters.http_request_builder import HttpRequestBuilder
from app.adapters.http_response_parser import HttpResponseParser
from app.adapters.raw_payload import RawPayload
from app.core.error_codes import ErrorCode
from app.core.errors import AdapterConfigurationError, AdapterError, RetryableError
from app.adapters.http_pagination import OffsetPagination


class HttpAPISource(SourceAdapter):
    """Fetches payloads from an HTTP JSON endpoint with pagination and retries."""

    def __init__(self, params: dict):
        super().__init__(params)
        self.client = HttpClient(timeout=params.get("timeout", 10.0))
        self.request_builder = HttpRequestBuilder(params)

    def _build_headers(self) -> Dict[str, str]:
        headers = self.request_builder.headers()
        token = self.params.get("token")
        headers.update(HttpAuth.bearer(token))
        return headers

    def _make_request(self, method: str, url: str, *, params=None, json_body=None, data=None):
        try:
            response = self.client.request(
                method,
                url,
                headers=self._build_headers(),
                params=params,
                json=json_body,
                data=data,
            )
            return response
        except AdapterError:
            raise
        except Exception as exc:
            raise RetryableError(f"HTTP request failed: {exc}", ErrorCode.RETRYABLE) from exc

    def _build_payload(self, response) -> bytes:
        try:
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                return json.dumps(response.json()).encode("utf-8")
            return response.content
        except Exception as exc:
            raise AdapterError(f"Failed to build payload: {exc}", ErrorCode.ADAPTER_RUNTIME) from exc

    def _iterate_pages(self, url: str):
        pagination = self.params.get("pagination") or {}
        mode = pagination.get("mode")
        max_pages = pagination.get("max_pages", 5)
        limit = pagination.get("limit", 50)
        offset = pagination.get("offset", 0)
        current_url = url

        if mode == "offset":
            pager = OffsetPagination(limit=limit, start=offset, max_pages=max_pages)
            for step in pager.steps():
                response = self._make_request(
                    self.params.get("method", "GET"),
                    current_url,
                    params={**self.params.get("query", {}), **step},
                    json_body=self.params.get("body"),
                )
                yield response
                payload_json = response.json()
                if len(payload_json) < limit:
                    break
        elif mode == "next_url":
            next_url = current_url
            for _ in range(max_pages):
                response = self._make_request(self.params.get("method", "GET"), next_url, json_body=self.params.get("body"))
                yield response
                payload = response.json()
                next_url = payload.get("next") or payload.get("next_url")
                if not next_url:
                    break
        else:
            response = self._make_request(self.params.get("method", "GET"), current_url, params=self.params.get("query"), json_body=self.params.get("body"))
            yield response

    def fetch(self) -> List[dict]:
        url = self.params.get("url")
        if not url:
            raise AdapterConfigurationError("HTTP API source missing 'url'")
        self.request_builder.method()  # validate method

        payloads: List[dict] = []
        for response in self._iterate_pages(url):
            parsed = HttpResponseParser.to_payload(response)
            payloads.append(parsed.__dict__)
        return payloads
