"""Branch model for Git branch metadata and relationships."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from graphite_cli.models.stack import Stack


@dataclass
class Branch:
    """Represents a Git branch with Graphite metadata.

    This model encapsulates a Git branch along with its metadata for stack
    management, including parent-child relationships, PR associations, and
    timestamps.

    Attributes:
        name: Git branch name.
        parent: Name of the parent branch (None for trunk branches).
        pr_number: GitHub PR number if submitted (None if not submitted).
        created_at: Timestamp when branch was created in Graphite.
        updated_at: Timestamp when branch metadata was last updated.
        commit_hash: Current commit hash of the branch.
        description: Branch description/commit message.
        children: Set of child branch names that depend on this branch.
    """

    name: str
    parent: str | None = None
    pr_number: int | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    commit_hash: str = ""
    description: str = ""
    children: set[str] = field(default_factory=set)

    def is_submitted(self) -> bool:
        """Check if branch has been submitted as a PR.

        Returns:
            True if the branch has an associated PR number, False otherwise.

        Examples:
            >>> branch = Branch(name="feature", pr_number=123)
            >>> branch.is_submitted()
            True

            >>> branch = Branch(name="feature")
            >>> branch.is_submitted()
            False
        """
        return self.pr_number is not None

    def is_trunk(self) -> bool:
        """Check if this is a trunk branch (no parent).

        Returns:
            True if the branch has no parent, False otherwise.

        Examples:
            >>> branch = Branch(name="main")
            >>> branch.is_trunk()
            True

            >>> branch = Branch(name="feature", parent="main")
            >>> branch.is_trunk()
            False
        """
        return self.parent is None

    def add_child(self, child_name: str) -> None:
        """Add a child branch to this branch.

        Args:
            child_name: Name of the child branch to add.

        Examples:
            >>> parent = Branch(name="main")
            >>> parent.add_child("feature")
            >>> "feature" in parent.children
            True
        """
        self.children.add(child_name)
        self.updated_at = datetime.now()

    def remove_child(self, child_name: str) -> None:
        """Remove a child branch from this branch.

        Args:
            child_name: Name of the child branch to remove.

        Examples:
            >>> parent = Branch(name="main", children={"feature"})
            >>> parent.remove_child("feature")
            >>> len(parent.children)
            0
        """
        self.children.discard(child_name)
        self.updated_at = datetime.now()

    def get_children(self, stack: Stack) -> list[Branch]:
        """Get all child branches from the stack.

        Args:
            stack: The stack containing all branches.

        Returns:
            List of child Branch objects, sorted by creation time.

        Examples:
            >>> from graphite_cli.models.stack import Stack
            >>> parent = Branch(name="main", children={"feature1", "feature2"})
            >>> child1 = Branch(name="feature1", parent="main")
            >>> child2 = Branch(name="feature2", parent="main")
            >>> stack = Stack(branches={"main": parent, "feature1": child1, "feature2": child2})
            >>> children = parent.get_children(stack)
            >>> len(children)
            2
            >>> all(child.parent == "main" for child in children)
            True
        """
        children = []
        for child_name in self.children:
            if child_name in stack.branches:
                children.append(stack.branches[child_name])
        
        # Sort by creation time
        return sorted(children, key=lambda b: b.created_at)

    def get_ancestors(self, stack: Stack) -> list[Branch]:
        """Get all ancestor branches from the stack.

        Args:
            stack: The stack containing all branches.

        Returns:
            List of ancestor Branch objects, from immediate parent to root.

        Examples:
            >>> from graphite_cli.models.stack import Stack
            >>> root = Branch(name="main")
            >>> parent = Branch(name="feature1", parent="main")
            >>> child = Branch(name="feature2", parent="feature1")
            >>> stack = Stack(branches={"main": root, "feature1": parent, "feature2": child})
            >>> ancestors = child.get_ancestors(stack)
            >>> [b.name for b in ancestors]
            ['feature1', 'main']
        """
        ancestors = []
        current_parent = self.parent
        
        while current_parent and current_parent in stack.branches:
            parent_branch = stack.branches[current_parent]
            ancestors.append(parent_branch)
            current_parent = parent_branch.parent
            
        return ancestors

    def get_descendants(self, stack: Stack) -> list[Branch]:
        """Get all descendant branches from the stack.

        Args:
            stack: The stack containing all branches.

        Returns:
            List of all descendant Branch objects in depth-first order.

        Examples:
            >>> from graphite_cli.models.stack import Stack
            >>> root = Branch(name="main", children={"feature1"})
            >>> child1 = Branch(name="feature1", parent="main", children={"feature2"})
            >>> child2 = Branch(name="feature2", parent="feature1")
            >>> stack = Stack(branches={"main": root, "feature1": child1, "feature2": child2})
            >>> descendants = root.get_descendants(stack)
            >>> [b.name for b in descendants]
            ['feature1', 'feature2']
        """
        descendants = []
        
        def collect_descendants(branch: Branch) -> None:
            for child in branch.get_children(stack):
                descendants.append(child)
                collect_descendants(child)
        
        collect_descendants(self)
        return descendants

    def get_depth(self, stack: Stack) -> int:
        """Get the depth of this branch in the stack.

        Args:
            stack: The stack containing all branches.

        Returns:
            Depth of the branch (0 for trunk, 1 for immediate children, etc.).

        Examples:
            >>> from graphite_cli.models.stack import Stack
            >>> root = Branch(name="main")
            >>> child = Branch(name="feature", parent="main")
            >>> stack = Stack(branches={"main": root, "feature": child})
            >>> root.get_depth(stack)
            0
            >>> child.get_depth(stack)
            1
        """
        return len(self.get_ancestors(stack))

    def update_metadata(self, commit_hash: str = "", description: str = "") -> None:
        """Update branch metadata.

        Args:
            commit_hash: New commit hash.
            description: New description.

        Examples:
            >>> branch = Branch(name="feature")
            >>> branch.update_metadata(commit_hash="abc123", description="Add feature")
            >>> branch.commit_hash
            'abc123'
            >>> branch.description
            'Add feature'
        """
        if commit_hash:
            self.commit_hash = commit_hash
        if description:
            self.description = description
        self.updated_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert branch to dictionary for serialization.

        Returns:
            Dictionary representation of the branch.

        Examples:
            >>> branch = Branch(name="feature", parent="main", pr_number=123)
            >>> data = branch.to_dict()
            >>> data["name"]
            'feature'
            >>> data["parent"]
            'main'
            >>> data["pr_number"]
            123
        """
        return {
            "name": self.name,
            "parent": self.parent,
            "pr_number": self.pr_number,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "commit_hash": self.commit_hash,
            "description": self.description,
            "children": list(self.children),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Branch:
        """Create branch from dictionary.

        Args:
            data: Dictionary containing branch data.

        Returns:
            Branch instance created from the data.

        Examples:
            >>> data = {
            ...     "name": "feature",
            ...     "parent": "main",
            ...     "pr_number": 123,
            ...     "created_at": "2024-01-01T12:00:00",
            ...     "updated_at": "2024-01-01T12:00:00",
            ...     "commit_hash": "abc123",
            ...     "description": "Add feature",
            ...     "children": ["child1", "child2"]
            ... }
            >>> branch = Branch.from_dict(data)
            >>> branch.name
            'feature'
            >>> branch.pr_number
            123
        """
        return cls(
            name=data["name"],
            parent=data.get("parent"),
            pr_number=data.get("pr_number"),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat())),
            commit_hash=data.get("commit_hash", ""),
            description=data.get("description", ""),
            children=set(data.get("children", [])),
        )

    def __str__(self) -> str:
        """Return string representation of the branch."""
        status = "submitted" if self.is_submitted() else "not submitted"
        parent_info = f" (parent: {self.parent})" if self.parent else " (trunk)"
        return f"Branch '{self.name}'{parent_info} - {status}"

    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        return (
            f"Branch(name='{self.name}', parent='{self.parent}', "
            f"pr_number={self.pr_number}, children={self.children})"
        )