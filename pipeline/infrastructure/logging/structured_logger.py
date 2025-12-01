"""
Structured Logging Infrastructure

Provides structured logging with context binding for the OMNI V4 pipeline.
Uses Python's standard logging module with JSON-like structured output.

Features:
- Context binding (restaurant_code, date set once)
- Structured key-value pairs
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Human-readable output for development
- JSON output for production (future)

Usage:
    from pipeline.infrastructure.logging.structured_logger import get_logger

    logger = get_logger(__name__)
    logger = logger.bind(restaurant="SDR", date="2025-10-20")

    logger.info("ingestion_complete",
                sales=5234.50,
                employees=17,
                duration_ms=234)

Output:
    [INFO] [SDR] [2025-10-20] ingestion_complete sales=5234.50 employees=17 duration_ms=234
"""

import logging
import sys
from typing import Dict, Any, Optional
from datetime import datetime


class StructuredLogger:
    """
    Structured logger with context binding.

    Wraps Python's standard logging.Logger with structured logging capabilities.
    Supports binding context (restaurant, date) that persists across log calls.
    """

    def __init__(self, name: str, base_logger: Optional[logging.Logger] = None):
        """
        Initialize structured logger.

        Args:
            name: Logger name (typically __name__)
            base_logger: Optional base logger (for testing)
        """
        self.name = name
        self._logger = base_logger or logging.getLogger(name)
        self._context: Dict[str, Any] = {}

    def bind(self, **kwargs) -> "StructuredLogger":
        """
        Bind context to logger (immutable - returns new logger).

        Args:
            **kwargs: Context key-value pairs

        Returns:
            New StructuredLogger with bound context
        """
        new_logger = StructuredLogger(self.name, self._logger)
        new_logger._context = {**self._context, **kwargs}
        return new_logger

    def _format_message(self, event: str, **kwargs) -> str:
        """
        Format structured log message.

        Args:
            event: Event name
            **kwargs: Additional key-value pairs

        Returns:
            Formatted message string
        """
        # Combine context and kwargs
        all_data = {**self._context, **kwargs}

        # Build context prefix
        context_parts = []
        if "restaurant" in all_data:
            context_parts.append(f"[{all_data['restaurant']}]")
        if "date" in all_data:
            context_parts.append(f"[{all_data['date']}]")

        context_prefix = " ".join(context_parts)
        if context_prefix:
            context_prefix += " "

        # Build key-value pairs (excluding restaurant/date as they're in prefix)
        kv_parts = []
        for key, value in all_data.items():
            if key not in ("restaurant", "date"):
                kv_parts.append(f"{key}={value}")

        kv_string = " ".join(kv_parts)
        if kv_string:
            kv_string = " " + kv_string

        return f"{context_prefix}{event}{kv_string}"

    def debug(self, event: str, **kwargs):
        """Log debug message."""
        self._logger.debug(self._format_message(event, **kwargs))

    def info(self, event: str, **kwargs):
        """Log info message."""
        self._logger.info(self._format_message(event, **kwargs))

    def warning(self, event: str, **kwargs):
        """Log warning message."""
        self._logger.warning(self._format_message(event, **kwargs))

    def error(self, event: str, **kwargs):
        """Log error message."""
        self._logger.error(self._format_message(event, **kwargs))

    def exception(self, event: str, **kwargs):
        """Log exception with traceback."""
        self._logger.exception(self._format_message(event, **kwargs))


def setup_logging(level: str = "INFO", format_type: str = "simple") -> None:
    """
    Configure root logger for OMNI V4.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        format_type: Format type (simple or detailed)
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Configure format
    if format_type == "simple":
        log_format = "[%(levelname)s] %(message)s"
    else:
        log_format = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True  # Override any existing configuration
    )


def get_logger(name: str) -> StructuredLogger:
    """
    Get structured logger for module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name)


# Initialize logging on module import (can be reconfigured later)
setup_logging()
