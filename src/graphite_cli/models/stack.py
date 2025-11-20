"""Stack model for managing collections of related branches."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from graphite_cli.exceptions.base import ValidationException
from graphite_cli.models.branch import Branch


@dataclass
class Stack:
    """Represents a collection of related branches in a stack.

    This model manages a collection of branches that form a dependency tree,
    providing operations for stack manipulation, validation, and traversal.

    Attributes:
        branches: Dictionary mapping branch names to Branch objects.
        trunk: Name of the trunk branch (usually 'main' or 'master').
        created_at: Timestamp when stack was created.
        updated_at: Timestamp when stack was last updated.
    """

    branches: dict[str, Branch] = field(default_factory=dict)
    trunk: str = "main"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def get_branch(self, name: str) -> Branch | None:
        """Get a branch by name.

        Args:
            name: Name of the branch to retrieve.

        Returns:
            Branch object if found, None otherwise.

        Examples:
            >>> stack = Stack()
            >>> stack.add_branch("feature")
            >>> branch = stack.get_branch("feature")
            >>> branch.name
            'feature'

            >>> stack.get_branch("nonexistent") is None
            True
        """
        return self.branches.get(name)

    def add_branch(self, name: str, parent: str | None = None, **kwargs: Any) -> Branch:
        """Add a new branch to the stack.

        Args:
            name: Name of the new branch.
            parent: Name of the parent branch.
            **kwargs: Additional branch attributes.

        Returns:
            The created Branch object.

        Raises:
            ValidationException: If branch already exists or parent not found.

        Examples:
            >>> stack = Stack()
            >>> stack.add_branch("main")
            >>> stack.add_branch("feature", parent="main")
            >>> len(stack.branches)
            2
            >>> stack.branches["feature"].parent
            'main'
        """
        if name in self.branches:
            raise ValidationException(f"Branch '{name}' already exists in stack")

        if parent and parent not in self.branches:
            raise ValidationException(f"Parent branch '{parent}' not found in stack")

        branch = Branch(name=name, parent=parent, **kwargs)
        self.branches[name] = branch
        self.updated_at = datetime.now()

        # Update parent's children set
        if parent and parent in self.branches:
            self.branches[parent].add_child(name)

        return branch

    def remove_branch(self, name: str) -> None:
        """Remove a branch from the stack.

        Args:
            name: Name of the branch to remove.

        Raises:
            ValidationException: If branch not found or has children.

        Examples:
            >>> stack = Stack()
            >>> stack.add_branch("main")
            >>> stack.add_branch("feature", parent="main")
            >>> stack.remove_branch("feature")
            >>> len(stack.branches)
            1
        """
        if name not in self.branches:
            raise ValidationException(f"Branch '{name}' not found in stack")

        branch = self.branches[name]
        
        if branch.children:
            child_list = ", ".join(sorted(branch.children))
            raise ValidationException(
                f"Cannot remove branch '{name}' with children: {child_list}",
                "Remove or move child branches first"
            )

        # Remove from parent's children set
        if branch.parent and branch.parent in self.branches:
            self.branches[branch.parent].remove_child(name)

        del self.branches[name]
        self.updated_at = datetime.now()

    def get_stack_for_branch(self, name: str) -> list[Branch]:
        """Get the complete stack (ancestors + branch + descendants) for a branch.

        Args:
            name: Name of the branch.

        Returns:
            List of Branch objects in the complete stack, ordered from root to leaves.

        Raises:
            ValidationException: If branch not found.

        Examples:
            >>> stack = Stack()
            >>> stack.add_branch("main")
            >>> stack.add_branch("feature1", parent="main")
            >>> stack.add_branch("feature2", parent="feature1")
            >>> branch_stack = stack.get_stack_for_branch("feature1")
            >>> [b.name for b in branch_stack]
            ['main', 'feature1', 'feature2']
        """
        if name not in self.branches:
            raise ValidationException(f"Branch '{name}' not found in stack")

        branch = self.branches[name]
        
        # Get ancestors (from root to branch)
        ancestors = list(reversed(branch.get_ancestors(self)))
        
        # Add the branch itself
        stack_branches = ancestors + [branch]
        
        # Add descendants
        descendants = branch.get_descendants(self)
        stack_branches.extend(descendants)
        
        return stack_branches

    def get_upstack_branches(self, name: str) -> list[Branch]:
        """Get all branches upstack (descendants) from the given branch.

        Args:
            name: Name of the base branch.

        Returns:
            List of Branch objects that are descendants of the given branch.

        Raises:
            ValidationException: If branch not found.

        Examples:
            >>> stack = Stack()
            >>> stack.add_branch("main")
            >>> stack.add_branch("feature1", parent="main")
            >>> stack.add_branch("feature2", parent="feature1")
            >>> upstack = stack.get_upstack_branches("main")
            >>> [b.name for b in upstack]
            ['feature1', 'feature2']
        """
        if name not in self.branches:
            raise ValidationException(f"Branch '{name}' not found in stack")

        return self.branches[name].get_descendants(self)

    def get_downstack_branches(self, name: str) -> list[Branch]:
        """Get all branches downstack (ancestors) from the given branch.

        Args:
            name: Name of the branch.

        Returns:
            List of Branch objects that are ancestors of the given branch.

        Raises:
            ValidationException: If branch not found.

        Examples:
            >>> stack = Stack()
            >>> stack.add_branch("main")
            >>> stack.add_branch("feature1", parent="main")
            >>> stack.add_branch("feature2", parent="feature1")
            >>> downstack = stack.get_downstack_branches("feature2")
            >>> [b.name for b in downstack]
            ['feature1', 'main']
        """
        if name not in self.branches:
            raise ValidationException(f"Branch '{name}' not found in stack")

        return self.branches[name].get_ancestors(self)

    def get_trunk_branches(self) -> list[Branch]:
        """Get all trunk branches (branches with no parent).

        Returns:
            List of Branch objects that have no parent.

        Examples:
            >>> stack = Stack()
            >>> stack.add_branch("main")
            >>> stack.add_branch("develop")
            >>> stack.add_branch("feature", parent="main")
            >>> trunks = stack.get_trunk_branches()
            >>> len(trunks)
            2
            >>> all(b.is_trunk() for b in trunks)
            True
        """
        return [branch for branch in self.branches.values() if branch.is_trunk()]

    def get_leaf_branches(self) -> list[Branch]:
        """Get all leaf branches (branches with no children).

        Returns:
            List of Branch objects that have no children.

        Examples:
            >>> stack = Stack()
            >>> stack.add_branch("main")
            >>> stack.add_branch("feature1", parent="main")
            >>> stack.add_branch("feature2", parent="main")
            >>> leaves = stack.get_leaf_branches()
            >>> len(leaves)
            2
            >>> all(not b.children for b in leaves)
            True
        """
        return [branch for branch in self.branches.values() if not branch.children]

    def validate_no_cycles(self) -> None:
        """Validate that the stack contains no cycles.

        Raises:
            ValidationException: If a cycle is detected in the stack.

        Examples:
            >>> stack = Stack()
            >>> stack.add_branch("main")
            >>> stack.add_branch("feature", parent="main")
            >>> stack.validate_no_cycles()  # Should not raise

            >>> # This would create a cycle (if allowed):
            >>> # stack.branches["main"].parent = "feature"
            >>> # stack.validate_no_cycles()  # Would raise ValidationException
        """
        visited = set()
        rec_stack = set()
        
        def has_cycle(branch_name: str) -> bool:
            if branch_name in rec_stack:
                return True
            if branch_name in visited:
                return False
                
            visited.add(branch_name)
            rec_stack.add(branch_name)
            
            if branch_name in self.branches:
                branch = self.branches[branch_name]
                for child_name in branch.children:
                    if has_cycle(child_name):
                        return True
            
            rec_stack.remove(branch_name)
            return False
        
        for branch_name in self.branches:
            if branch_name not in visited:
                if has_cycle(branch_name):
                    raise ValidationException(
                        f"Cycle detected in stack involving branch '{branch_name}'",
                        "Check branch parent-child relationships for circular dependencies"
                    )

    def get_branch_count(self) -> int:
        """Get the total number of branches in the stack.

        Returns:
            Number of branches in the stack.

        Examples:
            >>> stack = Stack()
            >>> stack.add_branch("main")
            >>> stack.add_branch("feature", parent="main")
            >>> stack.get_branch_count()
            2
        """
        return len(self.branches)

    def get_max_depth(self) -> int:
        """Get the maximum depth in the stack.

        Returns:
            Maximum depth of any branch in the stack.

        Examples:
            >>> stack = Stack()
            >>> stack.add_branch("main")
            >>> stack.add_branch("feature1", parent="main")
            >>> stack.add_branch("feature2", parent="feature1")
            >>> stack.get_max_depth()
            2
        """
        if not self.branches:
            return 0
        return max(branch.get_depth(self) for branch in self.branches.values())

    def to_dict(self) -> dict[str, Any]:
        """Convert stack to dictionary for serialization.

        Returns:
            Dictionary representation of the stack.

        Examples:
            >>> stack = Stack()
            >>> stack.add_branch("main")
            >>> data = stack.to_dict()
            >>> data["trunk"]
            'main'
            >>> "main" in data["branches"]
            True
        """
        return {
            "branches": {name: branch.to_dict() for name, branch in self.branches.items()},
            "trunk": self.trunk,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Stack:
        """Create stack from dictionary.

        Args:
            data: Dictionary containing stack data.

        Returns:
            Stack instance created from the data.

        Examples:
            >>> data = {
            ...     "branches": {
            ...         "main": {"name": "main", "created_at": "2024-01-01T12:00:00"},
            ...         "feature": {"name": "feature", "parent": "main", "created_at": "2024-01-01T12:00:00"}
            ...     },
            ...     "trunk": "main",
            ...     "created_at": "2024-01-01T12:00:00",
            ...     "updated_at": "2024-01-01T12:00:00"
            ... }
            >>> stack = Stack.from_dict(data)
            >>> stack.trunk
            'main'
            >>> len(stack.branches)
            2
        """
        branches = {}
        for name, branch_data in data.get("branches", {}).items():
            branches[name] = Branch.from_dict(branch_data)

        return cls(
            branches=branches,
            trunk=data.get("trunk", "main"),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat())),
        )

    def __str__(self) -> str:
        """Return string representation of the stack."""
        count = len(self.branches)
        trunk_count = len(self.get_trunk_branches())
        max_depth = self.get_max_depth()
        return f"Stack with {count} branches, {trunk_count} trunks, max depth {max_depth}"

    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        branch_names = sorted(self.branches.keys())
        return f"Stack(branches={branch_names}, trunk='{self.trunk}')"