import json
from typing import Dict, Optional

from app.core.errors import ValidationError


class JsonRules:
    """Validates JSON structure with depth and node limits."""

    @staticmethod
    def validate(
        payload: bytes,
        *,
        max_depth: int = 10,
        max_nodes: int = 5000,
        max_array_length: int = 1000,
    ) -> Dict:
        try:
            data = json.loads(payload.decode("utf-8", errors="replace"))
        except Exception as exc:
            raise ValidationError(f"JSON parse error: {exc}")
        nodes = 0

        def walk(obj, depth: int) -> None:
            nonlocal nodes
            if depth > max_depth:
                raise ValidationError("JSON exceeds max depth")
            nodes += 1
            if nodes > max_nodes:
                raise ValidationError("JSON exceeds max nodes")
            if isinstance(obj, dict):
                for v in obj.values():
                    walk(v, depth + 1)
            elif isinstance(obj, list):
                if len(obj) > max_array_length:
                    raise ValidationError("JSON array too long")
                for v in obj:
                    walk(v, depth + 1)

        walk(data, 0)
        return {"nodes": nodes}
