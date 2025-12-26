import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.models.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class SourceConfig(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    enabled = Column(Boolean, default=True)
    params = Column(Text, nullable=False)
    schedule = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    def params_dict(self) -> Dict[str, Any]:
        try:
            return json.loads(self.params)
        except json.JSONDecodeError:
            return {}

    def schedule_dict(self) -> Optional[Dict[str, Any]]:
        if not self.schedule:
            return None
        try:
            return json.loads(self.schedule)
        except json.JSONDecodeError:
            return None


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    run_id = Column(String, primary_key=True, index=True)
    source_id = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="PENDING")
    message = Column(Text, nullable=True)
    error_code = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), default=_utcnow)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    records_count = Column(Integer, nullable=False, default=0)
    bytes_total = Column(Integer, nullable=False, default=0)
    duration_ms = Column(Integer, nullable=False, default=0)
    cancellation_requested = Column(Boolean, default=False)


class RawRecord(Base):
    __tablename__ = "raw_records"

    record_id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, nullable=False)
    source_id = Column(Integer, nullable=False)
    ingest_time = Column(DateTime(timezone=True), default=_utcnow)
    format = Column(String, nullable=False)
    raw_size = Column(Integer, nullable=False)
    payload = Column(Text, nullable=False)
    checksum = Column(String, nullable=False)
    validation_status = Column(String, nullable=False)
    validation_message = Column(Text, nullable=True)
    error_code = Column(String, nullable=True)
    validation_details = Column(Text, nullable=True)
    content_type = Column(String, nullable=True)
    source_uri = Column(String, nullable=True)
    status_code = Column(Integer, nullable=True)
    row_count = Column(Integer, nullable=True)
    columns = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True)
    payload_path = Column(Text, nullable=True)


class RunEvent(Base):
    __tablename__ = "run_events"

    event_id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, nullable=False, index=True)
    ts = Column(DateTime(timezone=True), default=_utcnow)
    stage = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    error_code = Column(String, nullable=True)
