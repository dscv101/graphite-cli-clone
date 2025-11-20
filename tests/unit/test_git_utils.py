"""Unit tests for git_utils module."""

from pathlib import Path
from unittest.mock import Mock, PropertyMock, patch

import pytest
from git import Commit, Repo
from git.exc import BadName, InvalidGitRepositoryError

from graphite_cli.exceptions import GitException, ValidationException
from graphite_cli.utils.git_utils import (
    find_merge_base,
    get_branch_upstream,
    get_commit_count_between,
    get_current_branch_name,
    get_repo_root,
    get_short_sha,
    is_branch_merged,
    is_detached_head,
    is_git_repo,
    is_repo_clean,
    is_valid_branch_name,
    parse_ref,
    ref_exists,
    resolve_ref,
    validate_branch_name,
)


class TestBranchNameValidation:
    """Tests for branch name validation functions."""

    def test_valid_branch_names(self):
        """Test that valid branch names pass validation."""
        valid_names = [
            "main",
            "feature",
            "feature/new-feature",
            "bugfix/fix-123",
            "release/v1.0.0",
            "hotfix_urgent",
            "dev",
        ]

        for name in valid_names:
            assert is_valid_branch_name(name), f"'{name}' should be valid"
            validate_branch_name(name)  # Should not raise

    def test_invalid_branch_names(self):
        """Test that invalid branch names fail validation."""
        invalid_names = [
            "",  # Empty
            "-feature",  # Starts with -
            ".feature",  # Starts with .
            "feature..bad",  # Contains ..
            "feature~bad",  # Contains ~
            "feature^bad",  # Contains ^
            "feature:bad",  # Contains :
            "feature*bad",  # Contains *
            "feature?bad",  # Contains ?
            "feature[bad",  # Contains [
            "feature bad",  # Contains space
            "feature/",  # Ends with /
            "feature.lock",  # Ends with .lock
            "feature@{bad",  # Contains @{
            "feature/.hidden",  # Contains /.
        ]

        for name in invalid_names:
            assert not is_valid_branch_name(name), f"'{name}' should be invalid"
            with pytest.raises(ValidationException):
                validate_branch_name(name)

    def test_validate_branch_name_error_message(self):
        """Test that validation error includes helpful hint."""
        with pytest.raises(ValidationException) as exc_info:
            validate_branch_name("bad..name")

        assert "Invalid branch name" in str(exc_info.value)
        assert "consecutive dots" in str(exc_info.value)


class TestRefParsing:
    """Tests for ref parsing functions."""

    def test_parse_ref_valid_commit(self):
        """Test parsing a valid ref returns commit."""
        mock_repo = Mock(spec=Repo)
        mock_commit = Mock(spec=Commit)
        mock_repo.commit.return_value = mock_commit

        result = parse_ref(mock_repo, "HEAD")

        assert result == mock_commit
        mock_repo.commit.assert_called_once_with("HEAD")

    def test_parse_ref_invalid_ref(self):
        """Test parsing an invalid ref returns None."""
        mock_repo = Mock(spec=Repo)
        mock_repo.commit.side_effect = BadName("invalid")

        result = parse_ref(mock_repo, "nonexistent")

        assert result is None

    def test_ref_exists_true(self):
        """Test ref_exists returns True for existing refs."""
        mock_repo = Mock(spec=Repo)
        mock_commit = Mock(spec=Commit)
        mock_repo.commit.return_value = mock_commit

        assert ref_exists(mock_repo, "main") is True

    def test_ref_exists_false(self):
        """Test ref_exists returns False for non-existing refs."""
        mock_repo = Mock(spec=Repo)
        mock_repo.commit.side_effect = BadName("invalid")

        assert ref_exists(mock_repo, "nonexistent") is False

    def test_resolve_ref_branch(self):
        """Test resolving a branch name to full ref."""
        mock_repo = Mock(spec=Repo)
        mock_repo.branches = {"main": Mock()}

        result = resolve_ref(mock_repo, "main")

        assert result == "refs/heads/main"

    def test_resolve_ref_tag(self):
        """Test resolving a tag name to full ref."""
        mock_repo = Mock(spec=Repo)
        mock_repo.branches = {}
        mock_repo.tags = {"v1.0.0": Mock()}

        result = resolve_ref(mock_repo, "v1.0.0")

        assert result == "refs/tags/v1.0.0"

    def test_resolve_ref_head(self):
        """Test resolving HEAD returns HEAD."""
        mock_repo = Mock(spec=Repo)
        mock_repo.branches = {}
        mock_repo.tags = {}

        result = resolve_ref(mock_repo, "HEAD")

        assert result == "HEAD"

    def test_resolve_ref_nonexistent(self):
        """Test resolving a nonexistent ref raises exception."""
        mock_repo = Mock(spec=Repo)
        mock_repo.branches = {}
        mock_repo.tags = {}
        mock_repo.commit.side_effect = BadName("invalid")

        with pytest.raises(GitException) as exc_info:
            resolve_ref(mock_repo, "nonexistent")

        assert "Could not resolve ref" in str(exc_info.value)


class TestBranchOperations:
    """Tests for branch operation utilities."""

    def test_get_branch_upstream_exists(self):
        """Test getting upstream branch when it exists."""
        mock_repo = Mock(spec=Repo)
        mock_branch = Mock()
        mock_tracking = Mock()
        mock_tracking.name = "origin/main"
        mock_branch.tracking_branch.return_value = mock_tracking
        mock_repo.branches = {"main": mock_branch}

        result = get_branch_upstream(mock_repo, "main")

        assert result == "origin/main"

    def test_get_branch_upstream_none(self):
        """Test getting upstream branch when none exists."""
        mock_repo = Mock(spec=Repo)
        mock_branch = Mock()
        mock_branch.tracking_branch.return_value = None
        mock_repo.branches = {"main": mock_branch}

        result = get_branch_upstream(mock_repo, "main")

        assert result is None

    def test_get_branch_upstream_nonexistent_branch(self):
        """Test getting upstream for nonexistent branch returns None."""
        mock_repo = Mock(spec=Repo)
        mock_repo.branches = {}

        result = get_branch_upstream(mock_repo, "nonexistent")

        assert result is None

    def test_is_branch_merged_true(self):
        """Test checking if branch is merged returns True when merged."""
        mock_repo = Mock(spec=Repo)
        mock_branch_commit = Mock(spec=Commit)
        Mock(spec=Commit)
        mock_repo.commit.return_value = mock_branch_commit
        mock_repo.is_ancestor.return_value = True

        result = is_branch_merged(mock_repo, "feature", "main")

        assert result is True

    def test_is_branch_merged_false(self):
        """Test checking if branch is merged returns False when not merged."""
        mock_repo = Mock(spec=Repo)
        mock_branch_commit = Mock(spec=Commit)
        Mock(spec=Commit)
        mock_repo.commit.return_value = mock_branch_commit
        mock_repo.is_ancestor.return_value = False

        result = is_branch_merged(mock_repo, "feature", "main")

        assert result is False

    def test_is_branch_merged_nonexistent_branch(self):
        """Test checking merge with nonexistent branch raises exception."""
        mock_repo = Mock(spec=Repo)
        mock_repo.commit.side_effect = BadName("invalid")

        with pytest.raises(GitException) as exc_info:
            is_branch_merged(mock_repo, "nonexistent", "main")

        assert "does not exist" in str(exc_info.value)

    def test_find_merge_base_success(self):
        """Test finding merge base between two refs."""
        mock_repo = Mock(spec=Repo)
        mock_commit1 = Mock(spec=Commit)
        Mock(spec=Commit)
        mock_merge_base = Mock(spec=Commit)
        mock_repo.commit.return_value = mock_commit1
        mock_repo.merge_base.return_value = [mock_merge_base]

        result = find_merge_base(mock_repo, "main", "feature")

        assert result == mock_merge_base

    def test_find_merge_base_none(self):
        """Test finding merge base when no common ancestor."""
        mock_repo = Mock(spec=Repo)
        mock_commit1 = Mock(spec=Commit)
        Mock(spec=Commit)
        mock_repo.commit.return_value = mock_commit1
        mock_repo.merge_base.return_value = []

        result = find_merge_base(mock_repo, "main", "feature")

        assert result is None

    def test_find_merge_base_nonexistent_ref(self):
        """Test finding merge base with nonexistent ref raises exception."""
        mock_repo = Mock(spec=Repo)
        mock_repo.commit.side_effect = BadName("invalid")

        with pytest.raises(GitException) as exc_info:
            find_merge_base(mock_repo, "nonexistent", "main")

        assert "does not exist" in str(exc_info.value)


class TestRepositoryState:
    """Tests for repository state check utilities."""

    def test_is_repo_clean_true(self):
        """Test checking if repo is clean returns True when clean."""
        mock_repo = Mock(spec=Repo)
        mock_repo.is_dirty.return_value = False
        mock_repo.untracked_files = []

        result = is_repo_clean(mock_repo)

        assert result is True

    def test_is_repo_clean_false_dirty(self):
        """Test checking if repo is clean returns False when dirty."""
        mock_repo = Mock(spec=Repo)
        mock_repo.is_dirty.return_value = True

        result = is_repo_clean(mock_repo)

        assert result is False

    def test_is_repo_clean_false_untracked(self):
        """Test checking if repo is clean returns False with untracked files."""
        mock_repo = Mock(spec=Repo)
        mock_repo.is_dirty.return_value = False
        mock_repo.untracked_files = ["new_file.txt"]

        result = is_repo_clean(mock_repo)

        assert result is False

    def test_get_current_branch_name_success(self):
        """Test getting current branch name."""
        mock_repo = Mock(spec=Repo)
        mock_head = Mock()
        mock_head.is_detached = False
        mock_branch = Mock()
        mock_branch.name = "main"
        type(mock_repo).head = PropertyMock(return_value=mock_head)
        type(mock_repo).active_branch = PropertyMock(return_value=mock_branch)

        result = get_current_branch_name(mock_repo)

        assert result == "main"

    def test_get_current_branch_name_detached(self):
        """Test getting current branch name in detached HEAD state."""
        mock_repo = Mock(spec=Repo)
        mock_head = Mock()
        mock_head.is_detached = True
        type(mock_repo).head = PropertyMock(return_value=mock_head)

        result = get_current_branch_name(mock_repo)

        assert result is None

    def test_is_detached_head_true(self):
        """Test checking if HEAD is detached returns True."""
        mock_repo = Mock(spec=Repo)
        mock_head = Mock()
        mock_head.is_detached = True
        type(mock_repo).head = PropertyMock(return_value=mock_head)

        result = is_detached_head(mock_repo)

        assert result is True

    def test_is_detached_head_false(self):
        """Test checking if HEAD is detached returns False."""
        mock_repo = Mock(spec=Repo)
        mock_head = Mock()
        mock_head.is_detached = False
        type(mock_repo).head = PropertyMock(return_value=mock_head)

        result = is_detached_head(mock_repo)

        assert result is False


class TestRepositoryDetection:
    """Tests for repository detection utilities."""

    @patch("graphite_cli.utils.git_utils.Repo")
    def test_get_repo_root_success(self, mock_repo_class):
        """Test getting repository root."""
        mock_repo = Mock()
        mock_repo.working_dir = "/path/to/repo"
        mock_repo_class.return_value = mock_repo

        result = get_repo_root()

        assert result == Path("/path/to/repo")

    @patch("graphite_cli.utils.git_utils.Repo")
    def test_get_repo_root_not_a_repo(self, mock_repo_class):
        """Test getting repository root when not in a repo."""
        mock_repo_class.side_effect = InvalidGitRepositoryError()

        with pytest.raises(GitException) as exc_info:
            get_repo_root()

        assert "Not a git repository" in str(exc_info.value)

    @patch("graphite_cli.utils.git_utils.Repo")
    def test_is_git_repo_true(self, mock_repo_class):
        """Test checking if directory is a git repo returns True."""
        mock_repo_class.return_value = Mock()

        result = is_git_repo()

        assert result is True

    @patch("graphite_cli.utils.git_utils.Repo")
    def test_is_git_repo_false(self, mock_repo_class):
        """Test checking if directory is a git repo returns False."""
        mock_repo_class.side_effect = InvalidGitRepositoryError()

        result = is_git_repo()

        assert result is False


class TestCommitUtilities:
    """Tests for commit-related utilities."""

    def test_get_commit_count_between_success(self):
        """Test getting commit count between two refs."""
        mock_repo = Mock(spec=Repo)
        mock_commit1 = Mock(spec=Commit)
        mock_commit2 = Mock(spec=Commit)
        mock_commit3 = Mock(spec=Commit)
        mock_repo.commit.return_value = Mock()
        expected_commits = [mock_commit1, mock_commit2, mock_commit3]
        mock_repo.iter_commits.return_value = expected_commits

        result = get_commit_count_between(mock_repo, "main", "feature")

        assert result == len(expected_commits)

    def test_get_commit_count_between_nonexistent_ref(self):
        """Test getting commit count with nonexistent ref raises exception."""
        mock_repo = Mock(spec=Repo)
        mock_repo.commit.side_effect = BadName("invalid")

        with pytest.raises(GitException) as exc_info:
            get_commit_count_between(mock_repo, "nonexistent", "main")

        assert "does not exist" in str(exc_info.value)

    def test_get_short_sha(self):
        """Test getting short SHA from commit."""
        mock_commit = Mock(spec=Commit)
        mock_commit.hexsha = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"

        result = get_short_sha(mock_commit)

        assert result == "a1b2c3d"

    def test_get_short_sha_custom_length(self):
        """Test getting short SHA with custom length."""
        mock_commit = Mock(spec=Commit)
        mock_commit.hexsha = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"

        result = get_short_sha(mock_commit, length=10)

        assert result == "a1b2c3d4e5"
