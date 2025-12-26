from typing import Dict

from app.core.errors import ValidationError
from app.validation.encoding import EncodingDetector


class TextRules:
    """Validates plain text payloads with length constraints and encoding detection."""

    @staticmethod
    def validate(
        payload: bytes,
        *,
        max_bytes: int = 5 * 1024 * 1024,
        max_lines: int = 50000,
        max_line_length: int = 2000,
    ) -> Dict:
        if len(payload) > max_bytes:
            raise ValidationError("Text exceeds max bytes")
        encoding = EncodingDetector.detect(payload)
        text = payload.decode(encoding, errors="ignore")
        lines = text.splitlines()
        if len(lines) > max_lines:
            raise ValidationError("Text exceeds max lines")
        for line in lines:
            if len(line) > max_line_length:
                raise ValidationError("Text line too long")
        return {"encoding": encoding, "lines": len(lines)}
