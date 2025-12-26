from app.adapters.base import SourceAdapter
from app.adapters.file_adapter import FileSource
from app.adapters.http_api import HttpAPISource
from app.adapters.sqlite_adapter import SQLiteSource
from app.core.errors import AdapterConfigurationError


def get_adapter(source_type: str, params: dict) -> SourceAdapter:
    if source_type == "HTTP_API":
        return HttpAPISource(params)
    if source_type == "FILE":
        return FileSource(params)
    if source_type == "SQLITE":
        return SQLiteSource(params)
    raise AdapterConfigurationError(f"Unsupported source type: {source_type}")
