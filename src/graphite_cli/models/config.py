"""Graphite configuration model.

This module defines the GraphiteConfig dataclass that represents configuration
settings for the Graphite CLI tool. Configuration can be set at both the global
user level and per-repository level.
"""

from dataclasses import dataclass


@dataclass
class GraphiteConfig:
    """Graphite configuration settings.

    Attributes:
        trunk_branch: The main branch name (default: "main").
        remote_name: The Git remote name (default: "origin").
        branch_prefix: Optional prefix for branch names.
        branch_name_template: Template for auto-generated branch names.
        pr_title_template: Template for PR titles.
        pr_body_template: Template for PR body/description.
        include_pr_links: Whether to include PR links in PR descriptions.
        auto_restack: Automatically restack when needed.
        confirm_destructive_ops: Require confirmation for destructive operations.
        merge_method: GitHub merge method (merge, squash, rebase).
        github_token: GitHub authentication token (stored in keyring, not here).
        use_colors: Enable colored terminal output.
        use_emoji: Enable emoji in terminal output.
        show_pr_status: Show PR status in log output.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR).
        cache_github_data: Enable caching of GitHub API responses.
        cache_ttl_seconds: Cache time-to-live in seconds.
    """

    # Repository settings
    trunk_branch: str = "main"
    remote_name: str = "origin"

    # Branch naming
    branch_prefix: str = ""
    branch_name_template: str = "{prefix}{date}_{username}_{description}"

    # PR settings
    pr_title_template: str = "{commit_message}"
    pr_body_template: str = ""
    include_pr_links: bool = True

    # Behavior
    auto_restack: bool = True
    confirm_destructive_ops: bool = True
    merge_method: str = "squash"

    # GitHub
    github_token: str | None = None

    # UI
    use_colors: bool = True
    use_emoji: bool = True
    show_pr_status: bool = True

    # Advanced
    log_level: str = "INFO"
    cache_github_data: bool = True
    cache_ttl_seconds: int = 300

    def __post_init__(self) -> None:
        """Validate configuration after initialization.

        Raises:
            ValueError: If any configuration value is invalid.
        """
        # Validate merge_method
        valid_merge_methods = {"merge", "squash", "rebase"}
        if self.merge_method not in valid_merge_methods:
            msg = f"Invalid merge_method: {self.merge_method}. Must be one of {valid_merge_methods}"
            raise ValueError(msg)

        # Validate log_level
        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level.upper() not in valid_log_levels:
            msg = f"Invalid log_level: {self.log_level}. Must be one of {valid_log_levels}"
            raise ValueError(msg)

        # Normalize log_level to uppercase
        self.log_level = self.log_level.upper()

        # Validate cache_ttl_seconds
        if self.cache_ttl_seconds < 0:
            msg = f"Invalid cache_ttl_seconds: {self.cache_ttl_seconds}. Must be non-negative"
            raise ValueError(msg)

        # Validate trunk_branch is not empty
        if not self.trunk_branch or not self.trunk_branch.strip():
            msg = "trunk_branch cannot be empty"
            raise ValueError(msg)

        # Validate remote_name is not empty
        if not self.remote_name or not self.remote_name.strip():
            msg = "remote_name cannot be empty"
            raise ValueError(msg)


__all__ = ["GraphiteConfig"]
