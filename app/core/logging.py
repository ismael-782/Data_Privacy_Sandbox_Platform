"""Logging utilities."""

import logging
from logging.config import dictConfig

from .config import settings


def setup_logging(level: int | str = logging.INFO) -> None:
    """Configure application-wide logging."""
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                }
            },
            "root": {"handlers": ["console"], "level": level},
        }
    )
    logging.getLogger(__name__).debug("Logging initialized (debug=%s)", settings.app.debug)

