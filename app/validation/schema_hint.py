import csv
import io
import json
from typing import Dict, List, Optional


class SchemaHint:
    """Produces lightweight schema hints for JSON/CSV payloads."""

    @staticmethod
    def infer(payload: bytes, fmt: str) -> Optional[Dict]:
        if fmt == "JSON":
            return SchemaHint._infer_json(payload)
        if fmt == "CSV":
            return SchemaHint._infer_csv(payload)
        return None

    @staticmethod
    def _infer_json(payload: bytes) -> Optional[Dict]:
        try:
            data = json.loads(payload.decode("utf-8", errors="ignore"))
            if isinstance(data, list) and data and isinstance(data[0], dict):
                keys = sorted(set().union(*[item.keys() for item in data if isinstance(item, dict)]))
                return {"type": "object_list", "fields": keys}
            if isinstance(data, dict):
                return {"type": "object", "fields": sorted(data.keys())}
            return None
        except Exception:
            return None

    @staticmethod
    def _infer_csv(payload: bytes) -> Optional[Dict]:
        try:
            text = payload.decode("utf-8", errors="ignore")
            reader = csv.reader(io.StringIO(text))
            rows = list(reader)
            if not rows:
                return None
            header = rows[0]
            return {"type": "csv", "columns": header, "rows": len(rows) - 1}
        except Exception:
            return None
