"""Structured JSON logging helpers."""
import json
import logging
import sys
from typing import Any, Dict


class JsonFormatter(logging.Formatter):
    """Render log records as structured JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)

        extra = getattr(record, "extra_fields", None)
        if extra:
            log_record.update(extra)

        return json.dumps(log_record, default=str)


def configure_logging(level: int = logging.INFO) -> None:
    """Configure the root logger with JSON output to stdout."""
    root = logging.getLogger()

    if getattr(configure_logging, "_configured", False):
        root.setLevel(level)
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root.setLevel(level)
    root.handlers = [handler]
    configure_logging._configured = True  # type: ignore[attr-defined]


__all__ = ["configure_logging"]
