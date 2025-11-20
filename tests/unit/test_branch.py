"""Unit tests for Branch model."""

from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from graphite_cli.models.branch import Branch


class TestBranch:
    """Test cases for Branch model."""

    def test_branch_creation_minimal(self) -> None:
        """Test creating a branch with minimal required fields."""
        branch = Branch(
            name="feature-1",
            commit_sha="abc123def456",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        assert branch.name == "feature-1"
        assert branch.commit_sha == "abc123def456"
        assert branch.parent_branch is None
        assert branch.pr_number is None
        assert branch.pr_url is None
        assert branch.is_tracked is True
        assert branch.custom_metadata == {}

    def test_branch_creation_full(self) -> None:
        """Test creating a branch with all fields."""
        created = datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)
        updated = datetime(2024, 1, 16, 14, 20, 0, tzinfo=UTC)

        branch = Branch(
            name="feature-2",
            commit_sha="def456ghi789",
            parent_branch="main",
            pr_number=123,
            pr_url="https://github.com/org/repo/pull/123",
            created_at=created,
            updated_at=updated,
            is_tracked=True,
            custom_metadata={"priority": "high", "team": "backend"},
        )

        assert branch.name == "feature-2"
        assert branch.commit_sha == "def456ghi789"
        assert branch.parent_branch == "main"
        assert branch.pr_number == 123
        assert branch.pr_url == "https://github.com/org/repo/pull/123"
        assert branch.created_at == created
        assert branch.updated_at == updated
        assert branch.is_tracked is True
        assert branch.custom_metadata == {"priority": "high", "team": "backend"}

    def test_is_submitted_with_pr_number(self) -> None:
        """Test is_submitted returns True when PR number exists."""
        branch = Branch(
            name="feature-pr",
            commit_sha="xyz789",
            pr_number=456,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        assert branch.is_submitted() is True

    def test_is_submitted_without_pr_number(self) -> None:
        """Test is_submitted returns False when PR number is None."""
        branch = Branch(
            name="feature-no-pr",
            commit_sha="xyz789",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        assert branch.is_submitted() is False

    def test_get_children_single_child(self) -> None:
        """Test get_children returns single child branch."""

        parent_branch = Branch(
            name="parent",
            commit_sha="abc123",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        child_branch = Branch(
            name="child",
            commit_sha="def456",
            parent_branch="parent",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        # Mock stack
        mock_stack = Mock()
        mock_stack.branches = [parent_branch, child_branch]

        children = parent_branch.get_children(mock_stack)

        assert len(children) == 1
        assert children[0].name == "child"

    def test_get_children_multiple_children(self) -> None:
        """Test get_children returns multiple child branches."""

        parent_branch = Branch(
            name="parent",
            commit_sha="abc123",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        child1 = Branch(
            name="child1",
            commit_sha="def456",
            parent_branch="parent",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        child2 = Branch(
            name="child2",
            commit_sha="ghi789",
            parent_branch="parent",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        unrelated_branch = Branch(
            name="unrelated",
            commit_sha="jkl012",
            parent_branch="other-parent",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        # Mock stack
        mock_stack = Mock()
        mock_stack.branches = [parent_branch, child1, child2, unrelated_branch]

        children = parent_branch.get_children(mock_stack)

        assert len(children) == 2
        child_names = {child.name for child in children}
        assert child_names == {"child1", "child2"}

    def test_get_children_no_children(self) -> None:
        """Test get_children returns empty list when no children exist."""

        branch = Branch(
            name="leaf",
            commit_sha="abc123",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        # Mock stack with no children
        mock_stack = Mock()
        mock_stack.branches = [branch]

        children = branch.get_children(mock_stack)

        assert len(children) == 0

    def test_get_ancestors_simple_chain(self) -> None:
        """Test get_ancestors returns all ancestors in order."""

        main_branch = Branch(
            name="main",
            commit_sha="abc123",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        feature1 = Branch(
            name="feature-1",
            commit_sha="def456",
            parent_branch="main",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        feature2 = Branch(
            name="feature-2",
            commit_sha="ghi789",
            parent_branch="feature-1",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        # Mock stack
        mock_stack = Mock()

        def mock_get_branch(name: str):
            branches_map = {
                "main": main_branch,
                "feature-1": feature1,
                "feature-2": feature2,
            }
            return branches_map.get(name)

        mock_stack.get_branch = mock_get_branch

        ancestors = feature2.get_ancestors(mock_stack)

        assert len(ancestors) == 2
        assert ancestors[0].name == "feature-1"
        assert ancestors[1].name == "main"

    def test_get_ancestors_no_parent(self) -> None:
        """Test get_ancestors returns empty list for trunk branch."""

        branch = Branch(
            name="main",
            commit_sha="abc123",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        mock_stack = Mock()
        ancestors = branch.get_ancestors(mock_stack)

        assert len(ancestors) == 0

    def test_get_ancestors_missing_parent(self) -> None:
        """Test get_ancestors handles missing parent gracefully."""

        branch = Branch(
            name="orphan",
            commit_sha="abc123",
            parent_branch="missing-parent",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        # Mock stack that returns None for missing branch
        mock_stack = Mock()
        mock_stack.get_branch = Mock(return_value=None)

        ancestors = branch.get_ancestors(mock_stack)

        assert len(ancestors) == 0

    def test_branch_name_validation_empty(self) -> None:
        """Test branch name validation fails for empty string."""

        with pytest.raises(ValidationError) as exc_info:
            Branch(
                name="",
                commit_sha="abc123",
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )

        errors = exc_info.value.errors()
        assert any("name" in str(error) for error in errors)

    def test_branch_name_validation_starts_with_dash(self) -> None:
        """Test branch name validation fails for names starting with dash."""

        with pytest.raises(ValidationError) as exc_info:
            Branch(
                name="-invalid",
                commit_sha="abc123",
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )

        errors = exc_info.value.errors()
        assert any("name" in str(error) for error in errors)

    def test_commit_sha_validation_empty(self) -> None:
        """Test commit SHA validation fails for empty string."""

        with pytest.raises(ValidationError) as exc_info:
            Branch(
                name="feature",
                commit_sha="",
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )

        errors = exc_info.value.errors()
        assert any("commit_sha" in str(error) for error in errors)

    def test_branch_serialization(self) -> None:
        """Test branch can be serialized to dict."""
        created = datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)
        updated = datetime(2024, 1, 16, 14, 20, 0, tzinfo=UTC)

        branch = Branch(
            name="feature",
            commit_sha="abc123",
            parent_branch="main",
            pr_number=123,
            pr_url="https://github.com/org/repo/pull/123",
            created_at=created,
            updated_at=updated,
            is_tracked=True,
            custom_metadata={"key": "value"},
        )

        data = branch.model_dump()

        assert data["name"] == "feature"
        assert data["commit_sha"] == "abc123"
        assert data["parent_branch"] == "main"
        assert data["pr_number"] == 123
        assert data["pr_url"] == "https://github.com/org/repo/pull/123"
        assert data["is_tracked"] is True
        assert data["custom_metadata"] == {"key": "value"}

    def test_branch_json_serialization(self) -> None:
        """Test branch can be serialized to JSON."""
        created = datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)
        updated = datetime(2024, 1, 16, 14, 20, 0, tzinfo=UTC)

        branch = Branch(
            name="feature",
            commit_sha="abc123",
            created_at=created,
            updated_at=updated,
        )

        json_str = branch.model_dump_json()
        assert "feature" in json_str
        assert "abc123" in json_str
