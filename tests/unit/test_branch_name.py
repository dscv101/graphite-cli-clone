"""Unit tests for branch_name module."""

import os
from datetime import datetime
from unittest.mock import patch

import pytest

from graphite_cli.utils.branch_name import (
    format_branch_description,
    generate_branch_name,
    parse_template,
    validate_branch_name,
    validate_template,
)


class TestGenerateBranchName:
    """Tests for generate_branch_name function."""

    @patch.dict(os.environ, {"USER": "testuser"})
    @patch("graphite_cli.utils.branch_name.datetime")
    def test_generate_with_all_placeholders(self, mock_datetime):
        """Test generating branch name with all placeholders."""
        mock_datetime.now.return_value = datetime(2024, 1, 15, 10, 30)

        result = generate_branch_name(
            "Fix Login Bug",
            prefix="feature/",
            template="{prefix}{date}_{username}_{description}",
            date_format="%Y%m%d",
        )

        assert result == "feature/20240115_testuser_fix-login-bug"

    @patch.dict(os.environ, {"USER": "john"})
    def test_generate_with_only_description(self):
        """Test generating branch name with only description."""
        result = generate_branch_name(
            "add tests",
            template="{description}",
        )

        assert result == "add-tests"

    @patch.dict(os.environ, {"USER": "alice"})
    @patch("graphite_cli.utils.branch_name.datetime")
    def test_generate_with_custom_date_format(self, mock_datetime):
        """Test generating branch name with custom date format."""
        mock_datetime.now.return_value = datetime(2024, 3, 5, 14, 20)

        result = generate_branch_name(
            "new feature",
            template="{date}/{description}",
            date_format="%Y-%m-%d",
        )

        assert result == "2024-03-05/new-feature"

    @patch.dict(os.environ, {"USER": "bob"})
    def test_generate_with_custom_username(self):
        """Test generating branch name with custom username."""
        result = generate_branch_name(
            "bug fix",
            username="custom_user",
            template="{username}/{description}",
        )

        assert result == "custom-user/bug-fix"

    def test_generate_sanitizes_special_characters(self):
        """Test that special characters are sanitized."""
        result = generate_branch_name(
            "Fix Bug #123!",
            template="{description}",
        )

        assert result == "fix-bug-123"

    def test_generate_sanitizes_spaces(self):
        """Test that spaces are converted to hyphens."""
        result = generate_branch_name(
            "Add New Feature",
            template="{description}",
        )

        assert result == "add-new-feature"

    def test_generate_removes_consecutive_hyphens(self):
        """Test that consecutive hyphens are removed."""
        result = generate_branch_name(
            "Fix---Multiple---Hyphens",
            template="{description}",
        )

        assert result == "fix-multiple-hyphens"

    def test_generate_preserves_slashes_in_prefix(self):
        """Test that slashes in prefix are preserved."""
        result = generate_branch_name(
            "test",
            prefix="feature/bugfix/",
            template="{prefix}{description}",
        )

        assert result == "feature/bugfix/test"

    def test_generate_raises_on_empty_description(self):
        """Test that empty description raises ValueError."""
        with pytest.raises(ValueError, match="Description cannot be empty"):
            generate_branch_name("")

    def test_generate_raises_on_whitespace_description(self):
        """Test that whitespace-only description raises ValueError."""
        with pytest.raises(ValueError, match="Description cannot be empty"):
            generate_branch_name("   ")

    @patch.dict(os.environ, {}, clear=True)
    def test_generate_uses_default_username_when_not_set(self):
        """Test that default username is used when not in environment."""
        result = generate_branch_name(
            "test",
            template="{username}/{description}",
        )

        assert result == "user/test"

    def test_generate_handles_underscores(self):
        """Test that underscores are converted to hyphens."""
        result = generate_branch_name(
            "fix_login_bug",
            template="{description}",
        )

        assert result == "fix-login-bug"


class TestValidateBranchName:
    """Tests for validate_branch_name function."""

    def test_validate_accepts_valid_names(self):
        """Test that valid branch names are accepted."""
        valid_names = [
            "feature/my-branch",
            "bugfix/fix-123",
            "main",
            "develop",
            "feature/sub/nested",
            "release-1.2.3",
        ]

        for name in valid_names:
            validate_branch_name(name)  # Should not raise

    def test_validate_rejects_empty_name(self):
        """Test that empty name is rejected."""
        with pytest.raises(ValueError, match="Branch name cannot be empty"):
            validate_branch_name("")

    def test_validate_rejects_leading_hyphen(self):
        """Test that name starting with hyphen is rejected."""
        with pytest.raises(ValueError, match="cannot start with a hyphen"):
            validate_branch_name("-feature")

    def test_validate_rejects_trailing_hyphen(self):
        """Test that name ending with hyphen is rejected."""
        with pytest.raises(ValueError, match="cannot end with a hyphen"):
            validate_branch_name("feature-")

    def test_validate_rejects_consecutive_periods(self):
        """Test that consecutive periods are rejected."""
        with pytest.raises(ValueError, match="cannot contain consecutive periods"):
            validate_branch_name("branch..name")

    def test_validate_rejects_leading_slash(self):
        """Test that name starting with slash is rejected."""
        with pytest.raises(ValueError, match="cannot start with a slash"):
            validate_branch_name("/feature")

    def test_validate_rejects_trailing_slash(self):
        """Test that name ending with slash is rejected."""
        with pytest.raises(ValueError, match="cannot end with a slash"):
            validate_branch_name("feature/")

    def test_validate_rejects_consecutive_slashes(self):
        """Test that consecutive slashes are rejected."""
        with pytest.raises(ValueError, match="cannot contain consecutive slashes"):
            validate_branch_name("feature//branch")

    def test_validate_rejects_at_brace(self):
        """Test that '@{' pattern is rejected."""
        with pytest.raises(ValueError, match="cannot contain '@{'"):
            validate_branch_name("branch@{name}")

    def test_validate_rejects_special_characters(self):
        """Test that special characters are rejected."""
        invalid_chars = [" ", "~", "^", ":", "?", "*", "["]

        for char in invalid_chars:
            with pytest.raises(ValueError, match="cannot contain"):
                validate_branch_name(f"branch{char}name")

    def test_validate_rejects_at_symbol(self):
        """Test that '@' as name is rejected."""
        with pytest.raises(ValueError, match="cannot be '@'"):
            validate_branch_name("@")

    def test_validate_rejects_period(self):
        """Test that '.' as name is rejected."""
        with pytest.raises(ValueError, match="cannot be '.'"):
            validate_branch_name(".")

    def test_validate_rejects_component_starting_with_period(self):
        """Test that components starting with period are rejected."""
        with pytest.raises(ValueError, match="components cannot start with a period"):
            validate_branch_name("feature/.hidden")


class TestFormatBranchDescription:
    """Tests for format_branch_description function."""

    def test_format_basic_description(self):
        """Test formatting a basic description."""
        result = format_branch_description("Fix Bug #123")
        assert result == "fix-bug-123"

    def test_format_truncates_long_description(self):
        """Test that long descriptions are truncated."""
        long_desc = "This is a very long description that exceeds the maximum length"
        result = format_branch_description(long_desc, max_length=20)

        assert len(result) <= 20
        assert not result.endswith("-")

    def test_format_truncates_at_hyphen(self):
        """Test that truncation prefers breaking at hyphen."""
        desc = "add-user-authentication-feature"
        result = format_branch_description(desc, max_length=18)

        # Should break at last hyphen within max_length if > max_length/2
        # "add-user-authentic" is 18 chars, last hyphen at pos 16
        assert result == "add-user-authentic"

    def test_format_handles_no_hyphens(self):
        """Test truncation when no hyphens available."""
        desc = "verylongdescriptionwithnohyphens"
        result = format_branch_description(desc, max_length=10)

        assert len(result) == 10
        assert result == "verylongde"

    def test_format_removes_trailing_hyphen(self):
        """Test that trailing hyphen is removed after truncation."""
        result = format_branch_description("test-description", max_length=5)
        assert not result.endswith("-")

    def test_format_preserves_short_description(self):
        """Test that short descriptions are not truncated."""
        result = format_branch_description("short", max_length=50)
        assert result == "short"


class TestParseTemplate:
    """Tests for parse_template function."""

    def test_parse_extracts_all_placeholders(self):
        """Test extracting all placeholders from template."""
        template = "{prefix}{date}_{username}_{description}"
        result = parse_template(template)

        assert result == ["prefix", "date", "username", "description"]

    def test_parse_handles_no_placeholders(self):
        """Test parsing template with no placeholders."""
        template = "static-branch-name"
        result = parse_template(template)

        assert result == []

    def test_parse_handles_single_placeholder(self):
        """Test parsing template with single placeholder."""
        template = "{description}"
        result = parse_template(template)

        assert result == ["description"]

    def test_parse_handles_duplicate_placeholders(self):
        """Test parsing template with duplicate placeholders."""
        template = "{prefix}/{prefix}/{description}"
        result = parse_template(template)

        assert result == ["prefix", "prefix", "description"]


class TestValidateTemplate:
    """Tests for validate_template function."""

    def test_validate_accepts_valid_templates(self):
        """Test that valid templates are accepted."""
        valid_templates = [
            "{prefix}{date}_{username}_{description}",
            "{description}",
            "{date}/{username}/{description}",
            "static-{prefix}",
        ]

        for template in valid_templates:
            validate_template(template)  # Should not raise

    def test_validate_accepts_empty_template(self):
        """Test that template with no placeholders is accepted."""
        validate_template("static-branch-name")  # Should not raise

    def test_validate_rejects_invalid_placeholders(self):
        """Test that invalid placeholders are rejected."""
        with pytest.raises(ValueError, match="Invalid template placeholders"):
            validate_template("{invalid_placeholder}")

    def test_validate_rejects_multiple_invalid_placeholders(self):
        """Test that multiple invalid placeholders are reported."""
        with pytest.raises(ValueError, match="invalid1.*invalid2"):
            validate_template("{invalid1}/{invalid2}/{description}")

    def test_validate_accepts_mixed_valid_invalid(self):
        """Test that only invalid placeholders are reported."""
        with pytest.raises(ValueError, match="wrong"):
            validate_template("{prefix}/{wrong}/{description}")


class TestSanitizeBranchComponent:
    """Tests for _sanitize_branch_component helper function."""

    def test_sanitize_converts_to_lowercase(self):
        """Test that uppercase is converted to lowercase."""
        from graphite_cli.utils.branch_name import _sanitize_branch_component

        result = _sanitize_branch_component("UPPERCASE")
        assert result == "uppercase"

    def test_sanitize_replaces_spaces_with_hyphens(self):
        """Test that spaces are replaced with hyphens."""
        from graphite_cli.utils.branch_name import _sanitize_branch_component

        result = _sanitize_branch_component("hello world")
        assert result == "hello-world"

    def test_sanitize_replaces_underscores_with_hyphens(self):
        """Test that underscores are replaced with hyphens."""
        from graphite_cli.utils.branch_name import _sanitize_branch_component

        result = _sanitize_branch_component("hello_world")
        assert result == "hello-world"

    def test_sanitize_removes_special_characters(self):
        """Test that special characters are removed."""
        from graphite_cli.utils.branch_name import _sanitize_branch_component

        result = _sanitize_branch_component("test!@#$%name")
        assert result == "testname"

    def test_sanitize_preserves_slashes(self):
        """Test that slashes are preserved."""
        from graphite_cli.utils.branch_name import _sanitize_branch_component

        result = _sanitize_branch_component("feature/bugfix")
        assert result == "feature/bugfix"

    def test_sanitize_removes_consecutive_hyphens(self):
        """Test that consecutive hyphens are collapsed."""
        from graphite_cli.utils.branch_name import _sanitize_branch_component

        result = _sanitize_branch_component("test---name")
        assert result == "test-name"

    def test_sanitize_strips_leading_trailing_hyphens(self):
        """Test that leading/trailing hyphens are removed."""
        from graphite_cli.utils.branch_name import _sanitize_branch_component

        result = _sanitize_branch_component("-test-name-")
        assert result == "test-name"

    def test_sanitize_handles_empty_string(self):
        """Test that empty string returns empty string."""
        from graphite_cli.utils.branch_name import _sanitize_branch_component

        result = _sanitize_branch_component("")
        assert result == ""


class TestCleanBranchName:
    """Tests for _clean_branch_name helper function."""

    def test_clean_removes_consecutive_hyphens(self):
        """Test that consecutive hyphens are removed."""
        from graphite_cli.utils.branch_name import _clean_branch_name

        result = _clean_branch_name("test--branch---name")
        assert result == "test-branch-name"

    def test_clean_strips_leading_trailing_chars(self):
        """Test that leading/trailing hyphens and slashes are removed."""
        from graphite_cli.utils.branch_name import _clean_branch_name

        result = _clean_branch_name("-/test/branch/-")
        assert result == "test/branch"

    def test_clean_removes_component_periods(self):
        """Test that leading/trailing periods in components are removed."""
        from graphite_cli.utils.branch_name import _clean_branch_name

        result = _clean_branch_name("feature/.hidden/..test..")
        assert result == "feature/hidden/test"

    def test_clean_handles_empty_result(self):
        """Test handling of string that becomes empty after cleaning."""
        from graphite_cli.utils.branch_name import _clean_branch_name

        result = _clean_branch_name("---///...")
        assert result == ""
