"""Exception classes package.

This package contains all exception classes used throughout Graphite CLI.
All exceptions inherit from GraphiteException for consistent error handling.
"""

from graphite_cli.exceptions.base import (
    AuthenticationException,
    ConflictException,
    GitException,
    GitHubException,
    GraphiteException,
    ValidationException,
)

__all__ = [
    "AuthenticationException",
    "ConflictException",
    "GitException",
    "GitHubException",
    "GraphiteException",
    "ValidationException",
]
