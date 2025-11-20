"""Branch name generation utilities.

This module provides functions for generating branch names based on templates
and validating branch name formats according to Git ref naming rules.
"""

import os
import re
from datetime import datetime


def generate_branch_name(
    description: str,
    *,
    prefix: str = "",
    template: str = "{prefix}{date}_{username}_{description}",
    date_format: str = "%Y%m%d",
    username: str | None = None,
) -> str:
    """Generate a branch name from a template string.

    Args:
        description: Brief description for the branch (will be sanitized).
        prefix: Optional prefix for the branch name.
        template: Template string with placeholders:
            - {prefix}: Branch prefix
            - {date}: Current date
            - {username}: System username
            - {description}: Branch description
        date_format: strftime format string for date formatting.
        username: Override username (defaults to system username).

    Returns:
        Generated branch name with all placeholders replaced and sanitized.

    Raises:
        ValueError: If description is empty or results in empty branch name.

    Examples:
        >>> generate_branch_name("fix login bug", prefix="feature/")
        'feature/20240115_john_fix-login-bug'
        >>> generate_branch_name("add tests", template="{description}")
        'add-tests'
    """
    if not description or not description.strip():
        msg = "Description cannot be empty"
        raise ValueError(msg)

    # Get current date
    current_date = datetime.now().strftime(date_format)  # noqa: DTZ005

    # Get username
    if username is None:
        username = os.environ.get("USER") or os.environ.get("USERNAME") or "user"

    # Sanitize components
    sanitized_prefix = _sanitize_branch_component(prefix)
    sanitized_username = _sanitize_branch_component(username)
    sanitized_description = _sanitize_branch_component(description)

    # Replace placeholders in template
    branch_name = template.format(
        prefix=sanitized_prefix,
        date=current_date,
        username=sanitized_username,
        description=sanitized_description,
    )

    # Clean up the final branch name
    branch_name = _clean_branch_name(branch_name)

    if not branch_name:
        msg = "Generated branch name is empty after sanitization"
        raise ValueError(msg)

    return branch_name


def _sanitize_branch_component(component: str) -> str:
    """Sanitize a branch name component.

    Converts to lowercase, replaces spaces and special characters with hyphens,
    and removes consecutive hyphens.

    Args:
        component: Component string to sanitize.

    Returns:
        Sanitized component string.
    """
    if not component:
        return ""

    # Convert to lowercase
    component = component.lower()

    # Replace spaces and underscores with hyphens
    component = component.replace(" ", "-").replace("_", "-")

    # Remove characters that aren't alphanumeric, hyphens, or slashes
    component = re.sub(r"[^a-z0-9\-/]", "", component)

    # Remove consecutive hyphens
    component = re.sub(r"-+", "-", component)

    # Remove leading/trailing hyphens (but keep slashes)
    return component.strip("-")


def _clean_branch_name(branch_name: str) -> str:
    """Clean up a generated branch name.

    Removes consecutive hyphens, leading/trailing hyphens and slashes,
    and ensures the name follows Git ref naming rules.

    Args:
        branch_name: Branch name to clean.

    Returns:
        Cleaned branch name.
    """
    # Remove consecutive hyphens
    branch_name = re.sub(r"-+", "-", branch_name)

    # Remove leading/trailing hyphens and slashes
    branch_name = branch_name.strip("-/")

    # Ensure no component starts or ends with a period
    parts = branch_name.split("/")
    parts = [p.strip(".") for p in parts if p.strip(".")]
    return "/".join(parts)


def validate_branch_name(name: str) -> None:
    """Validate a branch name according to Git ref naming rules.

    Args:
        name: Branch name to validate.

    Raises:
        ValueError: If the branch name is invalid.

    Examples:
        >>> validate_branch_name("feature/my-branch")  # OK
        >>> validate_branch_name("")  # Raises ValueError
        >>> validate_branch_name("branch..name")  # Raises ValueError
    """
    if not name:
        msg = "Branch name cannot be empty"
        raise ValueError(msg)

    # Check for invalid patterns
    invalid_patterns = [
        (r"^-", "Branch name cannot start with a hyphen"),
        (r"-$", "Branch name cannot end with a hyphen"),
        (r"\.\.", "Branch name cannot contain consecutive periods"),
        (r"^/", "Branch name cannot start with a slash"),
        (r"/$", "Branch name cannot end with a slash"),
        (r"//", "Branch name cannot contain consecutive slashes"),
        (r"@\{", "Branch name cannot contain '@{'"),
        (r"[\x00-\x1f\x7f]", "Branch name cannot contain control characters"),
        (r"[ ~^:?*\[]", "Branch name cannot contain spaces or special characters: ~^:?*["),
    ]

    for pattern, error_msg in invalid_patterns:
        if re.search(pattern, name):
            raise ValueError(error_msg)

    # Check for invalid names
    if name in {"@", "."}:
        msg = f"Branch name cannot be '{name}'"
        raise ValueError(msg)

    # Check that each component doesn't start with a period
    for part in name.split("/"):
        if part.startswith("."):
            msg = "Branch name components cannot start with a period"
            raise ValueError(msg)


def format_branch_description(description: str, max_length: int = 50) -> str:
    """Format a branch description by truncating and sanitizing.

    Args:
        description: Raw description string.
        max_length: Maximum length for the description component.

    Returns:
        Formatted and truncated description.

    Examples:
        >>> format_branch_description("This is a very long description", max_length=10)
        'this-is-a'
        >>> format_branch_description("Fix Bug #123")
        'fix-bug-123'
    """
    # Sanitize first
    sanitized = _sanitize_branch_component(description)

    # Truncate if needed
    if len(sanitized) > max_length:
        # Try to break at a hyphen if possible
        truncated = sanitized[:max_length]
        last_hyphen = truncated.rfind("-")
        # Only break at hyphen if we keep at least half
        sanitized = truncated[:last_hyphen] if last_hyphen > max_length // 2 else truncated

    return sanitized.rstrip("-")


def parse_template(template: str) -> list[str]:
    """Parse a template string and extract placeholder names.

    Args:
        template: Template string with placeholders like {prefix}, {date}, etc.

    Returns:
        List of placeholder names found in the template.

    Examples:
        >>> parse_template("{prefix}{date}_{username}")
        ['prefix', 'date', 'username']
        >>> parse_template("static-branch-name")
        []
    """
    return re.findall(r"\{([^}]+)\}", template)


def validate_template(template: str) -> None:
    """Validate a branch name template.

    Args:
        template: Template string to validate.

    Raises:
        ValueError: If the template contains invalid placeholders.

    Examples:
        >>> validate_template("{prefix}{date}_{description}")  # OK
        >>> validate_template("{invalid_placeholder}")  # Raises ValueError
    """
    valid_placeholders = {"prefix", "date", "username", "description"}
    placeholders = parse_template(template)

    invalid = set(placeholders) - valid_placeholders
    if invalid:
        msg = f"Invalid template placeholders: {', '.join(sorted(invalid))}"
        raise ValueError(msg)
