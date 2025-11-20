"""Unit tests for GraphiteConfig model."""

import pytest

from graphite_cli.models.config import GraphiteConfig

# Test constants
DEFAULT_CACHE_TTL = 300
TEST_CACHE_TTL = 600
LARGE_CACHE_TTL = 86400
TEST_GITHUB_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"  # noqa: S105


class TestGraphiteConfigDefaults:
    """Test default configuration values."""

    def test_default_values(self):
        """Test that default configuration values are correct."""
        config = GraphiteConfig()

        # Repository settings
        assert config.trunk_branch == "main"
        assert config.remote_name == "origin"

        # Branch naming
        assert config.branch_prefix == ""
        assert config.branch_name_template == "{prefix}{date}_{username}_{description}"

        # PR settings
        assert config.pr_title_template == "{commit_message}"
        assert config.pr_body_template == ""
        assert config.include_pr_links is True

        # Behavior
        assert config.auto_restack is True
        assert config.confirm_destructive_ops is True
        assert config.merge_method == "squash"

        # GitHub
        assert config.github_token is None

        # UI
        assert config.use_colors is True
        assert config.use_emoji is True
        assert config.show_pr_status is True

        # Advanced
        assert config.log_level == "INFO"
        assert config.cache_github_data is True
        assert config.cache_ttl_seconds == DEFAULT_CACHE_TTL


class TestGraphiteConfigValidation:
    """Test configuration validation logic."""

    def test_valid_merge_method_merge(self):
        """Test that 'merge' is a valid merge method."""
        config = GraphiteConfig(merge_method="merge")
        assert config.merge_method == "merge"

    def test_valid_merge_method_squash(self):
        """Test that 'squash' is a valid merge method."""
        config = GraphiteConfig(merge_method="squash")
        assert config.merge_method == "squash"

    def test_valid_merge_method_rebase(self):
        """Test that 'rebase' is a valid merge method."""
        config = GraphiteConfig(merge_method="rebase")
        assert config.merge_method == "rebase"

    def test_invalid_merge_method(self):
        """Test that invalid merge method raises ValueError."""
        with pytest.raises(ValueError, match="Invalid merge_method: invalid"):
            GraphiteConfig(merge_method="invalid")

    def test_valid_log_level_debug(self):
        """Test that 'DEBUG' is a valid log level."""
        config = GraphiteConfig(log_level="DEBUG")
        assert config.log_level == "DEBUG"

    def test_valid_log_level_info(self):
        """Test that 'INFO' is a valid log level."""
        config = GraphiteConfig(log_level="INFO")
        assert config.log_level == "INFO"

    def test_valid_log_level_warning(self):
        """Test that 'WARNING' is a valid log level."""
        config = GraphiteConfig(log_level="WARNING")
        assert config.log_level == "WARNING"

    def test_valid_log_level_error(self):
        """Test that 'ERROR' is a valid log level."""
        config = GraphiteConfig(log_level="ERROR")
        assert config.log_level == "ERROR"

    def test_valid_log_level_critical(self):
        """Test that 'CRITICAL' is a valid log level."""
        config = GraphiteConfig(log_level="CRITICAL")
        assert config.log_level == "CRITICAL"

    def test_log_level_case_insensitive(self):
        """Test that log level is normalized to uppercase."""
        config = GraphiteConfig(log_level="debug")
        assert config.log_level == "DEBUG"

        config = GraphiteConfig(log_level="Info")
        assert config.log_level == "INFO"

        config = GraphiteConfig(log_level="warning")
        assert config.log_level == "WARNING"

    def test_invalid_log_level(self):
        """Test that invalid log level raises ValueError."""
        with pytest.raises(ValueError, match="Invalid log_level: INVALID"):
            GraphiteConfig(log_level="INVALID")

    def test_negative_cache_ttl(self):
        """Test that negative cache TTL raises ValueError."""
        with pytest.raises(
            ValueError, match=r"Invalid cache_ttl_seconds: -1\. Must be non-negative"
        ):
            GraphiteConfig(cache_ttl_seconds=-1)

    def test_zero_cache_ttl(self):
        """Test that zero cache TTL is valid."""
        config = GraphiteConfig(cache_ttl_seconds=0)
        assert config.cache_ttl_seconds == 0

    def test_positive_cache_ttl(self):
        """Test that positive cache TTL is valid."""
        config = GraphiteConfig(cache_ttl_seconds=TEST_CACHE_TTL)
        assert config.cache_ttl_seconds == TEST_CACHE_TTL

    def test_empty_trunk_branch(self):
        """Test that empty trunk branch raises ValueError."""
        with pytest.raises(ValueError, match="trunk_branch cannot be empty"):
            GraphiteConfig(trunk_branch="")

    def test_whitespace_trunk_branch(self):
        """Test that whitespace-only trunk branch raises ValueError."""
        with pytest.raises(ValueError, match="trunk_branch cannot be empty"):
            GraphiteConfig(trunk_branch="   ")

    def test_valid_trunk_branch(self):
        """Test that valid trunk branch is accepted."""
        config = GraphiteConfig(trunk_branch="develop")
        assert config.trunk_branch == "develop"

    def test_empty_remote_name(self):
        """Test that empty remote name raises ValueError."""
        with pytest.raises(ValueError, match="remote_name cannot be empty"):
            GraphiteConfig(remote_name="")

    def test_whitespace_remote_name(self):
        """Test that whitespace-only remote name raises ValueError."""
        with pytest.raises(ValueError, match="remote_name cannot be empty"):
            GraphiteConfig(remote_name="   ")

    def test_valid_remote_name(self):
        """Test that valid remote name is accepted."""
        config = GraphiteConfig(remote_name="upstream")
        assert config.remote_name == "upstream"


class TestGraphiteConfigCustomization:
    """Test custom configuration values."""

    def test_custom_branch_prefix(self):
        """Test setting custom branch prefix."""
        config = GraphiteConfig(branch_prefix="feature/")
        assert config.branch_prefix == "feature/"

    def test_custom_branch_name_template(self):
        """Test setting custom branch name template."""
        template = "{username}/{description}"
        config = GraphiteConfig(branch_name_template=template)
        assert config.branch_name_template == template

    def test_custom_pr_templates(self):
        """Test setting custom PR templates."""
        title_template = "[{branch}] {commit_message}"
        body_template = "## Changes\n\n{description}"
        config = GraphiteConfig(pr_title_template=title_template, pr_body_template=body_template)
        assert config.pr_title_template == title_template
        assert config.pr_body_template == body_template

    def test_disable_pr_links(self):
        """Test disabling PR links."""
        config = GraphiteConfig(include_pr_links=False)
        assert config.include_pr_links is False

    def test_disable_auto_restack(self):
        """Test disabling auto restack."""
        config = GraphiteConfig(auto_restack=False)
        assert config.auto_restack is False

    def test_disable_confirm_destructive_ops(self):
        """Test disabling destructive operation confirmation."""
        config = GraphiteConfig(confirm_destructive_ops=False)
        assert config.confirm_destructive_ops is False

    def test_github_token(self):
        """Test setting GitHub token."""
        config = GraphiteConfig(github_token=TEST_GITHUB_TOKEN)
        assert config.github_token == TEST_GITHUB_TOKEN

    def test_disable_colors(self):
        """Test disabling colored output."""
        config = GraphiteConfig(use_colors=False)
        assert config.use_colors is False

    def test_disable_emoji(self):
        """Test disabling emoji."""
        config = GraphiteConfig(use_emoji=False)
        assert config.use_emoji is False

    def test_disable_pr_status(self):
        """Test disabling PR status display."""
        config = GraphiteConfig(show_pr_status=False)
        assert config.show_pr_status is False

    def test_disable_cache(self):
        """Test disabling GitHub data cache."""
        config = GraphiteConfig(cache_github_data=False)
        assert config.cache_github_data is False

    def test_custom_cache_ttl(self):
        """Test setting custom cache TTL."""
        config = GraphiteConfig(cache_ttl_seconds=TEST_CACHE_TTL)
        assert config.cache_ttl_seconds == TEST_CACHE_TTL


class TestGraphiteConfigEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_all_custom_values(self):
        """Test creating config with all custom values."""
        config = GraphiteConfig(
            trunk_branch="develop",
            remote_name="upstream",
            branch_prefix="feat/",
            branch_name_template="{prefix}{description}",
            pr_title_template="[PR] {commit_message}",
            pr_body_template="Description: {description}",
            include_pr_links=False,
            auto_restack=False,
            confirm_destructive_ops=False,
            merge_method="merge",
            github_token=TEST_GITHUB_TOKEN,
            use_colors=False,
            use_emoji=False,
            show_pr_status=False,
            log_level="DEBUG",
            cache_github_data=False,
            cache_ttl_seconds=600,
        )

        assert config.trunk_branch == "develop"
        assert config.remote_name == "upstream"
        assert config.branch_prefix == "feat/"
        assert config.merge_method == "merge"
        assert config.log_level == "DEBUG"
        assert config.cache_ttl_seconds == TEST_CACHE_TTL

    def test_empty_string_fields(self):
        """Test that empty strings are valid for optional string fields."""
        config = GraphiteConfig(branch_prefix="", pr_body_template="", github_token="")
        assert config.branch_prefix == ""
        assert config.pr_body_template == ""
        assert config.github_token == ""

    def test_none_github_token(self):
        """Test that None is valid for github_token."""
        config = GraphiteConfig(github_token=None)
        assert config.github_token is None

    def test_large_cache_ttl(self):
        """Test that large cache TTL values are accepted."""
        config = GraphiteConfig(cache_ttl_seconds=LARGE_CACHE_TTL)  # 24 hours
        assert config.cache_ttl_seconds == LARGE_CACHE_TTL

    def test_mixed_case_log_level_normalization(self):
        """Test that mixed case log levels are normalized."""
        test_cases = [
            ("debug", "DEBUG"),
            ("Debug", "DEBUG"),
            ("DeBuG", "DEBUG"),
            ("info", "INFO"),
            ("warning", "WARNING"),
            ("error", "ERROR"),
            ("critical", "CRITICAL"),
        ]

        for input_level, expected_level in test_cases:
            config = GraphiteConfig(log_level=input_level)
            assert config.log_level == expected_level
