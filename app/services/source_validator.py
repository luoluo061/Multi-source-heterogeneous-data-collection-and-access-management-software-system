from pathlib import Path
from typing import Dict

from app.core.errors import AdapterConfigurationError
from app.services.schedule_parser import ScheduleParser


class SourceValidator:
    """Validates source parameter completeness before a run starts."""

    @staticmethod
    def validate(source_type: str, params: Dict) -> None:
        if source_type == "HTTP_API":
            SourceValidator._validate_http(params)
        elif source_type == "FILE":
            SourceValidator._validate_file(params)
        elif source_type == "SQLITE":
            SourceValidator._validate_sqlite(params)
        else:
            raise AdapterConfigurationError(f"Unsupported source type: {source_type}")
        SourceValidator._validate_schedule(params.get("schedule"))

    @staticmethod
    def _validate_http(params: Dict) -> None:
        if not params.get("url"):
            raise AdapterConfigurationError("HTTP source requires url")
        method = (params.get("method") or "GET").upper()
        if method not in {"GET", "POST"}:
            raise AdapterConfigurationError("HTTP source only supports GET/POST")

    @staticmethod
    def _validate_file(params: Dict) -> None:
        directory = params.get("directory")
        if not directory:
            raise AdapterConfigurationError("File source requires directory")
        path = Path(directory)
        if not path.exists():
            raise AdapterConfigurationError(f"Directory does not exist: {directory}")

    @staticmethod
    def _validate_sqlite(params: Dict) -> None:
        db_path = params.get("db_path")
        if not db_path:
            raise AdapterConfigurationError("SQLite source requires db_path")
        mode = params.get("mode", "table")
        if mode not in {"table", "query"}:
            raise AdapterConfigurationError("SQLite mode must be table or query")

    @staticmethod
    def _validate_schedule(schedule):
        if schedule is None:
            return
        interval = ScheduleParser.interval_seconds(schedule)
        if interval <= 0:
            raise AdapterConfigurationError("Schedule interval_seconds must be positive")
