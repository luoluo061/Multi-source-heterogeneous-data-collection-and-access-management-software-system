import json
import sqlite3
from typing import List, Optional

from app.adapters.base import SourceAdapter
from app.adapters.raw_payload import RawPayload
from app.core.error_codes import ErrorCode
from app.core.errors import AdapterConfigurationError, AdapterError
from app.adapters.sqlite_pager import SQLitePager


class SQLiteSource(SourceAdapter):
    """Reads rows from a SQLite table and serializes each row to JSON bytes."""

    def fetch(self) -> List[dict]:
        db_path = self.params.get("db_path")
        table = self.params.get("table")
        mode = self.params.get("mode", "table")
        query = self.params.get("query")
        columns = self.params.get("columns")
        where = self.params.get("where")
        limit = int(self.params.get("limit", 100))
        offset = int(self.params.get("offset", 0))
        if not db_path:
            raise AdapterConfigurationError("SQLite source requires 'db_path'")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        pager = SQLitePager(conn, limit=limit, offset=offset)
        try:
            payloads: List[dict] = []
            if mode == "table":
                query_text = pager.build_table_query(table, columns=columns, where=where)
            elif mode == "query":
                if not query:
                    raise AdapterConfigurationError("Query mode requires 'query'")
                query_text = pager.build_safe_query(query)
            else:
                raise AdapterConfigurationError("Unsupported SQLite mode")
            for page_rows in pager.execute_paginated(query_text):
                serialized = [dict(row) for row in page_rows]
                payloads.append(
                    RawPayload(
                        body=json.dumps(serialized).encode("utf-8"),
                        content_type="application/json",
                        url=f"sqlite://{db_path}",
                        status_code=200,
                        row_count=len(serialized),
                        columns=list(serialized[0].keys()) if serialized else [],
                    ).__dict__
                )
            return payloads
        except sqlite3.OperationalError as exc:
            raise AdapterError(f"SQLite operation failed: {exc}", ErrorCode.ADAPTER_RUNTIME) from exc
        finally:
            conn.close()
