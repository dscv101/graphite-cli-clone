"""Utility functions package."""

from graphite_cli.utils.branch_name import (
    format_branch_description,
    generate_branch_name,
    parse_template,
    validate_branch_name,
    validate_template,
)
from graphite_cli.utils.logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    WARNING,
    get_logger,
    log_command_execution,
    log_error,
    set_log_level,
    setup_logging,
)

__all__ = [
    "CRITICAL",
    "DEBUG",
    "ERROR",
    "INFO",
    "WARNING",
    "format_branch_description",
    "generate_branch_name",
    "get_logger",
    "log_command_execution",
    "log_error",
    "parse_template",
    "set_log_level",
    "setup_logging",
    "validate_branch_name",
    "validate_template",
]
