"""PullRequest model for representing GitHub pull requests."""

from datetime import datetime

from pydantic import BaseModel, Field


class PullRequest(BaseModel):
    """Represents a GitHub pull request.

    Attributes:
        number: PR number.
        title: PR title.
        body: PR description.
        url: PR URL.
        state: PR state (open, closed, merged).
        head_branch: Source branch.
        base_branch: Target branch.
        created_at: When PR was created.
        updated_at: When PR was last updated.
        merged_at: When PR was merged (if merged).
        mergeable: Whether PR can be merged.
        checks_passing: Whether all CI checks are passing.
        approved: Whether PR has required approvals.
    """

    number: int = Field(description="PR number")
    title: str = Field(description="PR title")
    body: str = Field(description="PR description")
    url: str = Field(description="PR URL")
    state: str = Field(description="PR state (open, closed, merged)")
    head_branch: str = Field(description="Source branch")
    base_branch: str = Field(description="Target branch")
    created_at: datetime = Field(description="When PR was created")
    updated_at: datetime = Field(description="When PR was last updated")
    merged_at: datetime | None = Field(None, description="When PR was merged (if merged)")
    mergeable: bool = Field(False, description="Whether PR can be merged")
    checks_passing: bool = Field(False, description="Whether all CI checks are passing")
    approved: bool = Field(False, description="Whether PR has required approvals")

    def is_mergeable(self) -> bool:
        """Check if PR can be merged.

        Returns:
            True if PR is open, mergeable, has passing checks, and is approved.
        """
        return self.state == "open" and self.mergeable and self.checks_passing and self.approved
