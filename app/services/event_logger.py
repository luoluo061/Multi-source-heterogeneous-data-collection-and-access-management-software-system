from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.entities import RunEvent


class EventLogger:
    """Persists run events for audit trail."""

    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)

    def log(
        self,
        run_id: str,
        *,
        stage: str,
        event_type: str,
        message: str,
        error_code: Optional[str] = None,
    ) -> None:
        event = RunEvent(
            run_id=run_id,
            ts=datetime.now(timezone.utc),
            stage=stage,
            event_type=event_type,
            message=message,
            error_code=error_code,
        )
        self.db.add(event)
        self.db.commit()
        self.logger.info(
            "run_event",
            extra={"run_id": run_id, "source_id": "-", "payload": {"stage": stage, "type": event_type, "code": error_code}},
        )
