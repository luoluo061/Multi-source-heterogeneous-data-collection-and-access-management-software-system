from typing import Dict, List

from app.core.logging import get_logger


class PayloadAudit:
    """Collects lightweight audit metrics over payloads."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def summarize(self, records: List[dict]) -> Dict[str, int]:
        total = 0
        for rec in records:
            total += rec.get("raw_size", 0)
        return {"records": len(records), "bytes": total}

    def log(self, run_id: str, source_id: int, records: List[dict]) -> None:
        summary = self.summarize(records)
        self.logger.info("payload_audit", extra={"run_id": run_id, "source_id": source_id, "payload": summary})
