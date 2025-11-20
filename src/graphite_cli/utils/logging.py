"""Logging configuration and utilities for Graphite CLI.

This module provides structured logging with multiple handlers, log levels,
and automatic redaction of sensitive information.

Features:
- Automatic sensitive data redaction
- Rich console formatting support
- File logging with directory creation
- Configurable log levels and handlers
"""

import logging
import re
import sys
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.logging import RichHandler

# Log level constants
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

# Sensitive field patterns to redact in logs
SENSITIVE_FIELDS = {"token", "password", "secret", "key", "authorization"}


class SensitiveDataFilter(logging.Filter):
    """Filter to redact sensitive information from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Redact sensitive data from log messages.

        Args:
            record: The log record to filter.

        Returns:
            Always True (allows all records through after redaction).
        """
        if hasattr(record, "msg") and isinstance(record.msg, str):
            # Identify and redact sensitive data patterns
            msg_lower = record.msg.lower()
            for field in SENSITIVE_FIELDS:
                if field in msg_lower:
                    # Pattern: finds "field: value" and redacts value
                    pattern = rf"\b{field}\b\s*[:\s]\s*([^\s,;)]+)"
                    record.msg = re.sub(
                        pattern,
                        f"{field}: [REDACTED]",
                        record.msg,
                        flags=re.IGNORECASE,
                    )
        return True


def setup_logging(
    level: int = INFO,
    log_file: Path | None = None,
    enable_rich: bool = True,
    propagate: bool = False,
) -> logging.Logger:
    """Configure structured logging for Graphite CLI.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Optional path to log file. If provided, logs will be written to file.
        enable_rich: If True, use Rich console handler for colored terminal output.
        propagate: If True, allow logs to propagate to parent loggers (useful for testing).

    Returns:
        Configured logger instance for the graphite_cli package.

    Example:
        >>> logger = setup_logging(level=DEBUG, log_file=Path("~/.graphite/logs/debug.log"))
        >>> logger.info("Starting Graphite CLI")
    """
    # Get or create the root logger for graphite_cli
    logger = logging.getLogger("graphite_cli")
    logger.setLevel(level)
    logger.propagate = propagate

    # Remove existing handlers to avoid duplicates
    # Close file handlers properly to prevent permission errors on Windows/macOS
    for handler in logger.handlers[:]:
        handler.close()
    logger.handlers.clear()

    # Add sensitive data filter
    sensitive_filter = SensitiveDataFilter()

    # Console handler with Rich formatting (if enabled)
    if enable_rich:
        console = Console(stderr=True)
        console_handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            markup=True,
            show_time=True,
            show_level=True,
            show_path=True,
        )
        console_handler.setLevel(level)
        console_handler.addFilter(sensitive_filter)
        logger.addHandler(console_handler)
    else:
        # Standard console handler for non-Rich environments
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(level)
        console_formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(sensitive_filter)
        logger.addHandler(console_handler)

    # File handler (if log_file is provided)
    if log_file:
        # Expand user path and create parent directories if needed
        log_file_path = Path(log_file).expanduser()
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file_path, encoding="utf-8", mode="a")
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        file_handler.addFilter(sensitive_filter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module.

    Args:
        name: The name of the module requesting the logger.

    Returns:
        Logger instance for the specified module.

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.debug("Debug message")
    """
    return logging.getLogger(f"graphite_cli.{name}")


def set_log_level(level: int) -> None:
    """Change the log level for all Graphite CLI loggers.

    Args:
        level: New logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Example:
        >>> set_log_level(DEBUG)  # Enable debug logging
        >>> set_log_level(WARNING)  # Show only warnings and errors
    """
    logger = logging.getLogger("graphite_cli")
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


def log_command_execution(
    command: str,
    args: dict[str, Any] | None = None,
) -> None:
    """Log the execution of a CLI command with structured data.

    Args:
        command: The name of the command being executed.
        args: Optional dictionary of command arguments (sensitive data will be redacted).

    Example:
        >>> log_command_execution("create", {"branch_name": "feature-x", "parent": "main"})
    """
    logger = get_logger("cli")

    # Redact sensitive arguments
    safe_args: dict[str, Any] = {}
    if args:
        for key, value in args.items():
            if any(sensitive in key.lower() for sensitive in SENSITIVE_FIELDS):
                safe_args[key] = "[REDACTED]"
            else:
                safe_args[key] = value

    # Include args in the message itself to avoid 'args' conflict with logging framework
    if safe_args:
        logger.info("Executing command: %s with arguments: %s", command, safe_args)
    else:
        logger.info("Executing command: %s", command)


def log_error(
    error: Exception,
    context: str | None = None,
) -> None:
    """Log an error with optional context information.

    Args:
        error: The exception that occurred.
        context: Optional context string describing where the error occurred.

    Example:
        >>> try:
        ...     risky_operation()
        ... except Exception as e:
        ...     log_error(e, "Failed during git rebase")
    """
    logger = get_logger("error")

    error_msg = f"{type(error).__name__}: {error}"
    if context:
        error_msg = f"{context} - {error_msg}"

    logger.error(error_msg, exc_info=True)
