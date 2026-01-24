"""
Structured logging configuration for Project Echo
Provides JSON-formatted logs with context enrichment
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict

from pythonjsonlogger import jsonlogger

from src.config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional context"""

    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """Add custom fields to log record"""
        super().add_fields(log_record, record, message_dict)

        # Add timestamp
        log_record["timestamp"] = datetime.utcnow().isoformat() + "Z"

        # Add service name
        log_record["service"] = "project-echo-api"

        # Add log level
        log_record["level"] = record.levelname

        # Add module and function
        log_record["module"] = record.module
        log_record["function"] = record.funcName
        log_record["line"] = record.lineno

        # Add request ID if available (from contextvars)
        # This will be set by middleware
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id

        # Add any additional context
        if hasattr(record, "context"):
            log_record["context"] = record.context


class TextFormatter(logging.Formatter):
    """Human-readable text formatter for development"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as readable text"""
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        level = record.levelname.ljust(8)
        module = f"{record.module}.{record.funcName}"
        message = record.getMessage()

        return f"{timestamp} | {level} | {module} | {message}"


def setup_logging() -> None:
    """Configure logging for the application"""

    # Get log level from settings
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Set formatter based on LOG_FORMAT setting
    if settings.LOG_FORMAT.lower() == "json":
        formatter = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(service)s %(module)s %(function)s %(message)s"
        )
    else:
        formatter = TextFormatter()

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Set levels for third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)

    # Create logger for this module
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured",
        extra={
            "context": {
                "log_level": settings.LOG_LEVEL,
                "log_format": settings.LOG_FORMAT,
                "environment": settings.APP_ENV,
            }
        },
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name"""
    return logging.getLogger(name)
