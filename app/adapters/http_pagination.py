from typing import Any, Dict, Iterable, List, Optional


class OffsetPagination:
    """Simple offset/limit pagination helper."""

    def __init__(self, limit: int, start: int = 0, max_pages: int = 10):
        self.limit = limit
        self.offset = start
        self.max_pages = max_pages

    def steps(self) -> Iterable[Dict[str, int]]:
        for _ in range(self.max_pages):
            yield {"offset": self.offset, "limit": self.limit}
            self.offset += self.limit


class NextUrlPagination:
    """Pagination helper for API responses that provide a `next` URL."""

    def __init__(self, max_pages: int = 10):
        self.max_pages = max_pages

    def extract_next(self, payload: Any) -> Optional[str]:
        if isinstance(payload, dict):
            next_link = payload.get("next") or payload.get("next_url")
            if isinstance(next_link, str):
                return next_link
        return None

    def steps(self, first_url: str, extractor) -> Iterable[str]:
        current = first_url
        for _ in range(self.max_pages):
            yield current
            payload = extractor()
            current = self.extract_next(payload)
            if not current:
                break
