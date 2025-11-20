"""Git utility functions for common Git operations.

This module provides low-level utility functions for working with Git
repositories through GitPython. These utilities handle ref parsing, branch
validation, and repository state checks.
"""

import re
from pathlib import Path
from typing import NoReturn

from git import Commit, InvalidGitRepositoryError, Repo
from git.exc import BadName, GitCommandError

from graphite_cli.exceptions import GitException, ValidationException


def is_valid_branch_name(name: str) -> bool:
    """Check if a branch name is valid according to Git naming rules.

    Args:
        name: The branch name to validate.

    Returns:
        True if the branch name is valid, False otherwise.

    Examples:
        >>> is_valid_branch_name("feature/new-feature")
        True
        >>> is_valid_branch_name("")
        False
        >>> is_valid_branch_name("feature..bad")
        False
    """
    if not name:
        return False

    # Git branch name rules:
    # 1. Cannot be empty
    # 2. Cannot start with '-' or '.'
    # 3. Cannot contain '..' (consecutive dots)
    # 4. Cannot contain '~', '^', ':', '\', '*', '?', '[', ' '
    # 5. Cannot end with '/'
    # 6. Cannot end with '.lock'
    # 7. Cannot contain '@{'

    invalid_patterns = [
        r"^\.",  # starts with .
        r"^\-",  # starts with -
        r"\.\.",  # contains ..
        r"[~^:\\\*\?\[\s]",  # contains invalid chars
        r"/$",  # ends with /
        r"\.lock$",  # ends with .lock
        r"@\{",  # contains @{
        r"/\.",  # contains /.
    ]

    return all(not re.search(pattern, name) for pattern in invalid_patterns)


def validate_branch_name(name: str) -> None:
    """Validate a branch name and raise an exception if invalid.

    Args:
        name: The branch name to validate.

    Raises:
        ValidationException: If the branch name is invalid.

    Examples:
        >>> validate_branch_name("feature/new-feature")  # No exception
        >>> validate_branch_name("")
        Traceback (most recent call last):
        ...
        ValidationException: Invalid branch name: ''
    """
    if not is_valid_branch_name(name):
        msg = f"Invalid branch name: '{name}'"
        raise ValidationException(
            msg,
            hint=(
                "Branch names must not:\n"
                "  - Be empty\n"
                "  - Start with '-' or '.'\n"
                "  - Contain '..' (consecutive dots)\n"
                "  - Contain special characters: ~ ^ : \\ * ? [ space\n"
                "  - End with '/'\n"
                "  - End with '.lock'\n"
                "  - Contain '@{'"
            ),
        )


def parse_ref(repo: Repo, ref_string: str) -> Commit | None:
    """Parse a ref string and return the corresponding commit.

    This function resolves various Git ref formats including:
    - Branch names (e.g., "main", "feature/branch")
    - Tags (e.g., "v1.0.0")
    - Commit SHAs (full or abbreviated)
    - Symbolic refs (e.g., "HEAD")
    - Relative refs (e.g., "HEAD~1", "main^")

    Args:
        repo: The Git repository.
        ref_string: The ref string to parse.

    Returns:
        The commit object if the ref exists, None if it doesn't exist.

    Examples:
        >>> repo = Repo(".")
        >>> commit = parse_ref(repo, "HEAD")
        >>> commit = parse_ref(repo, "main")
        >>> commit = parse_ref(repo, "v1.0.0")
    """
    try:
        return repo.commit(ref_string)
    except (BadName, GitCommandError):
        return None


def _raise_ref_not_found_error(ref_string: str) -> NoReturn:
    """Helper function to raise ref not found error."""
    msg = f"Could not resolve ref: '{ref_string}'"
    raise GitException(
        msg,
        hint="Ensure the branch, tag, or commit exists in the repository.",
    )


def resolve_ref(repo: Repo, ref_string: str) -> str:
    """Resolve a ref string to its full ref name.

    Args:
        repo: The Git repository.
        ref_string: The ref string to resolve (e.g., "main", "HEAD").

    Returns:
        The full ref name (e.g., "refs/heads/main", "HEAD").

    Raises:
        GitException: If the ref cannot be resolved.

    Examples:
        >>> repo = Repo(".")
        >>> resolve_ref(repo, "main")
        'refs/heads/main'
        >>> resolve_ref(repo, "HEAD")
        'HEAD'
    """
    try:
        # Try to find as a branch
        if ref_string in repo.branches:
            return f"refs/heads/{ref_string}"

        # Try to find as a tag
        if ref_string in repo.tags:
            return f"refs/tags/{ref_string}"

        # Check if it's already a full ref
        if ref_string.startswith("refs/") and ref_exists(repo, ref_string):
            return ref_string

        # Check if it's HEAD or other symbolic ref
        if ref_string == "HEAD" or ref_string.startswith("refs/"):
            return ref_string

        # If we can parse it as a commit, it might be a SHA
        commit = parse_ref(repo, ref_string)
        if commit:
            return commit.hexsha

        _raise_ref_not_found_error(ref_string)
    except Exception as e:
        if isinstance(e, GitException):
            raise
        msg = f"Failed to resolve ref '{ref_string}': {e}"
        raise GitException(
            msg,
            hint="Check that the ref exists and the repository is in a valid state.",
        ) from e


def ref_exists(repo: Repo, ref_string: str) -> bool:
    """Check if a ref exists in the repository.

    Args:
        repo: The Git repository.
        ref_string: The ref string to check.

    Returns:
        True if the ref exists, False otherwise.

    Examples:
        >>> repo = Repo(".")
        >>> ref_exists(repo, "main")
        True
        >>> ref_exists(repo, "nonexistent-branch")
        False
    """
    return parse_ref(repo, ref_string) is not None


def get_branch_upstream(repo: Repo, branch_name: str) -> str | None:
    """Get the upstream tracking branch for a local branch.

    Args:
        repo: The Git repository.
        branch_name: The local branch name.

    Returns:
        The upstream branch name (e.g., "origin/main"), or None if no
        upstream is configured.

    Examples:
        >>> repo = Repo(".")
        >>> get_branch_upstream(repo, "main")
        'origin/main'
    """
    try:
        if branch_name not in repo.branches:
            return None
        branch = repo.branches[branch_name]
        tracking_branch = branch.tracking_branch()
    except (IndexError, GitCommandError, KeyError):
        return None
    else:
        return tracking_branch.name if tracking_branch else None


def is_branch_merged(repo: Repo, branch: str, into_branch: str) -> bool:
    """Check if a branch has been fully merged into another branch.

    Args:
        repo: The Git repository.
        branch: The branch to check.
        into_branch: The branch to check against.

    Returns:
        True if branch is fully merged into into_branch, False otherwise.

    Raises:
        GitException: If either branch doesn't exist.

    Examples:
        >>> repo = Repo(".")
        >>> is_branch_merged(repo, "feature", "main")
        False
    """
    if not ref_exists(repo, branch):
        msg = f"Branch '{branch}' does not exist"
        raise GitException(
            msg,
            hint="Ensure the branch name is correct.",
        )

    if not ref_exists(repo, into_branch):
        msg = f"Branch '{into_branch}' does not exist"
        raise GitException(
            msg,
            hint="Ensure the branch name is correct.",
        )

    try:
        # Use git merge-base --is-ancestor
        branch_commit = repo.commit(branch)
        into_commit = repo.commit(into_branch)

        # If branch commit is an ancestor of into_branch, it's merged
        return repo.is_ancestor(branch_commit, into_commit)
    except GitCommandError as e:
        msg = f"Failed to check if '{branch}' is merged into '{into_branch}': {e}"
        raise GitException(
            msg,
            hint="Check that both branches exist and are valid.",
        ) from e


def find_merge_base(repo: Repo, ref1: str, ref2: str) -> Commit | None:
    """Find the best common ancestor (merge base) between two refs.

    Args:
        repo: The Git repository.
        ref1: The first ref.
        ref2: The second ref.

    Returns:
        The merge base commit, or None if no common ancestor exists.

    Raises:
        GitException: If either ref doesn't exist.

    Examples:
        >>> repo = Repo(".")
        >>> merge_base = find_merge_base(repo, "main", "feature")
    """
    if not ref_exists(repo, ref1):
        msg = f"Ref '{ref1}' does not exist"
        raise GitException(
            msg,
            hint="Ensure the ref name is correct.",
        )

    if not ref_exists(repo, ref2):
        msg = f"Ref '{ref2}' does not exist"
        raise GitException(
            msg,
            hint="Ensure the ref name is correct.",
        )

    try:
        commit1 = repo.commit(ref1)
        commit2 = repo.commit(ref2)

        # Find merge base using git merge-base
        merge_bases = repo.merge_base(commit1, commit2)

        # Return the first (and typically only) merge base
        return merge_bases[0] if merge_bases else None
    except GitCommandError as e:
        msg = f"Failed to find merge base between '{ref1}' and '{ref2}': {e}"
        raise GitException(
            msg,
            hint="Check that both refs exist and have common history.",
        ) from e


def is_repo_clean(repo: Repo) -> bool:
    """Check if the repository has a clean working tree.

    A clean working tree means no uncommitted changes (staged or unstaged)
    and no untracked files that would be committed.

    Args:
        repo: The Git repository.

    Returns:
        True if the working tree is clean, False otherwise.

    Examples:
        >>> repo = Repo(".")
        >>> is_repo_clean(repo)
        True
    """
    try:
        # Check for any changes (staged or unstaged)
        if repo.is_dirty(untracked_files=False):
            return False

        # Check for untracked files (excluding ignored files)
        untracked = repo.untracked_files
        return len(untracked) == 0
    except GitCommandError:
        # If we can't determine state, assume dirty for safety
        return False


def get_current_branch_name(repo: Repo) -> str | None:
    """Get the name of the currently checked out branch.

    Args:
        repo: The Git repository.

    Returns:
        The current branch name, or None if in detached HEAD state.

    Examples:
        >>> repo = Repo(".")
        >>> get_current_branch_name(repo)
        'main'
    """
    try:
        if repo.head.is_detached:
            return None
    except (GitCommandError, TypeError):
        return None
    else:
        return repo.active_branch.name


def is_detached_head(repo: Repo) -> bool:
    """Check if the repository is in detached HEAD state.

    Args:
        repo: The Git repository.

    Returns:
        True if in detached HEAD state, False otherwise.

    Examples:
        >>> repo = Repo(".")
        >>> is_detached_head(repo)
        False
    """
    try:
        return repo.head.is_detached
    except (GitCommandError, TypeError):
        # If we can't determine, assume detached for safety
        return True


def get_repo_root(path: Path | None = None) -> Path:
    """Find the root directory of a Git repository.

    Args:
        path: The path to start searching from. Defaults to current directory.

    Returns:
        The path to the repository root directory.

    Raises:
        GitException: If no Git repository is found.

    Examples:
        >>> root = get_repo_root()
        >>> root = get_repo_root(Path("/path/to/repo/subdir"))
    """
    search_path = path or Path.cwd()
    try:
        repo = Repo(search_path, search_parent_directories=True)
        return Path(repo.working_dir)
    except InvalidGitRepositoryError as e:
        msg = f"Not a git repository: {search_path}"
        raise GitException(
            msg,
            hint=(
                "Ensure you are inside a Git repository.\nInitialize a repository with: git init"
            ),
        ) from e


def is_git_repo(path: Path | None = None) -> bool:
    """Check if a directory is a Git repository.

    Args:
        path: The path to check. Defaults to current directory.

    Returns:
        True if the directory is a Git repository, False otherwise.

    Examples:
        >>> is_git_repo()
        True
        >>> is_git_repo(Path("/tmp"))
        False
    """
    try:
        search_path = path or Path.cwd()
        Repo(search_path, search_parent_directories=True)
    except InvalidGitRepositoryError:
        return False
    else:
        return True


def get_commit_count_between(repo: Repo, base_ref: str, head_ref: str) -> int:
    """Get the number of commits between two refs.

    Args:
        repo: The Git repository.
        base_ref: The base ref (older commit).
        head_ref: The head ref (newer commit).

    Returns:
        The number of commits from base_ref to head_ref (exclusive of base).

    Raises:
        GitException: If either ref doesn't exist.

    Examples:
        >>> repo = Repo(".")
        >>> count = get_commit_count_between(repo, "main", "feature")
    """
    if not ref_exists(repo, base_ref):
        msg = f"Ref '{base_ref}' does not exist"
        raise GitException(
            msg,
            hint="Ensure the ref name is correct.",
        )

    if not ref_exists(repo, head_ref):
        msg = f"Ref '{head_ref}' does not exist"
        raise GitException(
            msg,
            hint="Ensure the ref name is correct.",
        )

    try:
        # Get commits in head_ref that are not in base_ref
        commits = list(repo.iter_commits(f"{base_ref}..{head_ref}"))
        return len(commits)
    except GitCommandError as e:
        msg = f"Failed to count commits between '{base_ref}' and '{head_ref}': {e}"
        raise GitException(
            msg,
            hint="Check that both refs exist and have common history.",
        ) from e


def get_short_sha(commit: Commit, length: int = 7) -> str:
    """Get a shortened version of a commit SHA.

    Args:
        commit: The commit object.
        length: The desired length of the short SHA (default: 7).

    Returns:
        The shortened commit SHA.

    Examples:
        >>> repo = Repo(".")
        >>> commit = repo.head.commit
        >>> get_short_sha(commit)
        'a1b2c3d'
    """
    return commit.hexsha[:length]


__all__ = [
    "find_merge_base",
    "get_branch_upstream",
    "get_commit_count_between",
    "get_current_branch_name",
    "get_repo_root",
    "get_short_sha",
    "is_branch_merged",
    "is_detached_head",
    "is_git_repo",
    "is_repo_clean",
    "is_valid_branch_name",
    "parse_ref",
    "ref_exists",
    "resolve_ref",
    "validate_branch_name",
]
