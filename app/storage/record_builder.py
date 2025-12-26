import hashlib
from typing import Dict, List

from app.validation.payload import PayloadValidator
from app.validation.schema_hint import SchemaHint
from app.validation.content_stats import ContentInspector


class RecordBuilder:
    """Builds normalized record dictionaries ready for persistence."""

    def __init__(self, run_id: str, source_id: int):
        self.run_id = run_id
        self.source_id = source_id

    def build(self, payload_entry: Dict, fmt: str, raw_size: int, validation) -> Dict:
        checksum = hashlib.sha256(payload_entry["body"]).hexdigest()
        schema_hint = SchemaHint.infer(payload_entry["body"], fmt)
        stats = ContentInspector.analyze(payload_entry["body"])
        record = {
            "run_id": self.run_id,
            "source_id": self.source_id,
            "payload": payload_entry["body"],
            "format": fmt,
            "raw_size": raw_size,
            "validation_status": validation.status,
            "validation_message": validation.message,
            "validation_code": getattr(validation, "code", None),
            "validation_details": json.dumps(validation.details),
            "content_type": payload_entry.get("content_type"),
            "source_uri": payload_entry.get("url"),
            "status_code": payload_entry.get("status_code"),
            "row_count": payload_entry.get("row_count"),
            "columns": ",".join(payload_entry.get("columns", [])) if payload_entry.get("columns") else None,
            "checksum": checksum,
            "schema_hint": schema_hint,
            "metadata_json": stats.to_json(),
        }
        PayloadValidator.ensure_complete(record)
        return record

    def build_many(self, payloads: List[Dict], fmt_detector, validator) -> List[Dict]:
        built = []
        for payload_entry in payloads:
            detection = fmt_detector.detect(payload_entry["body"])
            validation = validator.validate(payload_entry["body"], detection["format"])
            record = self.build(payload_entry, detection["format"], detection["raw_size"], validation)
            # include checksum for downstream dedupe and file storage
            record["checksum"] = hashlib.sha256(payload_entry["body"]).hexdigest()
            built.append(record)
        return built
