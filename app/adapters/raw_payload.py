from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RawPayload:
    body: bytes
    content_type: Optional[str] = None
    url: Optional[str] = None
    status_code: Optional[int] = None
    row_count: Optional[int] = None
    columns: Optional[List[str]] = None
    encoding: Optional[str] = None
    checksum: Optional[str] = None
