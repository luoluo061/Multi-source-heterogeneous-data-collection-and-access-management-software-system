import sqlite3
from typing import Iterable, List

from app.core.errors import AdapterConfigurationError


class SQLitePager:
    """Helper to read SQLite data in pages."""

    def __init__(self, conn: sqlite3.Connection, limit: int = 100, offset: int = 0):
        self.conn = conn
        self.limit = limit
        self.offset = offset

    def build_table_query(self, table: str, *, columns=None, where=None) -> str:
        if not table:
            raise AdapterConfigurationError("Table name is required")
        cols = ", ".join(columns) if columns else "*"
        where_clause = f" WHERE {where}" if where else ""
        return f"SELECT {cols} FROM {table}{where_clause}"

    def build_safe_query(self, query: str) -> str:
        trimmed = query.strip().lower()
        if trimmed.startswith("update") or trimmed.startswith("delete") or trimmed.startswith("insert"):
            raise AdapterConfigurationError("Only read-only queries are allowed")
        return query

    def execute_paginated(self, query: str) -> Iterable[List[sqlite3.Row]]:
        current_offset = self.offset
        while True:
            paged_query = f"{query} LIMIT {self.limit} OFFSET {current_offset}"
            cursor = self.conn.execute(paged_query)
            rows = cursor.fetchall()
            if not rows:
                break
            yield rows
            if len(rows) < self.limit:
                break
            current_offset += self.limit
