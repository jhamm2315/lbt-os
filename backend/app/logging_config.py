"""
Structured JSON logging for LBT OS.

Injects request_id into every log record via a context variable.
Set logging_config.request_id_var before the first log in a request.
"""
from __future__ import annotations

import json
import logging
import logging.config
from contextvars import ContextVar
from datetime import datetime, timezone

request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class _JSONFormatter(logging.Formatter):
    _SKIP = frozenset({
        "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
        "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
        "created", "msecs", "relativeCreated", "thread", "threadName",
        "processName", "process", "message", "taskName",
    })

    def format(self, record: logging.LogRecord) -> str:
        entry: dict = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": request_id_var.get(""),
        }
        if record.exc_info:
            entry["exc"] = self.formatException(record.exc_info)
        for k, v in record.__dict__.items():
            if k not in self._SKIP and not k.startswith("_"):
                entry[k] = v
        return json.dumps(entry, default=str)


def configure_logging(level: str = "INFO") -> None:
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {"()": _JSONFormatter},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {"level": level, "handlers": ["console"]},
        "loggers": {
            "uvicorn":        {"level": "INFO",    "propagate": True},
            "uvicorn.access": {"level": "WARNING", "propagate": True},
            "stripe":         {"level": "WARNING", "propagate": True},
            "apscheduler":    {"level": "WARNING", "propagate": True},
            "httpx":          {"level": "WARNING", "propagate": True},
            "httpcore":       {"level": "WARNING", "propagate": True},
            "hpack":          {"level": "WARNING", "propagate": True},
        },
    })
