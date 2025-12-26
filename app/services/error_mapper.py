from app.core.error_codes import ErrorCode
from app.core.errors import AdapterError, StorageError, ValidationError


class ErrorMapper:
    """Maps exceptions to error codes."""

    @staticmethod
    def to_code(exc: Exception) -> str:
        if isinstance(exc, AdapterError):
            return exc.error_code or ErrorCode.ADAPTER_RUNTIME
        if isinstance(exc, StorageError):
            return exc.error_code or ErrorCode.STORAGE_FAILED
        if isinstance(exc, ValidationError):
            return exc.error_code or ErrorCode.VALIDATION_FAILED
        return ErrorCode.UNKNOWN
