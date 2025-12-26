from typing import Dict, List


class RunLabeler:
    """Assigns human-readable labels to runs based on payload metadata."""

    def labels_for_payloads(self, records: List[dict]) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for rec in records:
            fmt = rec.get("format", "UNKNOWN")
            counts[fmt] = counts.get(fmt, 0) + 1
        return counts
