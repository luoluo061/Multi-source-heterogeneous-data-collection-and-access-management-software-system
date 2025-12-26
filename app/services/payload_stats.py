from typing import Dict, List


class PayloadStats:
    """Calculates payload size statistics."""

    def summarize(self, records: List[dict]) -> Dict[str, int]:
        if not records:
            return {"min": 0, "max": 0, "avg": 0}
        sizes = [rec.get("raw_size", 0) for rec in records]
        total = sum(sizes)
        return {"min": min(sizes), "max": max(sizes), "avg": int(total / len(sizes))}
