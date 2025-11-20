# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains planning documentation for a **Graphite CLI Clone** - a Python-based tool that simplifies Git workflows and enables efficient PR stacking for software development teams. This is currently a **planning/specification repository** with no implementation yet.

**Key Concept**: The tool implements a "stack-based workflow" where each branch represents an atomic changeset, with branches depending on each other in a chain from trunk (main) to the most recent changes (upstack).

## Repository Structure

```
graphite-cli-clone/
├── requirements.md    # Complete requirements specification
├── design.md         # Technical design document with architecture
└── task_dag.md       # Task breakdown with dependencies (52 tasks)
```

## Key Documents

### requirements.md (16KB)
Complete specification including:
- Core commands: `gt create`, `gt submit`, `gt modify`, `gt sync`
- Navigation commands: `gt log`, `gt up/down/top/bottom`
- Stack manipulation: `gt rename`, `gt delete`, `gt move`, etc.
- Technical requirements: Python 3.14+, dependencies (Typer, Rich, GitPython, PyGithub)
- Architecture: 6-layer system (CLI, Git, GitHub, Stack, Config, Storage)

### design.md (24KB)
Technical implementation details including:
- Complete architecture diagrams
- Data models with full code examples (Branch, Stack, Repository, Config, PullRequest)
- Core service specifications (StackManager, GitService, GitHubService, StateManager, ConfigManager, Validator)
- Command implementation strategies with code examples
- State persistence formats (JSON schemas for .graphite/state.json and config.json)
- Error handling hierarchy
- Testing strategy

### task_dag.md (16KB)
Parallelization-optimized task breakdown:
- **72 tasks** organized into 8 stages
- Dependencies mapped as a DAG for parallel execution
- Effort estimates: 320-400 hours total, deliverable in 10 weeks with 3-4 developers
- Task categories: setup (3), backend (43), testing (11), docs (8), infra (4), qa (3)

## Architecture Overview

The planned system has 6 layers:

```
CLI Entry Point (Typer)
    ↓
Command Router (create/submit/modify/sync/etc.)
    ↓
Core Services (StackManager, GitService, GitHubService, ConfigManager, StateManager, Validator)
    ↓
Data Layer (Git repo, .graphite/ directory, system keyring)
```

**Key Data Models**:
- **Branch**: Git branch + metadata (parent, PR number, timestamps)
- **Stack**: Collection of related branches with tree operations
- **Repository**: Git repo state with GitHub integration
- **Config**: User/repo settings with templates and preferences
- **PullRequest**: GitHub PR metadata with merge status

**State Storage**:
- `.graphite/state.json` - Branch relationships, PR associations, metadata
- `.graphite/config.json` - Repo-level configuration
- `~/.config/graphite/config.json` - Global configuration
- System keyring - GitHub tokens (secure storage)

## Implementation Guidelines

### If Starting Implementation

**Phase 1: Foundation** (Start here)
- T001: Project setup with Hatch, pyproject.toml, src/graphite_cli/ structure
- T002: Configure Ruff (Google style, 100 char lines), Pyright (strict), Bandit, pytest
- T003: GitHub Actions CI/CD for linting, type checking, testing
- T004-T009: Implement data models in models/ directory

**Critical Path Tasks** (must be completed in order):
```
T001 → T005 (Branch model) → T006 (Stack model) → T024 (StackManager) → 
T025 (Restack) → T033 (Sync command) → T055 (E2E tests) → T068 (Coverage) → 
T069 (Integration testing) → T070 (Bug fixes) → T071 (Changelog) → T072 (Release)
```

**Parallel Development Opportunities**:
- Stages 1-2: Up to 11 tasks can run in parallel (models, utils, base services)
- Stage 5: Peak of 15 tasks can run in parallel (commands + tests)
- See task_dag.md "Execution Stages" for full parallelization strategy

### Code Quality Standards

**Must follow**:
- Google Python Style Guide
- Type hints for all functions (target: 100% type coverage)
- Docstrings for all public APIs
- Maximum line length: 100 characters
- Use Ruff for linting/formatting, Pyright for type checking

**Testing Requirements**:
- Unit tests: 80%+ coverage target
- Integration tests: Git operations with temp repos, GitHub API with mocks
- E2E tests: Complete workflows (create→submit, modify→sync, etc.)
- Framework: pytest + pytest-cov

### Dependencies (from design.md)

**Core**:
- Python 3.14+
- Typer ≥0.12.0 (CLI framework)
- Rich ≥13.7.0 (terminal formatting)
- GitPython ≥3.1.40 (Git operations)
- PyGithub ≥2.1.1 (GitHub API)
- keyring ≥24.3.0 (secure credential storage)
- pydantic ≥2.5.0 (data validation)

**Dev**:
- pytest ≥7.4.3
- pytest-cov ≥4.1.0
- ruff ≥0.1.6
- pyright ≥1.1.338
- bandit ≥1.7.5

## Common Tasks

### Planning & Analysis
```bash
# Review requirements
cat requirements.md | less

# Review architecture
cat design.md | less

# Check task dependencies
cat task_dag.md | less
```

### When Modifying Plans

**Consistency Rules**:
1. Changes to requirements.md must be reflected in design.md
2. New features require task entries in task_dag.md with effort estimates
3. Dependencies must be added to the DAG section
4. Update the relevant "Stage" in task_dag.md if adding tasks

**Document Versioning**:
- Each document has a version number and "Last Updated" date at bottom
- Increment version for significant changes
- Update "Last Updated" for any modification

### Task Breakdown Format (task_dag.md)

When adding new tasks, use this format:
```
| task_id | title | description | type | component | prerequisites | estimated_effort | priority |
```

Types: setup, backend, testing, docs, infra, qa
Components: infra, models, utils, core, cli, test, docs, release, qa
Priorities: critical, high, medium, low

## Key Concepts to Understand

**Stack Terminology**:
- **Trunk**: Central branch (main/master) where everything merges
- **Upstack**: Branches further from main (descendants, more recent)
- **Downstack**: Branches closer to main (ancestors, earlier changes)
- **Restack**: Rebasing descendant branches when parent changes

**Branch Philosophy**:
- One commit per branch (branches treated like commits)
- Break work into multiple branches, not multiple commits
- Each branch = atomic changeset

**PR Stacking**:
- Create dependent PRs that can be reviewed independently
- PR for branch B has base branch A (not main)
- When A merges, B auto-updates to target main

## Important Constraints

1. **Python Version**: Must target Python 3.14+
2. **Git Requirement**: Users must have Git installed (system dependency)
3. **GitHub Only**: V1 focuses on GitHub (GitLab/Bitbucket out of scope)
4. **Security**: Tokens stored in system keyring, never logged
5. **Performance**: Local operations <500ms, stack viz <1s for 50 branches
6. **State Management**: All branch metadata in .graphite/state.json (must handle corruption gracefully)

## Quick Reference: Command Summary

**Core Workflow**:
- `gt create [-a] [-m "msg"]` - Create branch in stack
- `gt submit [--stack]` - Submit branch(es) as PRs
- `gt modify [-a]` - Amend or add commits
- `gt sync` - Sync with remote, restack all

**Navigation**:
- `gt log [short|long]` - Visualize stack
- `gt up/down/top/bottom` - Move through stack
- `gt checkout` - Switch branches

**Manipulation**:
- `gt rename/delete/move` - Modify stack structure
- `gt split/squash/fold` - Advanced operations

**Setup**:
- `gt init` - Initialize Graphite in repo
- `gt auth` - Authenticate with GitHub
- `gt config` - Configure settings

## Future Enhancements (Out of Scope for V1)

Per requirements.md, these are explicitly deferred:
- VS Code extension
- Web dashboard
- GitLab/Bitbucket support
- Advanced conflict resolution UI
- Team analytics

## Development Phases (10-week plan)

1. **Weeks 1-2**: Foundation (project setup, Git wrapper, state management)
2. **Weeks 3-4**: Core stack operations (tracking, restack, visualization)
3. **Weeks 5-6**: GitHub integration (auth, PR creation/updates)
4. **Weeks 7-8**: Advanced features (modify, sync, navigation, manipulation)
5. **Weeks 9-10**: Polish (completion, help, docs, testing, optimization)

## Success Metrics for V1

From requirements.md:
- All core commands functional (create, submit, modify, sync)
- Stack visualization for up to 50 branches
- Reliable GitHub PR creation/updates
- Zero data loss in stack operations
- Comprehensive error handling with helpful messages
- 80%+ test coverage
- Complete user documentation
- Installable via pip

---

**Last Updated**: 2025-11-20
**Repository Type**: Planning/Specification (no implementation yet)
**Ready for**: Implementation kickoff
