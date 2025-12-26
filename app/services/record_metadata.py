from typing import Dict

from app.validation.schema_hint import SchemaHint


class RecordMetadataService:
    """Derives additional metadata from payloads."""

    def build(self, payload: bytes, fmt: str) -> Dict:
        hint = SchemaHint.infer(payload, fmt)
        return {"schema_hint": hint}
