"""Utility functions package."""

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
