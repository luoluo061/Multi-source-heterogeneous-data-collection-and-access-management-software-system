import csv
import io
import json
from typing import Dict, Optional


class FormatDetector:
    """Detects simple structural format for payload classification."""

    @staticmethod
    def detect(data: bytes) -> Dict[str, Optional[str]]:
        raw_size = len(data)
        text = data.decode("utf-8", errors="replace")
        if FormatDetector._is_json(text):
            return {"format": "JSON", "encoding": "utf-8", "schema_hint": None, "raw_size": raw_size}
        if FormatDetector._is_csv(text):
            return {"format": "CSV", "encoding": "utf-8", "schema_hint": None, "raw_size": raw_size}
        if text.strip():
            return {"format": "TEXT", "encoding": "utf-8", "schema_hint": None, "raw_size": raw_size}
        return {"format": "UNKNOWN", "encoding": None, "schema_hint": None, "raw_size": raw_size}

    @staticmethod
    def _is_json(text: str) -> bool:
        try:
            json.loads(text)
            return True
        except Exception:
            return False

    @staticmethod
    def _is_csv(text: str) -> bool:
        try:
            sample = io.StringIO(text)
            reader = csv.reader(sample)
            rows = list(reader)
            return len(rows) > 0 and len(rows[0]) > 1
        except Exception:
            return False
