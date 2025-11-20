"""Branch model for Graphite CLI.

This module defines the Branch dataclass that represents a Git branch
with Graphite metadata including parent relationships, PR associations,
and timestamps.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field, field_validator

if TYPE_CHECKING:
    from graphite_cli.models.stack import Stack


class Branch(BaseModel):
    """Represents a Git branch with Graphite metadata.

    Attributes:
        name: Branch name (must be valid Git ref).
        commit_sha: Current commit SHA.
        parent_branch: Name of parent branch in stack (None for trunk-based branches).
        pr_number: Associated PR number if submitted.
        pr_url: Associated PR URL if submitted.
        created_at: When branch was created in Graphite.
        updated_at: When branch was last modified.
        is_tracked: Whether branch is tracked by Graphite.
        custom_metadata: Additional user-defined metadata.
    """

    name: str = Field(description="Branch name")
    commit_sha: str = Field(description="Current commit SHA")
    parent_branch: str | None = Field(None, description="Name of parent branch in stack")
    pr_number: int | None = Field(None, description="Associated PR number if submitted")
    pr_url: str | None = Field(None, description="Associated PR URL if submitted")
    created_at: datetime = Field(description="When branch was created in Graphite")
    updated_at: datetime = Field(description="When branch was last modified")
    is_tracked: bool = Field(True, description="Whether branch is tracked by Graphite")
    custom_metadata: dict[str, str] = Field(
        default_factory=dict, description="Additional user-defined metadata"
    )

    @field_validator("name")
    @classmethod
    def validate_branch_name(cls, v: str) -> str:
        """Validate branch name follows Git ref naming rules.

        Args:
            v: The branch name to validate.

        Returns:
            The validated branch name.

        Raises:
            ValueError: If branch name is empty or starts with '-'.
        """
        if not v or v.startswith("-"):
            msg = "Branch name cannot be empty or start with '-'"
            raise ValueError(msg)
        return v

    @field_validator("commit_sha")
    @classmethod
    def validate_commit_sha(cls, v: str) -> str:
        """Validate commit SHA is not empty.

        Args:
            v: The commit SHA to validate.

        Returns:
            The validated commit SHA.

        Raises:
            ValueError: If commit SHA is empty.
        """
        if not v:
            msg = "Commit SHA cannot be empty"
            raise ValueError(msg)
        return v

    def is_submitted(self) -> bool:
        """Check if branch has been submitted as PR.

        Returns:
            True if branch has an associated PR number, False otherwise.
        """
        return self.pr_number is not None

    def get_children(self, stack: "Stack") -> list["Branch"]:
        """Get all child branches in stack.

        Args:
            stack: The stack containing this branch and its children.

        Returns:
            List of branches that have this branch as their parent.
        """
        return [b for b in stack.branches if b.parent_branch == self.name]

    def get_ancestors(self, stack: "Stack") -> list["Branch"]:
        """Get all ancestor branches up to trunk.

        Args:
            stack: The stack containing this branch and its ancestors.

        Returns:
            List of ancestor branches from immediate parent to trunk,
            in order from closest to farthest.
        """
        ancestors: list[Branch] = []
        current = self

        while current.parent_branch:
            parent = stack.get_branch(current.parent_branch)
            if parent:
                ancestors.append(parent)
                current = parent
            else:
                # Parent not found in stack, break to prevent infinite loop
                break

        return ancestors
