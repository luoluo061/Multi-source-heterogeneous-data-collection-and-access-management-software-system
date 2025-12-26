import json
from typing import Optional

from app.adapters.raw_payload import RawPayload


class HttpResponseParser:
    """Converts HTTP responses into RawPayload instances."""

    @staticmethod
    def to_payload(response) -> RawPayload:
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            body = json.dumps(response.json()).encode("utf-8")
        else:
            body = response.content
        return RawPayload(
            body=body,
            content_type=content_type,
            url=str(response.url),
            status_code=response.status_code,
        )
