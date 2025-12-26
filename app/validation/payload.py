from typing import Dict, List

from app.core.errors import ValidationError


class PayloadValidator:
    """Validates payload metadata completeness."""

    REQUIRED_FIELDS: List[str] = ["payload", "format", "raw_size", "validation_status"]

    @staticmethod
    def ensure_complete(record: Dict) -> None:
        missing = [field for field in PayloadValidator.REQUIRED_FIELDS if field not in record]
        if missing:
            raise ValidationError(f"Missing payload fields: {missing}")
