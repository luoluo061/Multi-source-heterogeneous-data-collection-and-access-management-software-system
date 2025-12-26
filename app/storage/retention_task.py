from sqlalchemy.orm import Session

from app.core.config import settings
from app.storage.retention import RetentionPolicy
from app.storage.retention_rules import RetentionRules


class RetentionTask:
    """Invoked by scheduler to enforce retention policy."""

    def __init__(self, db: Session):
        self.db = db

    def run(self):
        RetentionPolicy(self.db, days=settings.retention_days).enforce()
        RetentionRules(self.db).enforce_by_count()
