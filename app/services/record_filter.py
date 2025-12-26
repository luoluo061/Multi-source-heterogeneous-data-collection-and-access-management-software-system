from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from sqlalchemy import and_
from sqlalchemy.orm import Query

from app.models.entities import RawRecord


@dataclass
class RecordFilter:
    run_id: Optional[str] = None
    source_id: Optional[int] = None
    fmt: Optional[str] = None
    validation_status: Optional[str] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None

    def apply(self, query: Query) -> Query:
        clauses: List = []
        if self.run_id:
            clauses.append(RawRecord.run_id == self.run_id)
        if self.source_id is not None:
            clauses.append(RawRecord.source_id == self.source_id)
        if self.fmt:
            clauses.append(RawRecord.format == self.fmt)
        if self.validation_status:
            clauses.append(RawRecord.validation_status == self.validation_status)
        if self.start:
            clauses.append(RawRecord.ingest_time >= self.start)
        if self.end:
            clauses.append(RawRecord.ingest_time <= self.end)
        if clauses:
            query = query.filter(and_(*clauses))
        return query
