from app.core.error_codes import ErrorCode


class IngestionError(Exception):
    """Base exception for ingestion failures."""

    def __init__(self, message: str, error_code: str = ErrorCode.UNKNOWN):
        super().__init__(message)
        self.error_code = error_code


class SourceNotFoundError(IngestionError):
    """Raised when a source configuration cannot be located or is disabled."""


class SourceBusyError(IngestionError):
    """Raised when a source already has an active run and queuing is disabled."""


class AdapterConfigurationError(IngestionError):
    """Raised for adapter configuration issues."""


class AdapterError(IngestionError):
    """Raised for adapter runtime issues."""


class RetryableError(IngestionError):
    """Raised for retryable transient failures."""


class ValidationError(IngestionError):
    """Raised for payload validation issues."""


class StorageError(IngestionError):
    """Raised when persisting raw payloads fails."""
