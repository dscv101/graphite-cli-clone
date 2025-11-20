# Graphite CLI Clone - Technical Design Document

## Executive Summary

This document provides the detailed technical design for implementing a Python-based clone of the Graphite CLI tool. Following Sean Grove's "The New Code" methodology, this design translates the requirements specification into concrete implementation details, architectural patterns, and technical decisions that will guide development.

## Design Philosophy

### Core Principles

1. **Specification-Driven**: Code follows explicit specifications, enabling AI agents and developers to implement with clarity
2. **Simplicity First**: Prefer straightforward solutions over clever abstractions
3. **Type Safety**: Leverage Python 3.14+ type hints for compile-time safety
4. **Performance Conscious**: Design with performance implications in mind from the start
5. **Security First**: Build security into the architecture, not as an afterthought
6. **Testability**: Every component designed for isolated testing

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Entry Point                         │
│                    (main.py / gt)                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Command Router                            │
│              (typer application)                            │
└────┬────────┬────────┬────────┬────────┬───────────────────┘
     │        │        │        │        │
     ▼        ▼        ▼        ▼        ▼
┌─────────┬─────────┬─────────┬─────────┬─────────────────┐
│ Create  │ Submit  │ Modify  │  Sync   │ Navigation &    │
│ Command │ Command │ Command │ Command │ Other Commands  │
└────┬────┴────┬────┴────┬────┴────┬────┴────┬────────────┘
     │         │         │         │         │
     └─────────┴─────────┴─────────┴─────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Core Services Layer                        │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ Stack        │  │ Git          │  │ GitHub          │  │
│  │ Manager      │  │ Service      │  │ Service         │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ Config       │  │ State        │  │ Validation      │  │
│  │ Manager      │  │ Manager      │  │ Service         │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Layer                                │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ Repository   │  │ File System  │  │ Keyring         │  │
│  │ (Git)        │  │ (.graphite/) │  │ (Credentials)   │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

#### CLI Layer
- **Purpose**: Handle user interaction and command routing
- **Technology**: Typer framework
- **Responsibilities**:
  - Parse command-line arguments and options
  - Validate user input
  - Route commands to appropriate handlers
  - Format and display output using Rich
  - Handle errors and present user-friendly messages

#### Core Services Layer
- **Purpose**: Implement business logic and orchestrate operations
- **Components**:
  - **Stack Manager**: Manages stack state, relationships, and operations
  - **Git Service**: Abstracts Git operations
  - **GitHub Service**: Handles GitHub API interactions
  - **Config Manager**: Manages configuration
  - **State Manager**: Persists and retrieves local state
  - **Validation Service**: Validates operations and state

#### Data Layer
- **Purpose**: Provide data persistence and retrieval
- **Components**:
  - Git repository (via GitPython)
  - File system storage (.graphite/ directory)
  - System keyring (via keyring library)

## Module Structure

### Project Directory Layout

```
graphite-cli-clone/
├── src/
│   └── graphite_cli/
│       ├── __init__.py
│       ├── __main__.py              # Entry point
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── app.py               # Typer app definition
│       │   ├── commands/
│       │   │   ├── __init__.py
│       │   │   ├── create.py        # gt create command
│       │   │   ├── submit.py        # gt submit command
│       │   │   ├── modify.py        # gt modify command
│       │   │   ├── sync.py          # gt sync command
│       │   │   ├── navigation.py    # log, up, down, etc.
│       │   │   ├── manipulation.py  # rename, delete, etc.
│       │   │   ├── collaboration.py # get, track, etc.
│       │   │   ├── config.py        # init, auth, config
│       │   │   └── merge.py         # merge command
│       │   └── output/
│       │       ├── __init__.py
│       │       ├── formatter.py     # Output formatting
│       │       └── renderer.py      # Rich rendering
│       ├── core/
│       │   ├── __init__.py
│       │   ├── stack_manager.py     # Stack operations
│       │   ├── git_service.py       # Git operations
│       │   ├── github_service.py    # GitHub API
│       │   ├── config_manager.py    # Configuration
│       │   ├── state_manager.py     # State persistence
│       │   └── validator.py         # Validation logic
│       ├── models/
│       │   ├── __init__.py
│       │   ├── branch.py            # Branch model
│       │   ├── stack.py             # Stack model
│       │   ├── repository.py        # Repository model
│       │   ├── config.py            # Config model
│       │   └── pull_request.py      # PR model
│       ├── exceptions/
│       │   ├── __init__.py
│       │   ├── base.py              # Base exceptions
│       │   ├── git_errors.py        # Git exceptions
│       │   ├── github_errors.py     # GitHub exceptions
│       │   └── validation_errors.py # Validation exceptions
│       └── utils/
│           ├── __init__.py
│           ├── git_utils.py         # Git utilities
│           ├── branch_name.py       # Branch naming
│           └── logging.py           # Logging setup
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_stack_manager.py
│   │   ├── test_git_service.py
│   │   ├── test_github_service.py
│   │   └── ...
│   ├── integration/
│   │   ├── test_git_operations.py
│   │   ├── test_github_api.py
│   │   └── ...
│   └── e2e/
│       ├── test_create_workflow.py
│       ├── test_submit_workflow.py
│       └── ...
├── docs/
│   ├── installation.md
│   ├── quickstart.md
│   ├── commands.md
│   └── ...
├── pyproject.toml                   # Project config (Hatch)
├── requirements.md                  # Requirements spec
├── design.md                        # This document
├── README.md
├── CHANGELOG.md
└── LICENSE
```

## Data Models

### Branch Model

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Branch:
    """Represents a Git branch with Graphite metadata."""
    
    name: str
    """Branch name."""
    
    commit_sha: str
    """Current commit SHA."""
    
    parent_branch: Optional[str]
    """Name of parent branch in stack (None for trunk-based branches)."""
    
    pr_number: Optional[int]
    """Associated PR number if submitted."""
    
    pr_url: Optional[str]
    """Associated PR URL if submitted."""
    
    created_at: datetime
    """When branch was created in Graphite."""
    
    updated_at: datetime
    """When branch was last modified."""
    
    is_tracked: bool = True
    """Whether branch is tracked by Graphite."""
    
    custom_metadata: dict[str, str] = None
    """Additional user-defined metadata."""
    
    def is_submitted(self) -> bool:
        """Check if branch has been submitted as PR."""
        return self.pr_number is not None
    
    def get_children(self, stack: 'Stack') -> list['Branch']:
        """Get all child branches in stack."""
        return [b for b in stack.branches if b.parent_branch == self.name]
    
    def get_ancestors(self, stack: 'Stack') -> list['Branch']:
        """Get all ancestor branches up to trunk."""
        ancestors = []
        current = self
        while current.parent_branch:
            parent = stack.get_branch(current.parent_branch)
            if parent:
                ancestors.append(parent)
                current = parent
            else:
                break
        return ancestors
```

### Stack Model

```python
from dataclasses import dataclass
from typing import Optional


@dataclass
class Stack:
    """Represents a series of related branches."""
    
    trunk_branch: str
    """Name of trunk branch (e.g., 'main')."""
    
    branches: list[Branch]
    """All branches in repository tracked by Graphite."""
    
    current_branch: str
    """Currently checked out branch."""
    
    def get_branch(self, name: str) -> Optional[Branch]:
        """Get branch by name."""
        return next((b for b in self.branches if b.name == name), None)
    
    def get_stack_for_branch(self, branch_name: str) -> list[Branch]:
        """Get complete stack from trunk to specified branch."""
        branch = self.get_branch(branch_name)
        if not branch:
            return []
        
        stack = [branch]
        current = branch
        
        # Walk up to trunk
        while current.parent_branch:
            parent = self.get_branch(current.parent_branch)
            if parent:
                stack.insert(0, parent)
                current = parent
            else:
                break
        
        return stack
    
    def get_upstack_branches(self, branch_name: str) -> list[Branch]:
        """Get all branches upstack from specified branch."""
        result = []
        
        def collect_children(name: str) -> None:
            children = [b for b in self.branches if b.parent_branch == name]
            for child in children:
                result.append(child)
                collect_children(child.name)
        
        collect_children(branch_name)
        return result
    
    def get_downstack_branches(self, branch_name: str) -> list[Branch]:
        """Get all branches downstack to trunk from specified branch."""
        branch = self.get_branch(branch_name)
        if not branch:
            return []
        
        return branch.get_ancestors(self)
    
    def validate_no_cycles(self) -> bool:
        """Ensure no circular dependencies exist in stack."""
        visited = set()
        
        def has_cycle(branch_name: str, path: set[str]) -> bool:
            if branch_name in path:
                return True
            if branch_name in visited:
                return False
            
            visited.add(branch_name)
            path.add(branch_name)
            
            branch = self.get_branch(branch_name)
            if branch and branch.parent_branch:
                if has_cycle(branch.parent_branch, path):
                    return True
            
            path.remove(branch_name)
            return False
        
        for branch in self.branches:
            if has_cycle(branch.name, set()):
                return False
        
        return True
```

### Repository Model

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Repository:
    """Represents Git repository state."""
    
    path: Path
    """Path to repository root."""
    
    remote_url: str
    """URL of remote repository."""
    
    remote_name: str = "origin"
    """Name of remote (default: origin)."""
    
    owner: str = ""
    """Repository owner (parsed from remote URL)."""
    
    name: str = ""
    """Repository name (parsed from remote URL)."""
    
    def is_github_repo(self) -> bool:
        """Check if repository is hosted on GitHub."""
        return "github.com" in self.remote_url
    
    def get_github_repo_path(self) -> str:
        """Get GitHub repo path (owner/name)."""
        return f"{self.owner}/{self.name}"
```

### Config Model

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class GraphiteConfig:
    """Graphite configuration."""
    
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
    merge_method: str = "squash"  # merge, squash, rebase
    
    # GitHub
    github_token: Optional[str] = None
    
    # UI
    use_colors: bool = True
    use_emoji: bool = True
    show_pr_status: bool = True
    
    # Advanced
    log_level: str = "INFO"
    cache_github_data: bool = True
    cache_ttl_seconds: int = 300
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        valid_merge_methods = {"merge", "squash", "rebase"}
        if self.merge_method not in valid_merge_methods:
            raise ValueError(
                f"Invalid merge_method: {self.merge_method}. "
                f"Must be one of {valid_merge_methods}"
            )
```

### PullRequest Model

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PullRequest:
    """Represents a GitHub pull request."""
    
    number: int
    """PR number."""
    
    title: str
    """PR title."""
    
    body: str
    """PR description."""
    
    url: str
    """PR URL."""
    
    state: str
    """PR state (open, closed, merged)."""
    
    head_branch: str
    """Source branch."""
    
    base_branch: str
    """Target branch."""
    
    created_at: datetime
    """When PR was created."""
    
    updated_at: datetime
    """When PR was last updated."""
    
    merged_at: Optional[datetime]
    """When PR was merged (if merged)."""
    
    mergeable: bool = False
    """Whether PR can be merged."""
    
    checks_passing: bool = False
    """Whether all CI checks are passing."""
    
    approved: bool = False
    """Whether PR has required approvals."""
    
    def is_mergeable(self) -> bool:
        """Check if PR can be merged."""
        return (
            self.state == "open" and
            self.mergeable and
            self.checks_passing and
            self.approved
        )
```

## Core Services

### Stack Manager

**Purpose**: Manage stack state and orchestrate stack operations.

**Key Methods**:

```python
class StackManager:
    """Manages stack state and operations."""
    
    def __init__(
        self,
        git_service: GitService,
        state_manager: StateManager,
        validator: Validator,
    ) -> None:
        self.git = git_service
        self.state = state_manager
        self.validator = validator
    
    def load_stack(self) -> Stack:
        """Load current stack state from disk and git."""
        pass
    
    def save_stack(self, stack: Stack) -> None:
        """Persist stack state to disk."""
        pass
    
    def create_branch(
        self,
        name: Optional[str],
        parent: Optional[str],
        commit_message: Optional[str],
        stage_all: bool,
    ) -> Branch:
        """Create new branch in stack."""
        pass
    
    def restack_branch(self, branch_name: str) -> None:
        """Rebase branch onto its parent."""
        pass
    
    def restack_upstack(self, branch_name: str) -> None:
        """Rebase all upstack branches."""
        pass
    
    def delete_branch(self, branch_name: str, force: bool = False) -> None:
        """Delete branch and update stack."""
        pass
    
    def move_branch(
        self,
        branch_name: str,
        new_parent: str,
    ) -> None:
        """Move branch to new position in stack."""
        pass
    
    def validate_stack(self, stack: Stack) -> list[str]:
        """Validate stack integrity and return errors."""
        pass
```

### Git Service

**Purpose**: Abstract Git operations and provide clean API.

**Key Methods**:

```python
class GitService:
    """Abstracts Git operations."""
    
    def __init__(self, repo_path: Path) -> None:
        self.repo_path = repo_path
        self.repo = git.Repo(repo_path)
    
    def get_current_branch(self) -> str:
        """Get name of current branch."""
        pass
    
    def create_branch(self, name: str, start_point: str = "HEAD") -> None:
        """Create new branch."""
        pass
    
    def checkout_branch(self, name: str) -> None:
        """Checkout branch."""
        pass
    
    def delete_branch(self, name: str, force: bool = False) -> None:
        """Delete branch."""
        pass
    
    def commit(
        self,
        message: str,
        all_files: bool = False,
        amend: bool = False,
    ) -> str:
        """Create commit and return SHA."""
        pass
    
    def rebase(
        self,
        branch: str,
        onto: str,
        interactive: bool = False,
    ) -> None:
        """Rebase branch onto another."""
        pass
    
    def push(
        self,
        branch: str,
        remote: str = "origin",
        force: bool = False,
    ) -> None:
        """Push branch to remote."""
        pass
    
    def fetch(self, remote: str = "origin") -> None:
        """Fetch from remote."""
        pass
    
    def pull(self, branch: str, remote: str = "origin") -> None:
        """Pull branch from remote."""
        pass
    
    def get_merge_base(self, branch1: str, branch2: str) -> str:
        """Get common ancestor SHA."""
        pass
    
    def has_uncommitted_changes(self) -> bool:
        """Check for uncommitted changes."""
        pass
    
    def is_in_conflict(self) -> bool:
        """Check if repository is in conflict state."""
        pass
    
    def get_commit_message(self, sha: str = "HEAD") -> str:
        """Get commit message for SHA."""
        pass
    
    def get_commits_between(
        self,
        base: str,
        head: str,
    ) -> list[dict[str, str]]:
        """Get commits between two refs."""
        pass
```

### GitHub Service

**Purpose**: Handle all GitHub API interactions.

**Key Methods**:

```python
class GitHubService:
    """Handles GitHub API operations."""
    
    def __init__(self, token: str, owner: str, repo: str) -> None:
        self.github = Github(token)
        self.owner = owner
        self.repo = repo
        self._repo = self.github.get_repo(f"{owner}/{repo}")
        self._cache: dict[str, tuple[datetime, Any]] = {}
    
    def create_pull_request(
        self,
        title: str,
        body: str,
        head: str,
        base: str,
    ) -> PullRequest:
        """Create new pull request."""
        pass
    
    def update_pull_request(
        self,
        pr_number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
    ) -> PullRequest:
        """Update existing pull request."""
        pass
    
    def get_pull_request(self, pr_number: int) -> PullRequest:
        """Get pull request by number."""
        pass
    
    def list_pull_requests(
        self,
        state: str = "open",
    ) -> list[PullRequest]:
        """List pull requests."""
        pass
    
    def merge_pull_request(
        self,
        pr_number: int,
        merge_method: str = "squash",
    ) -> None:
        """Merge pull request."""
        pass
    
    def get_pr_for_branch(self, branch: str) -> Optional[PullRequest]:
        """Get PR associated with branch."""
        pass
    
    def check_pr_status(self, pr_number: int) -> dict[str, bool]:
        """Check PR mergability, CI status, approvals."""
        pass
    
    def authenticate(self, token: str) -> bool:
        """Verify GitHub token is valid."""
        pass
    
    def _get_cached(
        self,
        key: str,
        ttl_seconds: int = 300,
    ) -> Optional[Any]:
        """Get cached value if not expired."""
        pass
    
    def _set_cache(self, key: str, value: Any) -> None:
        """Cache value with timestamp."""
        pass
```

### State Manager

**Purpose**: Persist and retrieve Graphite state.

**Key Methods**:

```python
class StateManager:
    """Manages local state persistence."""
    
    def __init__(self, graphite_dir: Path) -> None:
        self.graphite_dir = graphite_dir
        self.state_file = graphite_dir / "state.json"
        self.graphite_dir.mkdir(exist_ok=True)
    
    def load_state(self) -> dict[str, Any]:
        """Load state from disk."""
        pass
    
    def save_state(self, state: dict[str, Any]) -> None:
        """Save state to disk."""
        pass
    
    def get_branch_metadata(self, branch_name: str) -> dict[str, Any]:
        """Get metadata for specific branch."""
        pass
    
    def set_branch_metadata(
        self,
        branch_name: str,
        metadata: dict[str, Any],
    ) -> None:
        """Set metadata for specific branch."""
        pass
    
    def delete_branch_metadata(self, branch_name: str) -> None:
        """Remove metadata for branch."""
        pass
    
    def get_tracked_branches(self) -> list[str]:
        """Get list of tracked branch names."""
        pass
```

### Config Manager

**Purpose**: Manage configuration at global and repo levels.

**Key Methods**:

```python
class ConfigManager:
    """Manages configuration."""
    
    def __init__(
        self,
        repo_config_path: Path,
        global_config_path: Path,
    ) -> None:
        self.repo_config_path = repo_config_path
        self.global_config_path = global_config_path
    
    def load_config(self) -> GraphiteConfig:
        """Load merged config (global + repo)."""
        pass
    
    def save_repo_config(self, config: GraphiteConfig) -> None:
        """Save repo-level config."""
        pass
    
    def save_global_config(self, config: GraphiteConfig) -> None:
        """Save global config."""
        pass
    
    def get_github_token(self) -> Optional[str]:
        """Get GitHub token from keyring."""
        pass
    
    def set_github_token(self, token: str) -> None:
        """Store GitHub token in keyring."""
        pass
    
    def delete_github_token(self) -> None:
        """Remove GitHub token from keyring."""
        pass
```

### Validator

**Purpose**: Validate operations and state.

**Key Methods**:

```python
class Validator:
    """Validates operations and state."""
    
    def validate_branch_name(self, name: str) -> None:
        """Validate branch name is legal."""
        pass
    
    def validate_stack_operation(
        self,
        operation: str,
        stack: Stack,
        branch: Branch,
    ) -> None:
        """Validate operation won't break stack."""
        pass
    
    def validate_no_uncommitted_changes(
        self,
        git_service: GitService,
    ) -> None:
        """Ensure working tree is clean."""
        pass
    
    def validate_branch_exists(
        self,
        branch_name: str,
        git_service: GitService,
    ) -> None:
        """Ensure branch exists."""
        pass
    
    def validate_parent_child_relationship(
        self,
        child: str,
        parent: str,
        stack: Stack,
    ) -> None:
        """Ensure relationship is valid."""
        pass
```

## Command Implementation

### Create Command

**Implementation Strategy**:

1. **Parse Arguments**: Extract branch name, commit message, and flags
2. **Validate State**: Check for uncommitted changes if not using `-a`
3. **Generate Branch Name**: If name not provided, auto-generate from config template
4. **Determine Parent**: Use current branch as parent
5. **Create Branch**: Use Git service to create branch
6. **Stage Changes**: If `-a` flag, stage all changes
7. **Commit**: If `-m` flag with message, create commit
8. **Update State**: Record branch metadata in state manager
9. **Output**: Display success message with branch name

**Code Structure**:

```python
@app.command(name="create", aliases=["c"])
def create(
    name: Optional[str] = typer.Argument(None),
    message: Optional[str] = typer.Option(None, "-m", "--message"),
    all_files: bool = typer.Option(False, "-a", "--all"),
) -> None:
    """Create a new branch in the stack."""
    
    # Initialize services
    git_service = GitService(Path.cwd())
    state_manager = StateManager(Path.cwd() / ".graphite")
    stack_manager = StackManager(git_service, state_manager, Validator())
    
    try:
        # Load current stack
        stack = stack_manager.load_stack()
        
        # Get current branch as parent
        parent_branch = git_service.get_current_branch()
        
        # Create branch
        branch = stack_manager.create_branch(
            name=name,
            parent=parent_branch,
            commit_message=message,
            stage_all=all_files,
        )
        
        # Display success
        console.print(f"[green]✓[/green] Created branch: {branch.name}")
        
        if branch.parent_branch:
            console.print(f"  Parent: {branch.parent_branch}")
        
    except GraphiteException as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
```

### Submit Command

**Implementation Strategy**:

1. **Parse Arguments**: Extract flags for stack submission
2. **Determine Branches**: Get current branch or entire stack based on flags
3. **Validate State**: Ensure branches have commits
4. **Authenticate GitHub**: Verify token and permissions
5. **Push Branches**: Push all branches to remote
6. **Create/Update PRs**: For each branch, create or update PR
7. **Update PR Descriptions**: Link dependent PRs in descriptions
8. **Update State**: Record PR numbers and URLs
9. **Output**: Display PR URLs

**Code Structure**:

```python
@app.command(name="submit", aliases=["s"])
def submit(
    stack: bool = typer.Option(False, "--stack", "-s"),
) -> None:
    """Submit branches as pull requests."""
    
    # Initialize services
    git_service = GitService(Path.cwd())
    state_manager = StateManager(Path.cwd() / ".graphite")
    config_manager = ConfigManager(
        Path.cwd() / ".graphite" / "config.json",
        Path.home() / ".config" / "graphite" / "config.json",
    )
    
    config = config_manager.load_config()
    github_token = config_manager.get_github_token()
    
    if not github_token:
        console.print("[red]Error:[/red] Not authenticated with GitHub")
        console.print("Run: gt auth")
        raise typer.Exit(1)
    
    # Get repository info
    repo = git_service.get_repository_info()
    github_service = GitHubService(github_token, repo.owner, repo.name)
    
    stack_manager = StackManager(git_service, state_manager, Validator())
    
    try:
        stack_obj = stack_manager.load_stack()
        current_branch = git_service.get_current_branch()
        
        # Determine branches to submit
        if stack:
            branches = stack_obj.get_stack_for_branch(current_branch)
        else:
            branches = [stack_obj.get_branch(current_branch)]
        
        # Submit each branch
        for branch in branches:
            # Push to remote
            git_service.push(branch.name, force=False)
            
            # Determine base branch
            base = branch.parent_branch or config.trunk_branch
            
            # Get commit message for title
            title = git_service.get_commit_message(branch.commit_sha)
            
            # Generate body with stack info
            body = generate_pr_body(branch, stack_obj, config)
            
            # Create or update PR
            if branch.is_submitted():
                pr = github_service.update_pull_request(
                    branch.pr_number,
                    title=title,
                    body=body,
                )
                console.print(f"[green]✓[/green] Updated PR for {branch.name}")
            else:
                pr = github_service.create_pull_request(
                    title=title,
                    body=body,
                    head=branch.name,
                    base=base,
                )
                console.print(f"[green]✓[/green] Created PR for {branch.name}")
            
            # Update state
            branch.pr_number = pr.number
            branch.pr_url = pr.url
            stack_manager.save_stack(stack_obj)
            
            # Display PR URL
            console.print(f"  {pr.url}")
            
    except GraphiteException as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
```

### Sync Command

**Implementation Strategy**:

1. **Fetch from Remote**: Get latest changes
2. **Update Trunk**: Pull trunk branch
3. **Detect Merged Branches**: Check which PRs are merged
4. **Restack All Branches**: Rebase each tracked branch onto parent
5. **Handle Conflicts**: Detect and guide user through resolution
6. **Cleanup**: Optionally delete merged branches
7. **Output**: Display sync summary

### Log Command

**Implementation Strategy**:

1. **Load Stack**: Get current stack state
2. **Build Tree Structure**: Create visual representation
3. **Fetch PR Status**: Get PR state for each branch (with caching)
4. **Render Tree**: Use Rich to display colored tree
5. **Highlight Current**: Mark current branch

**Visualization Example**:

```
◉ main (trunk)
├─◉ feature/api-refactor (#123, ✓ merged)
│ └─◯ feature/add-logging (#124, ⏳ open, approved)
│   └─◯ feature/error-handling (#125, ⏳ open) ← current
└─◯ feature/documentation (#126, ⏳ open)
```

## Error Handling

### Exception Hierarchy

```python
class GraphiteException(Exception):
    """Base exception for all Graphite errors."""
    
    def __init__(self, message: str, hint: Optional[str] = None) -> None:
        self.message = message
        self.hint = hint
        super().__init__(message)


class GitException(GraphiteException):
    """Git operation failed."""
    pass


class GitHubException(GraphiteException):
    """GitHub API operation failed."""
    pass


class ValidationException(GraphiteException):
    """Validation failed."""
    pass


class ConflictException(GitException):
    """Git conflict detected."""
    
    def __init__(self, branch: str, conflicting_files: list[str]) -> None:
        self.branch = branch
        self.conflicting_files = conflicting_files
        message = f"Conflict detected in branch '{branch}'"
        hint = "Resolve conflicts and run: gt continue"
        super().__init__(message, hint)


class AuthenticationException(GitHubException):
    """GitHub authentication failed."""
    
    def __init__(self) -> None:
        message = "Not authenticated with GitHub"
        hint = "Run: gt auth"
        super().__init__(message, hint)
```

### Error Display

All errors displayed with:
- Clear error message
- Contextual information
- Suggested fix (hint)
- Error code for reference

```python
def display_error(error: GraphiteException) -> None:
    """Display error with formatting."""
    console.print(f"\n[red]Error:[/red] {error.message}")
    
    if error.hint:
        console.print(f"[yellow]Hint:[/yellow] {error.hint}")
    
    if hasattr(error, "__cause__") and error.__cause__:
        console.print(f"\n[dim]Caused by: {error.__cause__}[/dim]")
```

## State Persistence

### State File Format

**Location**: `.graphite/state.json`

**Schema**:

```json
{
  "version": "1.0",
  "trunk_branch": "main",
  "branches": {
    "feature/api-refactor": {
      "parent_branch": "main",
      "pr_number": 123,
      "pr_url": "https://github.com/owner/repo/pull/123",
      "created_at": "2025-11-19T20:00:00Z",
      "updated_at": "2025-11-19T21:00:00Z",
      "custom_metadata": {}
    },
    "feature/add-logging": {
      "parent_branch": "feature/api-refactor",
      "pr_number": 124,
      "pr_url": "https://github.com/owner/repo/pull/124",
      "created_at": "2025-11-19T20:30:00Z",
      "updated_at": "2025-11-19T20:30:00Z",
      "custom_metadata": {}
    }
  },
  "tracked_remotes": []
}
```

### Config File Format

**Locations**:
- Global: `~/.config/graphite/config.json`
- Repo: `.graphite/config.json`

**Schema**:

```json
{
  "trunk_branch": "main",
  "remote_name": "origin",
  "branch_prefix": "dv/",
  "branch_name_template": "{prefix}{date}_{description}",
  "pr_title_template": "{commit_message}",
  "pr_body_template": "",
  "include_pr_links": true,
  "auto_restack": true,
  "confirm_destructive_ops": true,
  "merge_method": "squash",
  "use_colors": true,
  "use_emoji": true,
  "show_pr_status": true,
  "log_level": "INFO",
  "cache_github_data": true,
  "cache_ttl_seconds": 300
}
```

## Security Design

### Token Storage

**Approach**: Use system keyring for credential storage

**Implementation**:

```python
import keyring

SERVICE_NAME = "graphite-cli-clone"
TOKEN_KEY = "github_token"

def store_token(token: str) -> None:
    """Store GitHub token securely."""
    keyring.set_password(SERVICE_NAME, TOKEN_KEY, token)

def retrieve_token() -> Optional[str]:
    """Retrieve GitHub token."""
    return keyring.get_password(SERVICE_NAME, TOKEN_KEY)

def delete_token() -> None:
    """Delete stored token."""
    keyring.delete_password(SERVICE_NAME, TOKEN_KEY)
```

### Input Validation

- Validate all user input before processing
- Sanitize branch names (no special characters)
- Validate Git refs before operations
- Prevent command injection in Git operations

### API Security

- Always use HTTPS for GitHub API
- Validate API responses
- Handle rate limiting gracefully
- Never log sensitive data (tokens, credentials)

## Performance Optimization

### Caching Strategy

**GitHub API Caching**:
- Cache PR status for 5 minutes (configurable)
- Cache repository metadata for 10 minutes
- Invalidate cache on mutations

**Git Operations**:
- Batch Git commands where possible
- Minimize repository state queries
- Use plumbing commands for performance

### Lazy Loading

- Load stack state only when needed
- Defer GitHub API calls until required
- Load configuration on-demand

## Testing Strategy

### Unit Tests

**Coverage Target**: 80%+

**Key Test Areas**:
- Data models (Branch, Stack, etc.)
- Service methods (StackManager, GitService, etc.)
- Validation logic
- Configuration management
- Error handling

**Example Test**:

```python
def test_stack_get_upstack_branches():
    """Test getting upstack branches."""
    # Create test stack
    trunk = Branch("main", "abc123", None, None, None, datetime.now(), datetime.now())
    branch1 = Branch("feat1", "def456", "main", 1, "url1", datetime.now(), datetime.now())
    branch2 = Branch("feat2", "ghi789", "feat1", 2, "url2", datetime.now(), datetime.now())
    
    stack = Stack("main", [trunk, branch1, branch2], "feat2")
    
    # Test upstack from trunk
    upstack = stack.get_upstack_branches("main")
    assert len(upstack) == 2
    assert branch1 in upstack
    assert branch2 in upstack
    
    # Test upstack from branch1
    upstack = stack.get_upstack_branches("feat1")
    assert len(upstack) == 1
    assert branch2 in upstack
```

### Integration Tests

**Key Test Areas**:
- Git operations (using temporary repos)
- GitHub API (using mocks)
- State persistence
- Configuration loading

**Example Test**:

```python
@pytest.fixture
def temp_git_repo(tmp_path):
    """Create temporary Git repository."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    git.Repo.init(repo_path)
    return repo_path

def test_git_service_create_branch(temp_git_repo):
    """Test creating branch via GitService."""
    service = GitService(temp_git_repo)
    
    # Create initial commit
    (temp_git_repo / "test.txt").write_text("test")
    service.commit("Initial commit", all_files=True)
    
    # Create branch
    service.create_branch("feature/test")
    
    # Verify branch exists
    branches = [b.name for b in service.repo.branches]
    assert "feature/test" in branches
```

### End-to-End Tests

**Key Workflows**:
- Complete create → submit workflow
- Create → modify → submit workflow
- Sync workflow with conflicts
- Stack manipulation workflows

## Output Formatting

### Rich Library Usage

**Components**:
- **Console**: Main output interface
- **Table**: For structured data
- **Tree**: For stack visualization
- **Panel**: For grouped information
- **Progress**: For long operations
- **Syntax**: For code/diff highlighting

**Example Output**:

```python
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

console = Console()

def display_stack(stack: Stack) -> None:
    """Display stack as tree."""
    tree = Tree(f"[bold]{stack.trunk_branch}[/bold] (trunk)")
    
    def add_branch_to_tree(parent_tree, branch: Branch) -> None:
        # Format branch display
        branch_str = f"{branch.name}"
        
        if branch.pr_number:
            branch_str += f" (#{branch.pr_number})"
        
        # Add to tree
        node = parent_tree.add(branch_str)
        
        # Add children recursively
        children = branch.get_children(stack)
        for child in children:
            add_branch_to_tree(node, child)
    
    # Build tree
    trunk_branch = stack.get_branch(stack.trunk_branch)
    if trunk_branch:
        for child in trunk_branch.get_children(stack):
            add_branch_to_tree(tree, child)
    
    console.print(tree)
```

## Deployment

### PyPI Package

**Package Configuration** (`pyproject.toml`):

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "graphite-cli-clone"
version = "0.1.0"
description = "A Python clone of the Graphite CLI tool"
readme = "README.md"
requires-python = ">=3.14"
license = {text = "MIT"}
authors = [
    {name = "DSCV101", email = "derek.vitrano@gmail.com"},
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.14",
    "Topic :: Software Development :: Version Control :: Git",
]
dependencies = [
    "typer>=0.12.0",
    "rich>=13.7.0",
    "GitPython>=3.1.40",
    "PyGithub>=2.1.1",
    "keyring>=24.3.0",
    "pydantic>=2.5.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.3",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.6",
    "pyright>=1.1.338",
    "bandit>=1.7.5",
]

[project.scripts]
gt = "graphite_cli.__main__:main"

[tool.hatch.build.targets.wheel]
packages = ["src/graphite_cli"]

[tool.ruff]
target-version = "py314"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.pyright]
pythonVersion = "3.14"
strictMode = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]

[tool.coverage.run]
source = ["src/graphite_cli"]
omit = ["tests/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]
```

### Installation

```bash
pip install graphite-cli-clone
```

### Shell Completion

Generate completion scripts:

```bash
gt completion --shell bash > ~/.local/share/bash-completion/completions/gt
gt completion --shell zsh > ~/.zsh/completion/_gt
```

## Migration Path

### From Original Graphite CLI

**Compatibility Considerations**:
- Use same `.graphite/` directory structure
- Support importing existing state files
- Provide migration command: `gt migrate --from graphite`

**Migration Strategy**:
1. Detect existing Graphite installation
2. Parse existing state file
3. Convert to new format if needed
4. Preserve PR associations
5. Maintain branch relationships

## Future Enhancements

### Parallel Operations

Use `asyncio` for parallel GitHub API calls:

```python
import asyncio
from typing import Awaitable

async def submit_branches_parallel(
    branches: list[Branch],
    github_service: GitHubService,
) -> list[PullRequest]:
    """Submit multiple branches in parallel."""
    tasks: list[Awaitable[PullRequest]] = []
    
    for branch in branches:
        task = github_service.create_pull_request_async(
            title=branch.name,
            body="",
            head=branch.name,
            base=branch.parent_branch,
        )
        tasks.append(task)
    
    return await asyncio.gather(*tasks)
```

### Interactive UI

Use `textual` for interactive TUI:
- Interactive branch selection
- Real-time stack visualization
- Interactive conflict resolution

### AI-Powered Features

- Auto-generate PR descriptions using AI
- Suggest branch names based on changes
- Smart conflict resolution suggestions

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Week 1**:
- Set up project structure
- Configure tooling (Hatch, Ruff, Pyright, pytest)
- Implement data models
- Set up CI/CD pipeline

**Week 2**:
- Implement GitService
- Implement StateManager
- Implement ConfigManager
- Write unit tests for foundation

### Phase 2: Core Stack Operations (Weeks 3-4)

**Week 3**:
- Implement StackManager
- Implement Validator
- Implement create command
- Implement log command

**Week 4**:
- Implement restack logic
- Implement navigation commands (up, down, top, bottom)
- Write tests for stack operations
- Integration tests with temporary Git repos

### Phase 3: GitHub Integration (Weeks 5-6)

**Week 5**:
- Implement GitHubService
- Implement auth command
- Implement token storage (keyring)
- Write GitHub API tests (mocked)

**Week 6**:
- Implement submit command
- Implement PR creation/update logic
- Implement PR body generation with stack links
- Write end-to-end submit tests

### Phase 4: Advanced Features (Weeks 7-8)

**Week 7**:
- Implement modify command
- Implement sync command
- Implement conflict detection and handling
- Write tests for modify/sync workflows

**Week 8**:
- Implement manipulation commands (delete, move, rename)
- Implement merge command
- Implement collaboration commands (get, track)
- Write tests for manipulation workflows

### Phase 5: Polish & Documentation (Weeks 9-10)

**Week 9**:
- Implement shell completion
- Implement help system
- Write user documentation
- Create tutorial videos/guides

**Week 10**:
- Bug fixes and refinements
- Performance optimization
- Security audit
- Prepare for PyPI release

## Success Metrics

### Technical Metrics

- **Test Coverage**: ≥80%
- **Type Coverage**: 100% (all functions typed)
- **Performance**: Command response <500ms for local ops
- **Security**: Zero critical vulnerabilities (Bandit scan)

### User Experience Metrics

- **Installation Success**: 95%+ successful installs
- **Command Success Rate**: 99%+ for valid operations
- **Error Clarity**: User can resolve 90%+ of errors from error messages

### Adoption Metrics

- **PyPI Downloads**: Target 1,000 in first month
- **GitHub Stars**: Target 100 in first quarter
- **User Feedback**: Average 4+ stars on user surveys

## References

- Sean Grove's "The New Code" talk: Focus on specifications over code
- Graphite CLI source code: Study implementation patterns
- Git internals documentation: Understanding Git operations
- GitHub API v3 documentation: API capabilities and limits
- Python type system: Leveraging type hints effectively
- Rich library documentation: Terminal formatting capabilities

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-19  
**Status**: Design approved - ready for implementation  
**Author**: DSCV101 Organization  
**Based On**: requirements.md v1.0
