"""Unit tests for exception classes."""

import pytest

from graphite_cli.exceptions import (
    AuthenticationException,
    ConflictException,
    GitException,
    GitHubException,
    GraphiteException,
    ValidationException,
)


def test_graphite_exception_basic() -> None:
    """Test GraphiteException with message only."""
    exc = GraphiteException("Test error")
    assert exc.message == "Test error"
    assert exc.hint is None
    assert str(exc) == "Test error"


def test_graphite_exception_with_hint() -> None:
    """Test GraphiteException with message and hint."""
    exc = GraphiteException("Test error", "Try this fix")
    assert exc.message == "Test error"
    assert exc.hint == "Try this fix"
    assert "Test error" in str(exc)
    assert "Hint: Try this fix" in str(exc)


def test_git_exception_inherits_from_graphite() -> None:
    """Test GitException inherits from GraphiteException."""
    exc = GitException("Git operation failed")
    assert isinstance(exc, GraphiteException)
    assert isinstance(exc, GitException)


def test_github_exception_inherits_from_graphite() -> None:
    """Test GitHubException inherits from GraphiteException."""
    exc = GitHubException("GitHub API failed")
    assert isinstance(exc, GraphiteException)
    assert isinstance(exc, GitHubException)


def test_validation_exception_inherits_from_graphite() -> None:
    """Test ValidationException inherits from GraphiteException."""
    exc = ValidationException("Validation failed")
    assert isinstance(exc, GraphiteException)
    assert isinstance(exc, ValidationException)


def test_conflict_exception() -> None:
    """Test ConflictException with branch and files."""
    exc = ConflictException("feature-branch", ["file1.py", "file2.py"])
    assert exc.branch == "feature-branch"
    assert exc.conflicting_files == ["file1.py", "file2.py"]
    assert "feature-branch" in exc.message
    assert "file1.py" in exc.hint
    assert "file2.py" in exc.hint
    assert "gt continue" in exc.hint
    assert isinstance(exc, GitException)
    assert isinstance(exc, GraphiteException)


def test_authentication_exception() -> None:
    """Test AuthenticationException with default message."""
    exc = AuthenticationException()
    assert "authentication failed" in exc.message.lower()
    assert "gt auth" in exc.hint
    assert "GITHUB_TOKEN" in exc.hint
    assert isinstance(exc, GitHubException)
    assert isinstance(exc, GraphiteException)


def test_exceptions_are_raisable() -> None:
    """Test all exceptions can be raised and caught."""
    msg = "Test"
    branch_name = "branch"
    with pytest.raises(GraphiteException):
        raise GraphiteException(msg)

    with pytest.raises(GitException):
        raise GitException(msg)

    with pytest.raises(GitHubException):
        raise GitHubException(msg)

    with pytest.raises(ValidationException):
        raise ValidationException(msg)

    with pytest.raises(ConflictException):
        raise ConflictException(branch_name, ["file.py"])

    with pytest.raises(AuthenticationException):
        raise AuthenticationException
