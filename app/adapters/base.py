from typing import List


class SourceAdapter:
    """Interface for retrieving raw payloads from a configured source."""

    def __init__(self, params: dict):
        self.params = params

    def fetch(self) -> List[bytes]:
        raise NotImplementedError
