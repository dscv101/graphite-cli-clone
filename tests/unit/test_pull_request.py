"""Unit tests for PullRequest model."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from graphite_cli.models.pull_request import PullRequest


def test_pull_request_basic_creation() -> None:
    """Test PullRequest creation with all required fields."""
    pr = PullRequest(
        number=123,
        title="Add new feature",
        body="This PR adds a new feature",
        url="https://github.com/org/repo/pull/123",
        state="open",
        head_branch="feature-branch",
        base_branch="main",
        created_at=datetime(2024, 1, 15, 10, 30, 0),
        updated_at=datetime(2024, 1, 15, 14, 20, 0),
    )
    assert pr.number == 123
    assert pr.title == "Add new feature"
    assert pr.body == "This PR adds a new feature"
    assert pr.url == "https://github.com/org/repo/pull/123"
    assert pr.state == "open"
    assert pr.head_branch == "feature-branch"
    assert pr.base_branch == "main"
    assert pr.created_at == datetime(2024, 1, 15, 10, 30, 0)
    assert pr.updated_at == datetime(2024, 1, 15, 14, 20, 0)
    assert pr.merged_at is None
    assert pr.mergeable is False
    assert pr.checks_passing is False
    assert pr.approved is False


def test_pull_request_with_merged_at() -> None:
    """Test PullRequest with merged_at timestamp."""
    pr = PullRequest(
        number=123,
        title="Add new feature",
        body="This PR adds a new feature",
        url="https://github.com/org/repo/pull/123",
        state="merged",
        head_branch="feature-branch",
        base_branch="main",
        created_at=datetime(2024, 1, 15, 10, 30, 0),
        updated_at=datetime(2024, 1, 15, 14, 20, 0),
        merged_at=datetime(2024, 1, 15, 14, 20, 0),
    )
    assert pr.merged_at == datetime(2024, 1, 15, 14, 20, 0)


def test_pull_request_with_all_flags_true() -> None:
    """Test PullRequest with all boolean flags set to True."""
    pr = PullRequest(
        number=123,
        title="Add new feature",
        body="This PR adds a new feature",
        url="https://github.com/org/repo/pull/123",
        state="open",
        head_branch="feature-branch",
        base_branch="main",
        created_at=datetime(2024, 1, 15, 10, 30, 0),
        updated_at=datetime(2024, 1, 15, 14, 20, 0),
        mergeable=True,
        checks_passing=True,
        approved=True,
    )
    assert pr.mergeable is True
    assert pr.checks_passing is True
    assert pr.approved is True


def test_is_mergeable_all_conditions_met() -> None:
    """Test is_mergeable returns True when all conditions are met."""
    pr = PullRequest(
        number=123,
        title="Add new feature",
        body="This PR adds a new feature",
        url="https://github.com/org/repo/pull/123",
        state="open",
        head_branch="feature-branch",
        base_branch="main",
        created_at=datetime(2024, 1, 15, 10, 30, 0),
        updated_at=datetime(2024, 1, 15, 14, 20, 0),
        mergeable=True,
        checks_passing=True,
        approved=True,
    )
    assert pr.is_mergeable() is True


def test_is_mergeable_state_closed() -> None:
    """Test is_mergeable returns False when PR is closed."""
    pr = PullRequest(
        number=123,
        title="Add new feature",
        body="This PR adds a new feature",
        url="https://github.com/org/repo/pull/123",
        state="closed",
        head_branch="feature-branch",
        base_branch="main",
        created_at=datetime(2024, 1, 15, 10, 30, 0),
        updated_at=datetime(2024, 1, 15, 14, 20, 0),
        mergeable=True,
        checks_passing=True,
        approved=True,
    )
    assert pr.is_mergeable() is False


def test_is_mergeable_state_merged() -> None:
    """Test is_mergeable returns False when PR is already merged."""
    pr = PullRequest(
        number=123,
        title="Add new feature",
        body="This PR adds a new feature",
        url="https://github.com/org/repo/pull/123",
        state="merged",
        head_branch="feature-branch",
        base_branch="main",
        created_at=datetime(2024, 1, 15, 10, 30, 0),
        updated_at=datetime(2024, 1, 15, 14, 20, 0),
        merged_at=datetime(2024, 1, 15, 14, 20, 0),
        mergeable=True,
        checks_passing=True,
        approved=True,
    )
    assert pr.is_mergeable() is False


def test_is_mergeable_not_mergeable() -> None:
    """Test is_mergeable returns False when mergeable flag is False."""
    pr = PullRequest(
        number=123,
        title="Add new feature",
        body="This PR adds a new feature",
        url="https://github.com/org/repo/pull/123",
        state="open",
        head_branch="feature-branch",
        base_branch="main",
        created_at=datetime(2024, 1, 15, 10, 30, 0),
        updated_at=datetime(2024, 1, 15, 14, 20, 0),
        mergeable=False,
        checks_passing=True,
        approved=True,
    )
    assert pr.is_mergeable() is False


def test_is_mergeable_checks_not_passing() -> None:
    """Test is_mergeable returns False when checks are not passing."""
    pr = PullRequest(
        number=123,
        title="Add new feature",
        body="This PR adds a new feature",
        url="https://github.com/org/repo/pull/123",
        state="open",
        head_branch="feature-branch",
        base_branch="main",
        created_at=datetime(2024, 1, 15, 10, 30, 0),
        updated_at=datetime(2024, 1, 15, 14, 20, 0),
        mergeable=True,
        checks_passing=False,
        approved=True,
    )
    assert pr.is_mergeable() is False


def test_is_mergeable_not_approved() -> None:
    """Test is_mergeable returns False when PR is not approved."""
    pr = PullRequest(
        number=123,
        title="Add new feature",
        body="This PR adds a new feature",
        url="https://github.com/org/repo/pull/123",
        state="open",
        head_branch="feature-branch",
        base_branch="main",
        created_at=datetime(2024, 1, 15, 10, 30, 0),
        updated_at=datetime(2024, 1, 15, 14, 20, 0),
        mergeable=True,
        checks_passing=True,
        approved=False,
    )
    assert pr.is_mergeable() is False


def test_is_mergeable_no_flags_set() -> None:
    """Test is_mergeable returns False when no boolean flags are set."""
    pr = PullRequest(
        number=123,
        title="Add new feature",
        body="This PR adds a new feature",
        url="https://github.com/org/repo/pull/123",
        state="open",
        head_branch="feature-branch",
        base_branch="main",
        created_at=datetime(2024, 1, 15, 10, 30, 0),
        updated_at=datetime(2024, 1, 15, 14, 20, 0),
    )
    assert pr.is_mergeable() is False


def test_pull_request_missing_required_fields() -> None:
    """Test PullRequest validation fails when required fields are missing."""
    with pytest.raises(ValidationError):
        PullRequest(
            number=123,
            title="Add new feature",
            # Missing required fields
        )


def test_pull_request_invalid_number_type() -> None:
    """Test PullRequest validation fails with invalid number type."""
    with pytest.raises(ValidationError):
        PullRequest(
            number="not-a-number",  # Should be int
            title="Add new feature",
            body="This PR adds a new feature",
            url="https://github.com/org/repo/pull/123",
            state="open",
            head_branch="feature-branch",
            base_branch="main",
            created_at=datetime(2024, 1, 15, 10, 30, 0),
            updated_at=datetime(2024, 1, 15, 14, 20, 0),
        )


def test_pull_request_serialization() -> None:
    """Test PullRequest can be serialized to dict."""
    pr = PullRequest(
        number=123,
        title="Add new feature",
        body="This PR adds a new feature",
        url="https://github.com/org/repo/pull/123",
        state="open",
        head_branch="feature-branch",
        base_branch="main",
        created_at=datetime(2024, 1, 15, 10, 30, 0),
        updated_at=datetime(2024, 1, 15, 14, 20, 0),
    )
    pr_dict = pr.model_dump()
    assert pr_dict["number"] == 123
    assert pr_dict["title"] == "Add new feature"
    assert pr_dict["state"] == "open"
    assert pr_dict["merged_at"] is None


def test_pull_request_deserialization() -> None:
    """Test PullRequest can be created from dict."""
    pr_data = {
        "number": 123,
        "title": "Add new feature",
        "body": "This PR adds a new feature",
        "url": "https://github.com/org/repo/pull/123",
        "state": "open",
        "head_branch": "feature-branch",
        "base_branch": "main",
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T14:20:00",
        "merged_at": None,
        "mergeable": False,
        "checks_passing": False,
        "approved": False,
    }
    pr = PullRequest(**pr_data)
    assert pr.number == 123
    assert pr.title == "Add new feature"
    assert pr.state == "open"
