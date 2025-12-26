from typing import Dict, Any


class DetailBuilder:
    """Normalizes validation details for persistence."""

    def __init__(self):
        self.details: Dict[str, Any] = {}

    def add(self, key: str, value: Any) -> None:
        self.details[key] = value

    def merge(self, payload: Dict[str, Any]) -> None:
        self.details.update(payload)

    def build(self) -> Dict[str, Any]:
        return self.details
