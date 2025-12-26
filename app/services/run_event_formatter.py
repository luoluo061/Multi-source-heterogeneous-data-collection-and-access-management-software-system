from typing import Dict

from app.models.entities import RunEvent


class RunEventFormatter:
    """Formats run events into serializable dictionaries."""

    @staticmethod
    def to_dict(event: RunEvent) -> Dict:
        return {
            "event_id": event.event_id,
            "run_id": event.run_id,
            "ts": event.ts.isoformat(),
            "stage": event.stage,
            "event_type": event.event_type,
            "message": event.message,
            "error_code": event.error_code,
        }
