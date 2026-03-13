"""
Custom logging formatters that inject request context into every log record.

Both formatters pull request_id and user_id from contextvars (set by
RequestTracingMiddleware) so every log line is automatically traceable
to the request that produced it.

Usage — in config.py LOGGING dict:

    'formatters': {
        'verbose': {
            '()': 'app.core.logging.RequestContextFormatter',
            'format': '[{levelname}] {asctime} [{request_id}] [{user_id}] {name} {message}',
            'style': '{',
        },
        'json': {
            '()': 'app.core.logging.RequestContextJSONFormatter',
        },
    }
"""

import json
import logging
from datetime import datetime, timezone

from app.middleware.logging_context import context_request_id, context_user_id

# Fields that belong to the LogRecord internals and should not be forwarded
# to JSON output as extra keys.
_SKIP_RECORD_FIELDS = frozenset({
    "msg", "args", "created", "exc_info", "exc_text", "levelname", "levelno",
    "pathname", "filename", "module", "lineno", "funcName", "processName",
    "process", "threadName", "thread", "name", "msecs", "relativeCreated",
    "stack_info", "taskName",
})


class RequestContextFormatter(logging.Formatter):
    """
    Text formatter that adds request_id and user_id placeholders to the format string.

    Use {request_id} and {user_id} in your format string — they are injected
    from contextvars before the base Formatter renders the record.
    """

    def format(self, record: logging.LogRecord) -> str:
        record.request_id = context_request_id.get() or "-"
        record.user_id = context_user_id.get() or "-"
        return super().format(record)


class RequestContextJSONFormatter(logging.Formatter):
    """
    JSON formatter that includes request context fields.

    Produces one JSON object per log line — compatible with log aggregators
    such as Datadog, Papertrail, and Railway's built-in log viewer.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": context_request_id.get(),
            "user_id": context_user_id.get(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Forward any extra= keys passed to the logger call
        for key, value in record.__dict__.items():
            if key not in _SKIP_RECORD_FIELDS and not key.startswith("_"):
                log_data[key] = value

        return json.dumps(log_data, default=str)


def configure_logging(debug: bool = False) -> None:
    """
    Configure the root logging hierarchy for the application.

    Called once from app lifespan on startup.
    """
    formatter_class = "app.core.logging.RequestContextFormatter"
    log_format = "[{levelname}] {asctime} [{request_id}] [{user_id}] {name} — {message}"
    date_format = "%d/%b/%Y %H:%M:%S"

    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "()": formatter_class,
                "format": log_format,
                "style": "{",
                "datefmt": date_format,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "verbose",
                "level": "DEBUG",
            },
        },
        "loggers": {
            # Root — catches everything not matched below
            "": {
                "handlers": ["console"],
                "level": "DEBUG" if debug else "INFO",
                "propagate": False,
            },
            # Suppress noisy SQLAlchemy statement logs unless DEBUG
            "sqlalchemy.engine": {
                "handlers": ["console"],
                "level": "INFO" if debug else "WARNING",
                "propagate": False,
            },
            # App namespaces — always verbose
            "app": {
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": False,
            },
            "app.services.openai": {
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": False,
            },
            "app.middleware.request_tracing": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
        },
    })
