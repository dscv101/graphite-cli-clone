# AGENTS.md

This document provides coding standards, project standards, security guidelines, and testing requirements for AI agents working on the Graphite CLI Clone project.

**Version**: 1.0  
**Last Updated**: 2025-11-20  
**Applies To**: All AI agents (Codegen, Claude, etc.)

---

## Table of Contents

1. [Coding Standards](#coding-standards)
2. [Project Standards](#project-standards)
3. [Security Guidelines](#security-guidelines)
4. [Testing Requirements](#testing-requirements)
5. [AI Agent Workflow](#ai-agent-workflow)
6. [Common Pitfalls](#common-pitfalls)

---

## Coding Standards

### Style Guide

This project follows the **Google Python Style Guide** with specific configurations enforced by Ruff.

#### Key Requirements

- **Line Length**: Maximum 100 characters
- **Python Version**: Minimum 3.11, target 3.11+ features
- **Type Hints**: Required for all functions, methods, and class attributes
- **Docstrings**: Required for all public APIs (modules, classes, functions, methods)
- **Docstring Format**: Google-style docstrings

#### Example

```python
def restack_branch(
    branch_name: str,
    parent_branch: str,
    force: bool = False,
) -> BranchMetadata:
    """Rebase a branch onto its parent branch.

    Args:
        branch_name: The name of the branch to restack.
        parent_branch: The name of the parent branch.
        force: If True, force the restack even if conflicts exist.

    Returns:
        Updated branch metadata after restacking.

    Raises:
        GraphiteRebaseError: If the rebase fails.
        GraphiteBranchNotFoundError: If the branch doesn't exist.
    """
    # Implementation here
    pass
```

### Code Quality Tools

#### Ruff (Linting & Formatting)

```bash
# Format code
hatch run format

# Check formatting
hatch run format-check

# Lint code
hatch run lint
```

**Enabled Rules**: See `pyproject.toml` lines 89-127 for full list. Key categories:
- `E`, `W`: pycodestyle errors and warnings
- `F`: pyflakes (undefined names, unused imports)
- `I`: isort (import sorting)
- `D`: pydocstyle (Google-style docstrings)
- `ANN`: type annotations (required)
- `S`: security (bandit integration)
- `B`: bugbear (likely bugs and design issues)
- `RUF`: Ruff-specific best practices

**Per-File Ignores**:
- Tests: `S101` (assert), `ANN` (type hints), `D` (docstrings) allowed
- `exceptions/base.py`: `N818` (exception naming pattern)

#### Pyright (Type Checking)

```bash
hatch run type-check
```

**Configuration**: Strict mode enabled with:
- Import cycle detection
- Unused import/class/function/variable detection
- Private usage enforcement
- Unnecessary cast/isinstance detection

#### Bandit (Security)

```bash
hatch run security
```

**Configuration**: Medium-high severity detection, excludes test directories.

### Import Organization

Use isort conventions (enforced by Ruff):

```python
# Standard library imports
import os
from pathlib import Path
from typing import Optional

# Third-party imports
import typer
from rich.console import Console

# Local application imports
from graphite_cli.models.branch import Branch
from graphite_cli.services.git import GitService
```

### Naming Conventions

- **Modules**: `snake_case` (e.g., `stack_manager.py`)
- **Classes**: `PascalCase` (e.g., `StackManager`, `GitService`)
- **Functions/Methods**: `snake_case` (e.g., `restack_branch`, `get_current_branch`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_CONFIG_PATH`, `MAX_BRANCH_NAME_LENGTH`)
- **Private Members**: Prefix with `_` (e.g., `_internal_helper`)
- **Exceptions**: Prefix with `Graphite` (e.g., `GraphiteRebaseError`)

### Type Hints Best Practices

```python
from typing import Optional, List, Dict, Any
from pathlib import Path

# Good: Explicit types
def load_config(path: Path) -> Dict[str, Any]:
    pass

# Good: Optional for nullable values
def find_parent(branch: str) -> Optional[str]:
    pass

# Good: Generic collections
def list_branches() -> List[Branch]:
    pass

# Avoid: Implicit Any
def process_data(data):  # Bad: missing type hint
    pass
```

---

## Project Standards

### Architecture Overview

The project follows a **6-layer architecture**:

```
CLI Entry Point (Typer)
    ↓
Command Router (create/submit/modify/sync/etc.)
    ↓
Core Services (StackManager, GitService, GitHubService, ConfigManager, StateManager, Validator)
    ↓
Data Layer (Git repo, .graphite/ directory, system keyring)
```

### Directory Structure

```
src/graphite_cli/
├── cli/                    # CLI commands and entry points
│   ├── app.py             # Main Typer app
│   └── commands/          # Command implementations
├── models/                # Data models (Pydantic)
│   ├── branch.py
│   ├── stack.py
│   ├── repository.py
│   ├── config.py
│   └── pull_request.py
├── services/              # Business logic services
│   ├── git.py            # Git operations wrapper
│   ├── github.py         # GitHub API wrapper
│   ├── stack_manager.py  # Stack manipulation
│   ├── config_manager.py # Configuration management
│   └── state_manager.py  # State persistence
├── utils/                 # Utility functions
│   ├── validators.py     # Input validation
│   └── terminal.py       # Terminal UI helpers
└── exceptions/            # Custom exceptions
    └── base.py           # Exception hierarchy

tests/
├── unit/                  # Unit tests (isolated)
├── integration/           # Integration tests (Git/GitHub)
└── e2e/                  # End-to-end workflow tests
```

### Data Models (Pydantic)

All data models must:
1. Inherit from `pydantic.BaseModel`
2. Use type annotations for all fields
3. Include field descriptions via `Field(description="...")`
4. Define validators for complex validation logic
5. Implement serialization methods if needed

**Example**:

```python
from pydantic import BaseModel, Field, field_validator

class Branch(BaseModel):
    """Represents a Git branch with Graphite metadata.
    
    Attributes:
        name: The branch name (must be valid Git ref).
        parent: The parent branch name in the stack.
        commit_sha: The current commit SHA.
        pr_number: Associated GitHub PR number (if submitted).
        created_at: ISO 8601 timestamp of creation.
    """
    
    name: str = Field(description="Branch name")
    parent: str = Field(description="Parent branch name")
    commit_sha: str = Field(description="Current commit SHA")
    pr_number: Optional[int] = Field(None, description="GitHub PR number")
    created_at: str = Field(description="Creation timestamp (ISO 8601)")
    
    @field_validator("name")
    @classmethod
    def validate_branch_name(cls, v: str) -> str:
        """Validate branch name follows Git ref naming rules."""
        if not v or v.startswith("-"):
            raise ValueError("Branch name cannot be empty or start with '-'")
        return v
```

### Service Layer Guidelines

**Principles**:
1. **Single Responsibility**: Each service manages one domain (Git, GitHub, Stack, Config, State)
2. **Dependency Injection**: Pass dependencies via constructor, not global imports
3. **Error Handling**: Raise specific exceptions, don't return error codes
4. **Idempotency**: Operations should be safe to retry when possible
5. **Logging**: Use structured logging for debugging (not `print()`)

**Example**:

```python
class StackManager:
    """Manages stack operations (restack, visualization, manipulation)."""
    
    def __init__(self, git_service: GitService, state_manager: StateManager) -> None:
        """Initialize the stack manager.
        
        Args:
            git_service: Service for Git operations.
            state_manager: Service for state persistence.
        """
        self._git = git_service
        self._state = state_manager
    
    def restack_branch(self, branch: Branch, force: bool = False) -> Branch:
        """Rebase a branch and all its descendants onto the parent branch.
        
        Args:
            branch: The branch to restack.
            force: If True, force restack even if conflicts detected.
        
        Returns:
            Updated branch metadata.
        
        Raises:
            GraphiteRebaseError: If rebase fails.
        """
        # Implementation
        pass
```

### State Management

**State Storage Locations**:
- `.graphite/state.json` - Branch relationships, PR associations, metadata
- `.graphite/config.json` - Repository-level configuration
- `~/.config/graphite/config.json` - Global user configuration
- System keyring - GitHub tokens (secure storage via `keyring` library)

**State Schema** (`.graphite/state.json`):

```json
{
  "version": "1.0",
  "trunk": "main",
  "branches": {
    "feature-branch": {
      "parent": "main",
      "children": ["sub-feature"],
      "pr_number": 123,
      "commit_sha": "abc123...",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T14:20:00Z"
    }
  }
}
```

**State Modification Rules**:
1. Always validate state before writing
2. Create backups before destructive operations
3. Handle corrupted state gracefully (rebuild from Git if possible)
4. Use atomic file writes (write to temp, then rename)
5. Lock state file during modifications to prevent race conditions

### Error Handling

**Exception Hierarchy**:

```python
# Base exception
class GraphiteError(Exception):
    """Base exception for all Graphite errors."""
    pass

# Category exceptions
class GraphiteGitError(GraphiteError):
    """Git operation failed."""
    pass

class GraphiteGitHubError(GraphiteError):
    """GitHub API operation failed."""
    pass

class GraphiteValidationError(GraphiteError):
    """Input validation failed."""
    pass

# Specific exceptions
class GraphiteBranchNotFoundError(GraphiteGitError):
    """Branch does not exist."""
    pass

class GraphiteRebaseError(GraphiteGitError):
    """Rebase operation failed."""
    pass
```

**Error Handling Practices**:
1. Catch specific exceptions, not generic `Exception`
2. Provide helpful error messages with actionable guidance
3. Include context (branch name, PR number, etc.) in error messages
4. Log full tracebacks for debugging, but show clean messages to users
5. Use `typer.Exit()` for fatal CLI errors

---

## Security Guidelines

### Critical Security Rules

⚠️ **NEVER commit secrets to the repository**

1. **GitHub Tokens**:
   - Store in system keyring via `keyring` library
   - Never log tokens or include in error messages
   - Never write tokens to files (including config files)
   - Use environment variables only for CI/CD, not local development

2. **User Data**:
   - Sanitize all user input before passing to Git/GitHub APIs
   - Validate branch names, commit messages, and file paths
   - Prevent path traversal attacks in file operations

3. **Git Operations**:
   - Never execute arbitrary shell commands from user input
   - Use GitPython API, not shell commands when possible
   - Validate all Git refs before checkout/rebase operations

4. **GitHub API**:
   - Use PyGithub library, not raw HTTP requests
   - Respect rate limits (5000 requests/hour for authenticated users)
   - Cache API responses when appropriate

### Security Checklist

Before committing code, verify:

- [ ] No hardcoded tokens, passwords, or API keys
- [ ] No sensitive data in error messages or logs
- [ ] User input validated before use in commands
- [ ] File paths sanitized to prevent directory traversal
- [ ] Shell command injection prevented
- [ ] Secrets stored in keyring, not files
- [ ] Security linter (Bandit) passes without warnings

### Running Security Checks

```bash
# Run Bandit security linter
hatch run security

# Check for common security issues
ruff check --select S

# Manual review checklist
grep -r "token\|password\|secret" src/  # Should find only keyring usage
```

---

## Testing Requirements

### Testing Strategy

**Target Coverage**: 80%+ overall, 100% for critical paths

**Test Types**:
1. **Unit Tests** (`tests/unit/`): Isolated component testing with mocks
2. **Integration Tests** (`tests/integration/`): Real Git operations, mocked GitHub
3. **End-to-End Tests** (`tests/e2e/`): Complete workflow testing

### Unit Tests

**Guidelines**:
- Test each function/method in isolation
- Mock all external dependencies (Git, GitHub, filesystem)
- Use `pytest.fixture` for common setup
- Test both success and failure cases
- Test edge cases and boundary conditions

**Example**:

```python
import pytest
from unittest.mock import Mock, patch
from graphite_cli.services.stack_manager import StackManager

@pytest.fixture
def mock_git_service():
    """Create a mock GitService."""
    return Mock()

@pytest.fixture
def mock_state_manager():
    """Create a mock StateManager."""
    return Mock()

@pytest.fixture
def stack_manager(mock_git_service, mock_state_manager):
    """Create a StackManager with mocked dependencies."""
    return StackManager(mock_git_service, mock_state_manager)

def test_restack_branch_success(stack_manager, mock_git_service):
    """Test successful branch restack."""
    # Arrange
    branch = Branch(name="feature", parent="main", commit_sha="abc123")
    mock_git_service.rebase.return_value = True
    
    # Act
    result = stack_manager.restack_branch(branch)
    
    # Assert
    assert result.name == "feature"
    mock_git_service.rebase.assert_called_once_with("feature", "main")

def test_restack_branch_conflict(stack_manager, mock_git_service):
    """Test restack with merge conflicts."""
    # Arrange
    branch = Branch(name="feature", parent="main", commit_sha="abc123")
    mock_git_service.rebase.side_effect = GraphiteRebaseError("Conflict")
    
    # Act & Assert
    with pytest.raises(GraphiteRebaseError):
        stack_manager.restack_branch(branch)
```

### Integration Tests

**Guidelines**:
- Use temporary Git repositories (create in `/tmp`)
- Test real Git operations (commit, rebase, merge)
- Mock GitHub API calls (use `responses` library)
- Clean up resources after tests
- Mark with `@pytest.mark.integration`

**Example**:

```python
import pytest
import tempfile
import shutil
from pathlib import Path
from graphite_cli.services.git import GitService

@pytest.fixture
def temp_git_repo():
    """Create a temporary Git repository."""
    repo_dir = Path(tempfile.mkdtemp())
    # Initialize Git repo
    git = GitService(repo_dir)
    git.init()
    # Create initial commit
    (repo_dir / "README.md").write_text("# Test Repo")
    git.add("README.md")
    git.commit("Initial commit")
    
    yield repo_dir
    
    # Cleanup
    shutil.rmtree(repo_dir)

@pytest.mark.integration
def test_git_rebase_integration(temp_git_repo):
    """Test real Git rebase operation."""
    git = GitService(temp_git_repo)
    
    # Create feature branch
    git.checkout("feature", create=True)
    (temp_git_repo / "feature.txt").write_text("Feature")
    git.add("feature.txt")
    git.commit("Add feature")
    
    # Create commits on main
    git.checkout("main")
    (temp_git_repo / "main.txt").write_text("Main")
    git.add("main.txt")
    git.commit("Update main")
    
    # Rebase feature onto main
    git.checkout("feature")
    git.rebase("main")
    
    # Assert
    assert (temp_git_repo / "feature.txt").exists()
    assert (temp_git_repo / "main.txt").exists()
```

### End-to-End Tests

**Guidelines**:
- Test complete user workflows
- Use real Git, mock GitHub API
- Test commands via CLI interface
- Mark with `@pytest.mark.e2e`

**Example Workflows to Test**:
1. `gt init` → `gt create` → `gt submit` → `gt sync`
2. `gt create` (multiple) → `gt log` → `gt up/down`
3. `gt modify` → `gt submit --stack` → verify PR updates
4. Branch deletion and stack cleanup

### Running Tests

```bash
# Run all tests
hatch run test

# Run with coverage
hatch run test-cov

# Run specific test types
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m e2e            # End-to-end tests only

# Run specific test file
pytest tests/unit/test_stack_manager.py

# Run specific test
pytest tests/unit/test_stack_manager.py::test_restack_branch_success
```

### Test Coverage Goals

| Component | Target Coverage | Priority |
|-----------|----------------|----------|
| Models | 100% | Critical |
| Services (Stack, Git, GitHub) | 100% | Critical |
| CLI Commands | 80% | High |
| Utils | 80% | Medium |
| Exception Handling | 100% | Critical |

---

## AI Agent Workflow

### Before Starting Work

1. **Read project documentation**:
   - `CLAUDE.md` - Project overview and structure
   - `requirements.md` - Complete requirements specification
   - `design.md` - Technical design and architecture
   - `task_dag.md` - Task breakdown and dependencies
   - This file (`AGENTS.md`) - Standards and guidelines

2. **Check current project state**:
   ```bash
   # View directory structure
   ls -la src/graphite_cli/
   
   # Check existing tests
   ls -la tests/
   
   # Run existing tests
   hatch run test
   ```

3. **Identify task dependencies**:
   - Consult `task_dag.md` for prerequisite tasks
   - Verify prerequisite components exist before building on them

### During Implementation

1. **Follow TDD (Test-Driven Development)**:
   - Write failing tests first
   - Implement minimal code to pass tests
   - Refactor for quality

2. **Incremental commits**:
   - Commit frequently with descriptive messages
   - Format: `<type>: <description>` (e.g., `feat: implement Branch model`)
   - Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`

3. **Run checks continuously**:
   ```bash
   # Before each commit
   hatch run format       # Format code
   hatch run lint         # Check linting
   hatch run type-check   # Check types
   hatch run test         # Run tests
   
   # Or run all at once
   hatch run check-all
   ```

4. **Use MCP servers** (per repo rules):
   - `context7` - For third-party documentation
   - `code-reasoning` - For decision making

### Code Review Self-Checklist

Before submitting code for review:

- [ ] All tests pass (`hatch run test`)
- [ ] Code is formatted (`hatch run format`)
- [ ] No linting errors (`hatch run lint`)
- [ ] No type checking errors (`hatch run type-check`)
- [ ] No security issues (`hatch run security`)
- [ ] Test coverage meets targets (80%+)
- [ ] All public APIs have docstrings
- [ ] Error handling is comprehensive
- [ ] No hardcoded secrets or credentials
- [ ] State changes are validated and atomic
- [ ] Integration tests for Git operations
- [ ] User-facing error messages are helpful

---

## Common Pitfalls

### Pitfall 1: Skipping Type Hints

❌ **Wrong**:
```python
def find_branch(name):
    return branches.get(name)
```

✅ **Correct**:
```python
def find_branch(name: str) -> Optional[Branch]:
    """Find a branch by name."""
    return branches.get(name)
```

### Pitfall 2: Hardcoded Paths

❌ **Wrong**:
```python
config_path = "/home/user/.graphite/config.json"
```

✅ **Correct**:
```python
from pathlib import Path

config_path = Path.home() / ".config" / "graphite" / "config.json"
```

### Pitfall 3: Catching Generic Exceptions

❌ **Wrong**:
```python
try:
    git.rebase(branch)
except Exception:
    print("Rebase failed")
```

✅ **Correct**:
```python
try:
    git.rebase(branch)
except GraphiteRebaseError as e:
    typer.echo(f"Error: Failed to rebase {branch}: {e}", err=True)
    raise typer.Exit(1)
```

### Pitfall 4: Untested Code Paths

❌ **Wrong**: Implementing a feature without tests

✅ **Correct**: Write tests first, then implement

```python
# 1. Write test
def test_restack_with_conflict():
    # Test conflict handling
    pass

# 2. Implement feature
def restack_branch(branch):
    # Implementation
    pass
```

### Pitfall 5: Logging Sensitive Data

❌ **Wrong**:
```python
logger.info(f"Using GitHub token: {token}")
```

✅ **Correct**:
```python
logger.info("Using GitHub token: [REDACTED]")
# Or use structured logging with automatic redaction
```

### Pitfall 6: Direct Shell Commands

❌ **Wrong**:
```python
import subprocess
subprocess.run(f"git rebase {branch}", shell=True)
```

✅ **Correct**:
```python
from git import Repo
repo = Repo(".")
repo.git.rebase(branch)
```

### Pitfall 7: Missing Validation

❌ **Wrong**:
```python
def create_branch(name: str) -> Branch:
    # Assume name is valid
    return Branch(name=name, ...)
```

✅ **Correct**:
```python
def create_branch(name: str) -> Branch:
    """Create a new branch with validation."""
    if not name or name.startswith("-"):
        raise GraphiteValidationError(f"Invalid branch name: {name}")
    if ".." in name:
        raise GraphiteValidationError(f"Path traversal detected in branch name: {name}")
    return Branch(name=name, ...)
```

---

## Additional Resources

### Documentation

- **Google Python Style Guide**: https://google.github.io/styleguide/pyguide.html
- **Pydantic Documentation**: https://docs.pydantic.dev/latest/
- **Typer Documentation**: https://typer.tiangolo.com/
- **GitPython Documentation**: https://gitpython.readthedocs.io/

### Tools

- **Ruff**: https://docs.astral.sh/ruff/
- **Pyright**: https://github.com/microsoft/pyright
- **pytest**: https://docs.pytest.org/
- **Hatch**: https://hatch.pypa.io/

### Project-Specific

- **Requirements**: See `requirements.md`
- **Design**: See `design.md`
- **Tasks**: See `task_dag.md`
- **Quick Start**: See `CLAUDE.md`

---

**Questions?** Open an issue or consult the project maintainers.

**Last Updated**: 2025-11-20  
**Version**: 1.0
