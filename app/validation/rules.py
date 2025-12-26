import csv
import io
import json
from dataclasses import dataclass
from typing import Optional


@dataclass
class RuleResult:
    passed: bool
    message: str = ""


class ValidationRules:
    """Reusable validation rules for different payload formats."""

    @staticmethod
    def check_not_empty(content: bytes) -> RuleResult:
        if not content:
            return RuleResult(False, "Content is empty")
        return RuleResult(True, "")

    @staticmethod
    def check_size(content: bytes, max_size: int) -> RuleResult:
        if len(content) > max_size:
            return RuleResult(False, "Content exceeds size limit")
        return RuleResult(True, "")

    @staticmethod
    def check_json(content: bytes) -> RuleResult:
        text = content.decode("utf-8", errors="replace")
        try:
            json.loads(text)
            return RuleResult(True, "")
        except Exception as exc:
            return RuleResult(False, f"JSON parse error: {exc}")

    @staticmethod
    def check_csv(content: bytes) -> RuleResult:
        text = content.decode("utf-8", errors="replace")
        try:
            reader = csv.reader(io.StringIO(text))
            rows = list(reader)
            if not rows:
                return RuleResult(False, "CSV has no rows")
            header = rows[0]
            if len(header) == 0:
                return RuleResult(False, "CSV header empty")
            return RuleResult(True, "")
        except Exception as exc:
            return RuleResult(False, f"CSV parse error: {exc}")

    @staticmethod
    def check_text(content: bytes) -> RuleResult:
        text = content.decode("utf-8", errors="replace")
        if not text.strip():
            return RuleResult(False, "Text content is empty")
        return RuleResult(True, "")
