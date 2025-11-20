"""Base exception classes for Graphite CLI.

This module defines the exception hierarchy used throughout the application.
All exceptions inherit from GraphiteException for consistent error handling.
"""


class GraphiteException(Exception):
    """Base exception for all Graphite errors.

    Attributes:
        message: The error message describing what went wrong.
        hint: Optional hint for how to resolve the error.
    """

    def __init__(self, message: str, hint: str | None = None) -> None:
        """Initialize GraphiteException.

        Args:
            message: The error message.
            hint: Optional hint for resolution.
        """
        self.message = message
        self.hint = hint
        super().__init__(message)

    def __str__(self) -> str:
        """Return string representation with hint if available."""
        if self.hint:
            return f"{self.message}\nHint: {self.hint}"
        return self.message


class GitException(GraphiteException):
    """Git operation failed.

    Raised when a Git command or operation fails, such as checkout,
    commit, rebase, or merge operations.
    """


class GitHubException(GraphiteException):
    """GitHub API operation failed.

    Raised when a GitHub API request fails, including authentication errors,
    rate limiting, or network issues.
    """


class ValidationException(GraphiteException):
    """Validation failed.

    Raised when input validation fails, such as invalid branch names,
    malformed configuration, or invalid stack operations.
    """


class ConflictException(GitException):
    """Git conflict detected.

    Raised when a Git operation results in merge conflicts that require
    manual resolution.

    Attributes:
        branch: The branch where the conflict occurred.
        conflicting_files: List of files with conflicts.
    """

    def __init__(self, branch: str, conflicting_files: list[str]) -> None:
        """Initialize ConflictException.

        Args:
            branch: The branch where the conflict occurred.
            conflicting_files: List of files with conflicts.
        """
        self.branch = branch
        self.conflicting_files = conflicting_files
        message = f"Conflict detected on branch '{branch}'"
        hint = (
            "Resolve conflicts in the following files:\n"
            + "\n".join(f"  - {f}" for f in conflicting_files)
            + "\n\nThen run: gt continue"
        )
        super().__init__(message, hint)


class AuthenticationException(GitHubException):
    """GitHub authentication failed.

    Raised when GitHub authentication fails or token is invalid/expired.
    """

    def __init__(self) -> None:
        """Initialize AuthenticationException."""
        message = "GitHub authentication failed"
        hint = (
            "Please authenticate with GitHub:\n"
            "  gt auth\n\n"
            "Or set a valid token:\n"
            "  export GITHUB_TOKEN=<your-token>"
        )
        super().__init__(message, hint)


__all__ = [
    "AuthenticationException",
    "ConflictException",
    "GitException",
    "GitHubException",
    "GraphiteException",
    "ValidationException",
]
