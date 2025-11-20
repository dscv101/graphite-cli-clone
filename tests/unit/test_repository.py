"""Unit tests for Repository model."""

from pathlib import Path

import pytest

from graphite_cli.models.repository import Repository


class TestRepository:
    """Test suite for Repository model."""

    def test_repository_initialization(self) -> None:
        """Test basic repository initialization."""
        path = Path("/path/to/repo")
        remote_url = "https://github.com/user/repo.git"

        repo = Repository(
            path=path,
            remote_url=remote_url,
        )

        assert repo.path == path
        assert repo.remote_url == remote_url
        assert repo.remote_name == "origin"
        assert repo.owner == ""
        assert repo.name == ""

    def test_repository_with_custom_remote_name(self) -> None:
        """Test repository initialization with custom remote name."""
        path = Path("/path/to/repo")
        remote_url = "https://github.com/user/repo.git"
        remote_name = "upstream"

        repo = Repository(
            path=path,
            remote_url=remote_url,
            remote_name=remote_name,
        )

        assert repo.remote_name == remote_name

    def test_repository_with_owner_and_name(self) -> None:
        """Test repository initialization with owner and name."""
        path = Path("/path/to/repo")
        remote_url = "https://github.com/user/repo.git"
        owner = "user"
        name = "repo"

        repo = Repository(
            path=path,
            remote_url=remote_url,
            owner=owner,
            name=name,
        )

        assert repo.owner == owner
        assert repo.name == name

    def test_is_github_repo_with_https_url(self) -> None:
        """Test is_github_repo() with HTTPS GitHub URL."""
        repo = Repository(
            path=Path("/path/to/repo"),
            remote_url="https://github.com/user/repo.git",
        )

        assert repo.is_github_repo() is True

    def test_is_github_repo_with_ssh_url(self) -> None:
        """Test is_github_repo() with SSH GitHub URL."""
        repo = Repository(
            path=Path("/path/to/repo"),
            remote_url="git@github.com:user/repo.git",
        )

        assert repo.is_github_repo() is True

    def test_is_github_repo_with_gitlab_url(self) -> None:
        """Test is_github_repo() with GitLab URL."""
        repo = Repository(
            path=Path("/path/to/repo"),
            remote_url="https://gitlab.com/user/repo.git",
        )

        assert repo.is_github_repo() is False

    def test_is_github_repo_with_bitbucket_url(self) -> None:
        """Test is_github_repo() with Bitbucket URL."""
        repo = Repository(
            path=Path("/path/to/repo"),
            remote_url="https://bitbucket.org/user/repo.git",
        )

        assert repo.is_github_repo() is False

    def test_is_github_repo_with_custom_host(self) -> None:
        """Test is_github_repo() with custom host."""
        repo = Repository(
            path=Path("/path/to/repo"),
            remote_url="https://git.example.com/user/repo.git",
        )

        assert repo.is_github_repo() is False

    def test_is_github_repo_with_github_enterprise(self) -> None:
        """Test is_github_repo() with GitHub Enterprise URL."""
        repo = Repository(
            path=Path("/path/to/repo"),
            remote_url="https://github.enterprise.com/user/repo.git",
        )

        # Should return False as URL contains 'github.enterprise.com', not 'github.com'
        assert repo.is_github_repo() is False

    def test_get_github_repo_path_success(self) -> None:
        """Test get_github_repo_path() with valid owner and name."""
        repo = Repository(
            path=Path("/path/to/repo"),
            remote_url="https://github.com/user/repo.git",
            owner="user",
            name="repo",
        )

        assert repo.get_github_repo_path() == "user/repo"

    def test_get_github_repo_path_with_org(self) -> None:
        """Test get_github_repo_path() with organization owner."""
        repo = Repository(
            path=Path("/path/to/repo"),
            remote_url="https://github.com/myorg/myrepo.git",
            owner="myorg",
            name="myrepo",
        )

        assert repo.get_github_repo_path() == "myorg/myrepo"

    def test_get_github_repo_path_empty_owner(self) -> None:
        """Test get_github_repo_path() raises error when owner is empty."""
        repo = Repository(
            path=Path("/path/to/repo"),
            remote_url="https://github.com/user/repo.git",
            owner="",
            name="repo",
        )

        with pytest.raises(ValueError, match="owner and name must be set"):
            repo.get_github_repo_path()

    def test_get_github_repo_path_empty_name(self) -> None:
        """Test get_github_repo_path() raises error when name is empty."""
        repo = Repository(
            path=Path("/path/to/repo"),
            remote_url="https://github.com/user/repo.git",
            owner="user",
            name="",
        )

        with pytest.raises(ValueError, match="owner and name must be set"):
            repo.get_github_repo_path()

    def test_get_github_repo_path_both_empty(self) -> None:
        """Test get_github_repo_path() raises error when both are empty."""
        repo = Repository(
            path=Path("/path/to/repo"),
            remote_url="https://github.com/user/repo.git",
            owner="",
            name="",
        )

        with pytest.raises(ValueError, match="owner and name must be set"):
            repo.get_github_repo_path()

    def test_repository_dataclass_equality(self) -> None:
        """Test repository equality comparison."""
        repo1 = Repository(
            path=Path("/path/to/repo"),
            remote_url="https://github.com/user/repo.git",
            owner="user",
            name="repo",
        )
        repo2 = Repository(
            path=Path("/path/to/repo"),
            remote_url="https://github.com/user/repo.git",
            owner="user",
            name="repo",
        )

        assert repo1 == repo2

    def test_repository_dataclass_inequality(self) -> None:
        """Test repository inequality comparison."""
        repo1 = Repository(
            path=Path("/path/to/repo1"),
            remote_url="https://github.com/user/repo1.git",
            owner="user",
            name="repo1",
        )
        repo2 = Repository(
            path=Path("/path/to/repo2"),
            remote_url="https://github.com/user/repo2.git",
            owner="user",
            name="repo2",
        )

        assert repo1 != repo2

    def test_repository_repr(self) -> None:
        """Test repository string representation."""
        repo = Repository(
            path=Path("/path/to/repo"),
            remote_url="https://github.com/user/repo.git",
            owner="user",
            name="repo",
        )

        repo_repr = repr(repo)
        assert "Repository(" in repo_repr
        assert "path=" in repo_repr
        assert "remote_url=" in repo_repr
        assert "owner=" in repo_repr
        assert "name=" in repo_repr


class TestRepositoryEdgeCases:
    """Test edge cases for Repository model."""

    def test_repository_with_path_as_string(self) -> None:
        """Test repository accepts Path object (not string)."""
        # This should work as Path is the expected type
        path = Path("/path/to/repo")
        repo = Repository(
            path=path,
            remote_url="https://github.com/user/repo.git",
        )

        assert isinstance(repo.path, Path)
        assert repo.path == path

    def test_is_github_repo_case_sensitivity(self) -> None:
        """Test is_github_repo() is case-sensitive."""
        # Test with uppercase
        repo = Repository(
            path=Path("/path/to/repo"),
            remote_url="https://GITHUB.COM/user/repo.git",
        )

        # Should return False as check is case-sensitive
        assert repo.is_github_repo() is False

    def test_get_github_repo_path_with_special_characters(self) -> None:
        """Test get_github_repo_path() with special characters."""
        repo = Repository(
            path=Path("/path/to/repo"),
            remote_url="https://github.com/user-name/repo.name.git",
            owner="user-name",
            name="repo.name",
        )

        assert repo.get_github_repo_path() == "user-name/repo.name"

    def test_repository_with_long_paths(self) -> None:
        """Test repository with very long path."""
        long_path = Path("/very/long/path/to/repository" * 10)
        repo = Repository(
            path=long_path,
            remote_url="https://github.com/user/repo.git",
        )

        assert repo.path == long_path

    def test_repository_with_unicode_in_url(self) -> None:
        """Test repository with unicode characters in URL."""
        repo = Repository(
            path=Path("/path/to/repo"),
            remote_url="https://github.com/user/repo-\u4e2d\u6587.git",
        )

        assert repo.remote_url == "https://github.com/user/repo-\u4e2d\u6587.git"
        assert repo.is_github_repo() is True
