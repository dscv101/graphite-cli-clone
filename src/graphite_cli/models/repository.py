"""Repository model for Git repository state."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Repository:
    """Represents Git repository state.

    This model encapsulates the core properties of a Git repository,
    including its local path, remote configuration, and GitHub metadata.

    Attributes:
        path: Path to repository root directory.
        remote_url: URL of the remote repository.
        remote_name: Name of the remote (typically 'origin').
        owner: Repository owner (parsed from remote URL for GitHub repos).
        name: Repository name (parsed from remote URL).
    """

    path: Path
    remote_url: str
    remote_name: str = "origin"
    owner: str = ""
    name: str = ""

    def is_github_repo(self) -> bool:
        """Check if repository is hosted on GitHub.

        Returns:
            True if the remote URL contains 'github.com', False otherwise.

        Examples:
            >>> repo = Repository(
            ...     path=Path("/path/to/repo"),
            ...     remote_url="https://github.com/user/repo.git"
            ... )
            >>> repo.is_github_repo()
            True

            >>> repo = Repository(
            ...     path=Path("/path/to/repo"),
            ...     remote_url="https://gitlab.com/user/repo.git"
            ... )
            >>> repo.is_github_repo()
            False
        """
        return "github.com" in self.remote_url

    def get_github_repo_path(self) -> str:
        """Get GitHub repository path in the format 'owner/name'.

        Returns:
            The repository path as 'owner/name'.

        Raises:
            ValueError: If owner or name is empty (indicates repo is not
                properly initialized or is not a GitHub repository).

        Examples:
            >>> repo = Repository(
            ...     path=Path("/path/to/repo"),
            ...     remote_url="https://github.com/user/repo.git",
            ...     owner="user",
            ...     name="repo"
            ... )
            >>> repo.get_github_repo_path()
            'user/repo'
        """
        if not self.owner or not self.name:
            msg = (
                "Repository owner and name must be set. "
                "Ensure the repository is properly initialized."
            )
            raise ValueError(msg)
        return f"{self.owner}/{self.name}"
