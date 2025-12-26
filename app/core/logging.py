import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

from app.core.config import settings


LOG_FORMAT = "%(asctime)s [%(levelname)s] run_id=%(run_id)s source_id=%(source_id)s %(name)s: %(message)s"


def _build_handler() -> RotatingFileHandler:
    handler = RotatingFileHandler(settings.log_dir / "app.log", maxBytes=2_000_000, backupCount=3)
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    return handler


def configure_logging() -> None:
    logger = logging.getLogger()
    if logger.handlers:
        return
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)
    logger.addHandler(_build_handler())


class ContextLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that injects run_id/source_id for traceability."""

    def process(self, msg, kwargs):
        extra = kwargs.get("extra", {})
        context = self.extra.copy()
        context.update({"run_id": extra.get("run_id", "-"), "source_id": extra.get("source_id", "-")})
        kwargs["extra"] = context
        return msg, kwargs


def get_logger(name: Optional[str] = None, run_id: str = "-", source_id: str = "-") -> logging.Logger:
    configure_logging()
    base_logger = logging.getLogger(name)
    adapter = ContextLoggerAdapter(base_logger, {"run_id": run_id, "source_id": source_id})
    return adapter
