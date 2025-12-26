from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class SourceBase(BaseModel):
    name: str
    type: str
    enabled: bool = True
    params: Dict[str, Any]
    schedule: Optional[Dict[str, Any]] = None


class SourceCreate(SourceBase):
    """Payload for creating a source."""


class SourceUpdate(BaseModel):
    """Payload for updating a source."""

    name: Optional[str] = None
    type: Optional[str] = None
    enabled: Optional[bool] = None
    params: Optional[Dict[str, Any]] = None
    schedule: Optional[Dict[str, Any]] = None


class SourceRead(SourceBase):
    """Source representation returned to API clients."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
