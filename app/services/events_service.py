from typing import List

from sqlalchemy.orm import Session

from app.models.entities import RunEvent


class EventsService:
    """Query run events with pagination."""

    def __init__(self, db: Session):
        self.db = db

    def list(self, run_id: str, page: int = 1, page_size: int = 20) -> tuple[int, List[RunEvent]]:
        query = self.db.query(RunEvent).filter(RunEvent.run_id == run_id).order_by(RunEvent.ts.asc())
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return total, items
