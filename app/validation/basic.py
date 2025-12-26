import csv
import io
import json

from app.core.config import settings
from app.validation.rules import RuleResult, ValidationRules
from app.validation.csv_rules import CsvRules
from app.validation.json_rules import JsonRules
from app.validation.text_rules import TextRules


class ValidationResult:
    def __init__(self, status: str, message: str = "", details: dict | None = None, code: str | None = None):
        self.status = status
        self.message = message
        self.details = details or {}
        self.code = code or status


class BasicValidator:
    """Lightweight structural validation for ingested payloads."""

    @staticmethod
    def _apply_rule(rule: RuleResult) -> ValidationResult:
        if not rule.passed:
            return ValidationResult("FAILED", rule.message)
        return ValidationResult("PASSED", "OK")

    @staticmethod
    def validate(content: bytes, detected_format: str) -> ValidationResult:
        base_rules = [
            ValidationRules.check_not_empty(content),
            ValidationRules.check_size(content, settings.max_payload_size_bytes),
        ]
        for rule in base_rules:
            if not rule.passed:
                result = BasicValidator._apply_rule(rule)
                result.code = "SIZE_OR_EMPTY"
                return result

        if detected_format == "JSON":
            try:
                details = JsonRules.validate(content)
                return ValidationResult("PASSED", "OK", details=details, code="JSON_OK")
            except ValidationError as exc:
                return ValidationResult("FAILED", str(exc), code="JSON_INVALID")
        if detected_format == "CSV":
            try:
                details = CsvRules.validate(content)
                return ValidationResult("PASSED", "OK", details=details, code="CSV_OK")
            except ValidationError as exc:
                return ValidationResult("FAILED", str(exc), code="CSV_INVALID")
        try:
            details = TextRules.validate(content)
            return ValidationResult("PASSED", "OK", details=details, code="TEXT_OK")
        except ValidationError as exc:
            return ValidationResult("FAILED", str(exc), code="TEXT_INVALID")
