# Task DAG Plan - Graphite CLI Clone

## Overview

This document defines a Directed Acyclic Graph (DAG) of implementation tasks for the Graphite CLI Clone project. Tasks are organized for maximum parallelization while maintaining necessary dependencies. Each task is designed to be independently implementable by AI coding agents or human developers.

**Total Tasks**: 52  
**Estimated Total Effort**: 320-400 hours  
**Target Timeline**: 10 weeks with parallel execution

---

## Tasks

| task_id | title | description | type | component | prerequisites | estimated_effort | priority |
|---------|-------|-------------|------|-----------|---------------|------------------|----------|
| T001 | Project Setup | Initialize project structure with pyproject.toml, configure Hatch, set up source directory structure under src/graphite_cli/ | setup | infra | none | 4h | critical |
| T002 | Configure Tooling | Set up Ruff (Google style, line length 100), Pyright (strict mode, Python 3.14), Bandit, pytest, pytest-cov in pyproject.toml | setup | infra | none | 3h | critical |
| T003 | CI/CD Pipeline | Create GitHub Actions workflow for linting (Ruff), type checking (Pyright), security scanning (Bandit), and testing (pytest with coverage) | setup | infra | none | 4h | critical |
| T004 | Base Exception Classes | Implement exception hierarchy: GraphiteException, GitException, GitHubException, ValidationException, ConflictException, AuthenticationException in exceptions/ | backend | core | T001 | 3h | critical |
| T005 | Branch Model | Implement Branch dataclass with all fields, methods (is_submitted, get_children, get_ancestors) in models/branch.py | backend | models | T001 | 3h | critical |
| T006 | Stack Model | Implement Stack dataclass with methods (get_branch, get_stack_for_branch, get_upstack_branches, get_downstack_branches, validate_no_cycles) in models/stack.py | backend | models | T005 | 4h | critical |
| T007 | Repository Model | Implement Repository dataclass with methods (is_github_repo, get_github_repo_path) in models/repository.py | backend | models | T001 | 2h | high |
| T008 | Config Model | Implement GraphiteConfig dataclass with validation in models/config.py | backend | models | T001 | 3h | high |
| T009 | PullRequest Model | Implement PullRequest dataclass with is_mergeable method in models/pull_request.py | backend | models | T001 | 2h | high |
| T010 | Git Utility Functions | Implement git_utils.py with helper functions for Git operations (parse refs, validate branch names, etc.) | backend | utils | T001 | 3h | high |
| T011 | Branch Naming Utility | Implement branch_name.py with auto-generation logic, template parsing, date formatting | backend | utils | T001 | 3h | medium |
| T012 | Logging Setup | Implement logging.py with structured logging configuration, log levels, file output | backend | utils | T001 | 2h | medium |
| T013 | StateManager Implementation | Implement StateManager class with load/save state, branch metadata CRUD, tracked branches management in core/state_manager.py | backend | core | T001, T004, T005 | 5h | critical |
| T014 | ConfigManager Implementation | Implement ConfigManager class with load/save config (global + repo), keyring integration for tokens in core/config_manager.py | backend | core | T001, T004, T008 | 5h | critical |
| T015 | Validator Implementation | Implement Validator class with all validation methods (branch names, stack operations, uncommitted changes, relationships) in core/validator.py | backend | core | T001, T004, T005, T006 | 4h | critical |
| T016 | GitService - Basic Operations | Implement GitService with basic operations: get_current_branch, create_branch, checkout_branch, delete_branch in core/git_service.py | backend | core | T001, T004, T007, T010 | 6h | critical |
| T017 | GitService - Commit Operations | Extend GitService with commit operations: commit, get_commit_message, get_commits_between, has_uncommitted_changes | backend | core | T016 | 4h | critical |
| T018 | GitService - Rebase Operations | Extend GitService with rebase operations: rebase, get_merge_base, is_in_conflict | backend | core | T016 | 5h | critical |
| T019 | GitService - Remote Operations | Extend GitService with remote operations: push, fetch, pull, get_repository_info | backend | core | T016 | 4h | high |
| T020 | GitHubService - Authentication | Implement GitHubService with authentication, token validation, basic GitHub API setup in core/github_service.py | backend | core | T001, T004, T007, T009 | 4h | critical |
| T021 | GitHubService - PR Operations | Extend GitHubService with PR operations: create_pull_request, update_pull_request, get_pull_request, list_pull_requests | backend | core | T020 | 5h | critical |
| T022 | GitHubService - PR Status | Extend GitHubService with check_pr_status, get_pr_for_branch, merge_pull_request | backend | core | T021 | 4h | high |
| T023 | GitHubService - Caching | Implement caching mechanism in GitHubService (_get_cached, _set_cache) with TTL support | backend | core | T020 | 3h | medium |
| T024 | StackManager - Core Operations | Implement StackManager with load_stack, save_stack, create_branch in core/stack_manager.py | backend | core | T013, T015, T016, T006 | 6h | critical |
| T025 | StackManager - Restack Operations | Extend StackManager with restack_branch, restack_upstack, validate_stack | backend | core | T024, T018 | 5h | critical |
| T026 | StackManager - Manipulation | Extend StackManager with delete_branch, move_branch operations | backend | core | T024 | 4h | high |
| T027 | Rich Output Formatter | Implement formatter.py with output formatting utilities using Rich library in cli/output/ | backend | cli | T001 | 3h | high |
| T028 | Rich Renderer | Implement renderer.py with tree rendering, table rendering, progress bars using Rich in cli/output/ | backend | cli | T027 | 4h | high |
| T029 | Typer App Setup | Create main Typer app in cli/app.py with common options, error handling, context management | backend | cli | T001, T004 | 3h | critical |
| T030 | Create Command | Implement create command with all flags (-a, -m, name generation) in cli/commands/create.py | backend | cli | T024, T029 | 5h | critical |
| T031 | Submit Command | Implement submit command with stack submission, PR creation/update, body generation in cli/commands/submit.py | backend | cli | T021, T024, T029 | 6h | critical |
| T032 | Modify Command | Implement modify command with amend, new commit, interactive rebase in cli/commands/modify.py | backend | cli | T025, T029 | 5h | high |
| T033 | Sync Command | Implement sync command with fetch, pull, restack, conflict handling, cleanup in cli/commands/sync.py | backend | cli | T025, T029 | 6h | high |
| T034 | Log Command | Implement log command (short, long variants) with tree visualization in cli/commands/navigation.py | backend | cli | T024, T028, T029 | 5h | high |
| T035 | Navigation Commands | Implement checkout, up, down, top, bottom commands in cli/commands/navigation.py | backend | cli | T024, T029 | 4h | medium |
| T036 | Manipulation Commands | Implement rename, delete, move, reorder commands in cli/commands/manipulation.py | backend | cli | T026, T029 | 5h | medium |
| T037 | Split Command | Implement split command for splitting branch into multiple branches in cli/commands/manipulation.py | backend | cli | T026, T029 | 4h | low |
| T038 | Squash Command | Implement squash command for squashing multiple branches in cli/commands/manipulation.py | backend | cli | T026, T029 | 4h | low |
| T039 | Fold Command | Implement fold command for folding branch into parent in cli/commands/manipulation.py | backend | cli | T026, T029 | 3h | low |
| T040 | Collaboration Commands | Implement get, track, untrack commands in cli/commands/collaboration.py | backend | cli | T024, T029 | 4h | medium |
| T041 | Init Command | Implement init command for repository initialization in cli/commands/config.py | backend | cli | T014, T029 | 3h | high |
| T042 | Auth Command | Implement auth command with OAuth/token flow, keyring storage in cli/commands/config.py | backend | cli | T014, T020, T029 | 5h | critical |
| T043 | Config Command | Implement interactive config command in cli/commands/config.py | backend | cli | T014, T029 | 4h | medium |
| T044 | Merge Command | Implement merge command with mergeability checks, CI validation in cli/commands/merge.py | backend | cli | T022, T029 | 5h | medium |
| T045 | Continue Command | Implement continue command for resuming after conflict resolution in cli/commands/config.py | backend | cli | T025, T029 | 3h | medium |
| T046 | Git Passthrough | Implement unrecognized command passthrough to git in cli/app.py | backend | cli | T029 | 2h | low |
| T047 | Shell Completion | Implement completion command generating bash/zsh/fish scripts in cli/commands/config.py | backend | cli | T029 | 3h | low |
| T048 | Help System | Implement help command, --help flags, command documentation in cli/app.py | backend | cli | T029 | 3h | medium |
| T049 | Unit Tests - Models | Write pytest unit tests for all models (Branch, Stack, Repository, Config, PullRequest) | testing | test | T005, T006, T007, T008, T009 | 8h | critical |
| T050 | Unit Tests - Core Services | Write pytest unit tests for StateManager, ConfigManager, Validator, StackManager | testing | test | T013, T014, T015, T024, T025, T026 | 12h | critical |
| T051 | Integration Tests - Git | Write integration tests for GitService using temporary repositories | testing | test | T016, T017, T018, T019 | 10h | high |
| T052 | Integration Tests - GitHub | Write integration tests for GitHubService using mocked API | testing | test | T020, T021, T022, T023 | 10h | high |
| T053 | E2E Tests - Create Workflow | Write end-to-end test for create -> submit workflow | testing | test | T030, T031 | 6h | high |
| T054 | E2E Tests - Modify Workflow | Write end-to-end test for create -> modify -> submit workflow | testing | test | T030, T032, T031 | 6h | high |
| T055 | E2E Tests - Sync Workflow | Write end-to-end test for sync workflow with conflicts | testing | test | T033 | 6h | medium |
| T056 | README Documentation | Write comprehensive README.md with quick start, installation, examples | docs | docs | T030, T031, T033, T034 | 4h | high |
| T057 | Installation Guide | Write detailed installation.md with platform-specific instructions | docs | docs | none | 3h | medium |
| T058 | Command Reference | Write complete commands.md documenting all commands with examples | docs | docs | T030, T031, T032, T033, T034, T035, T036, T040, T041, T042, T043, T044 | 6h | high |
| T059 | Workflow Tutorials | Write workflow tutorials (basic stacking, collaboration, conflict resolution) | docs | docs | T058 | 5h | medium |
| T060 | Configuration Guide | Write configuration.md documenting all config options | docs | docs | T014, T043 | 3h | medium |
| T061 | Troubleshooting Guide | Write troubleshooting.md with common issues and solutions | docs | docs | T058 | 4h | low |
| T062 | Contributing Guide | Write CONTRIBUTING.md with development setup, testing, PR process | docs | docs | T002 | 3h | low |
| T063 | PyPI Package Setup | Configure package metadata, entry points, dependencies for PyPI in pyproject.toml | infra | release | T001, T002 | 2h | high |
| T064 | Build and Release Workflow | Create GitHub Actions workflow for building, testing, and publishing to PyPI | infra | release | T003, T063 | 3h | high |
| T065 | Performance Benchmarks | Create performance benchmark suite for critical operations (stack loading, restack) | testing | test | T024, T025 | 4h | low |
| T066 | Security Audit | Run comprehensive security audit with Bandit, review token storage, input validation | qa | qa | T014, T020 | 3h | medium |
| T067 | Type Coverage Check | Verify 100% type coverage with Pyright, add missing type hints | qa | qa | all backend tasks | 4h | medium |
| T068 | Test Coverage Report | Generate coverage report, ensure 80%+ coverage, identify gaps | qa | qa | T049, T050, T051, T052, T053, T054, T055 | 2h | high |
| T069 | Integration Testing | Manual integration testing of complete workflows on real repository | qa | qa | T030, T031, T032, T033, T034 | 6h | high |
| T070 | Bug Fixes and Polish | Address bugs found during testing, refine error messages, improve UX | qa | qa | T068, T069 | 12h | high |
| T071 | CHANGELOG | Write CHANGELOG.md documenting v0.1.0 features | docs | docs | T070 | 2h | medium |
| T072 | Release v0.1.0 | Tag release, publish to PyPI, create GitHub release with notes | infra | release | T064, T068, T070, T071 | 2h | high |

---

## DAG

```
# Foundation Stage
T001 -> T004, T005, T007, T008, T009, T010, T011, T012, T013, T014, T015, T016, T020, T027, T029, T063
T002 -> T003, T062, T063, T067
T003 -> T064

# Models Stage
T004 -> T013, T014, T015, T016, T020, T029
T005 -> T006, T013, T015, T049
T006 -> T024, T049
T007 -> T016, T020, T049
T008 -> T014, T049
T009 -> T020, T049
T010 -> T016
T011 -> (no direct dependents)
T012 -> (no direct dependents)

# Core Services Stage
T013 -> T024, T050
T014 -> T041, T042, T043, T050, T060, T066
T015 -> T024, T050
T016 -> T017, T018, T019, T024, T051
T017 -> T051
T018 -> T025, T051
T019 -> T051
T020 -> T021, T042, T052, T066
T021 -> T022, T031, T052
T022 -> T044, T052
T023 -> T052
T024 -> T025, T026, T030, T031, T034, T035, T040, T050, T065
T025 -> T032, T033, T045, T050, T065
T026 -> T036, T037, T038, T039, T050

# CLI Output Stage
T027 -> T028
T028 -> T034
T029 -> T030, T031, T032, T033, T034, T035, T036, T037, T038, T039, T040, T041, T042, T043, T044, T045, T046, T047, T048

# CLI Commands Stage
T030 -> T053, T054, T056, T058, T069
T031 -> T053, T054, T056, T058, T069
T032 -> T054, T058, T069
T033 -> T055, T056, T058, T069
T034 -> T056, T058, T069
T035 -> T058
T036 -> T058
T037 -> (no direct dependents)
T038 -> (no direct dependents)
T039 -> (no direct dependents)
T040 -> T058
T041 -> T058
T042 -> T058
T043 -> T058, T060
T044 -> T058
T045 -> (no direct dependents)
T046 -> (no direct dependents)
T047 -> (no direct dependents)
T048 -> (no direct dependents)

# Testing Stage
T049 -> T068
T050 -> T068
T051 -> T068
T052 -> T068
T053 -> T068
T054 -> T068
T055 -> T068

# Documentation Stage
T056 -> (no direct dependents)
T057 -> (no direct dependents)
T058 -> T059
T059 -> (no direct dependents)
T060 -> (no direct dependents)
T061 -> (no direct dependents)
T062 -> (no direct dependents)

# Release Stage
T063 -> T064
T064 -> T072
T065 -> (no direct dependents)
T066 -> T070
T067 -> T070
T068 -> T069, T070
T069 -> T070
T070 -> T071, T072
T071 -> T072
T072 -> (final task)
```

---

## Execution Stages

### Stage 0: Foundation (3 tasks parallel)
**Can start immediately - no dependencies**

```
T001: Project Setup
T002: Configure Tooling
T003: CI/CD Pipeline (depends on T002 internally, but can start in parallel)
```

**Duration**: ~4 hours (critical path)

---

### Stage 1: Models & Base Infrastructure (11 tasks parallel)
**Requires**: Stage 0 complete

```
T004: Base Exception Classes
T005: Branch Model
T007: Repository Model
T008: Config Model
T009: PullRequest Model
T010: Git Utility Functions
T011: Branch Naming Utility
T012: Logging Setup
T027: Rich Output Formatter
T063: PyPI Package Setup
T067: Type Coverage Check (can start but will need iteration)
```

**Duration**: ~4 hours (critical path)

---

### Stage 2: Complex Models & Early Services (7 tasks parallel)
**Requires**: Stage 1 complete

```
T006: Stack Model (needs T005)
T013: StateManager Implementation (needs T004, T005)
T014: ConfigManager Implementation (needs T004, T008)
T015: Validator Implementation (needs T004, T005, T006 - starts after T006)
T016: GitService - Basic Operations (needs T004, T007, T010)
T020: GitHubService - Authentication (needs T004, T007, T009)
T028: Rich Renderer (needs T027)
T029: Typer App Setup (needs T004)
T062: Contributing Guide (needs T002)
```

**Note**: T015 starts slightly after T006 completes

**Duration**: ~6 hours (critical path)

---

### Stage 3: Extended Services (10 tasks parallel)
**Requires**: Stage 2 complete

```
T017: GitService - Commit Operations
T018: GitService - Rebase Operations
T019: GitService - Remote Operations
T021: GitHubService - PR Operations
T024: StackManager - Core Operations (needs T013, T015, T016, T006)
T041: Init Command (needs T014, T029)
T042: Auth Command (needs T014, T020, T029)
T043: Config Command (needs T014, T029)
T057: Installation Guide
T064: Build and Release Workflow (needs T003, T063)
```

**Duration**: ~6 hours (critical path)

---

### Stage 4: Advanced Services & Core Commands (12 tasks parallel)
**Requires**: Stage 3 complete

```
T022: GitHubService - PR Status
T023: GitHubService - Caching
T025: StackManager - Restack Operations (needs T024, T018)
T026: StackManager - Manipulation (needs T024)
T030: Create Command (needs T024, T029)
T031: Submit Command (needs T021, T024, T029)
T034: Log Command (needs T024, T028, T029)
T035: Navigation Commands (needs T024, T029)
T040: Collaboration Commands (needs T024, T029)
T046: Git Passthrough
T047: Shell Completion
T048: Help System
```

**Duration**: ~6 hours (critical path)

---

### Stage 5: Remaining Commands & Unit Tests (15 tasks parallel)
**Requires**: Stage 4 complete

```
T032: Modify Command (needs T025, T029)
T033: Sync Command (needs T025, T029)
T036: Manipulation Commands (needs T026, T029)
T037: Split Command
T038: Squash Command
T039: Fold Command
T044: Merge Command (needs T022, T029)
T045: Continue Command (needs T025, T029)
T049: Unit Tests - Models (needs T005-T009)
T050: Unit Tests - Core Services (needs T013-T015, T024-T026)
T051: Integration Tests - Git (needs T016-T019)
T052: Integration Tests - GitHub (needs T020-T023)
T060: Configuration Guide (needs T014, T043)
T065: Performance Benchmarks (needs T024, T025)
T066: Security Audit (needs T014, T020)
```

**Duration**: ~12 hours (critical path)

---

### Stage 6: E2E Tests & Documentation (10 tasks parallel)
**Requires**: Stage 5 complete

```
T053: E2E Tests - Create Workflow (needs T030, T031)
T054: E2E Tests - Modify Workflow (needs T030, T032, T031)
T055: E2E Tests - Sync Workflow (needs T033)
T056: README Documentation (needs T030, T031, T033, T034)
T058: Command Reference (needs most commands)
T059: Workflow Tutorials (needs T058)
T061: Troubleshooting Guide (needs T058)
T068: Test Coverage Report (needs all test tasks)
```

**Duration**: ~10 hours (critical path)

---

### Stage 7: QA & Polish (2 tasks sequential)
**Requires**: Stage 6 complete

```
T069: Integration Testing (needs T030-T034, T068)
T070: Bug Fixes and Polish (needs T068, T069)
```

**Duration**: ~18 hours (sequential)

---

### Stage 8: Release (2 tasks sequential)
**Requires**: Stage 7 complete

```
T071: CHANGELOG (needs T070)
T072: Release v0.1.0 (needs T064, T068, T070, T071)
```

**Duration**: ~4 hours (sequential)

---

## Parallelization Summary

### Maximum Parallelization by Stage

- **Stage 0**: 3 parallel tasks
- **Stage 1**: 11 parallel tasks
- **Stage 2**: 9 parallel tasks
- **Stage 3**: 10 parallel tasks
- **Stage 4**: 12 parallel tasks
- **Stage 5**: 15 parallel tasks (peak parallelization)
- **Stage 6**: 10 parallel tasks
- **Stage 7**: 2 sequential tasks (QA bottleneck)
- **Stage 8**: 2 sequential tasks (release process)

### Critical Path Analysis

**Critical Path** (longest dependency chain):
```
T001 -> T005 -> T006 -> T024 -> T025 -> T033 -> T055 -> T068 -> T069 -> T070 -> T071 -> T072
```

**Critical Path Duration**: ~70 hours

**With Perfect Parallelization**: ~70 hours (critical path bottleneck)

**Realistic Timeline** (accounting for coordination, reviews, rework): 320-400 total hours, deliverable in 10 weeks with 3-4 developers working in parallel.

---

## Task Assignment Recommendations

### Backend Developer 1 (Core Services)
- T016-T019: GitService implementation
- T024-T026: StackManager implementation
- T049-T050: Unit tests for core services

### Backend Developer 2 (GitHub & State)
- T013: StateManager
- T014: ConfigManager
- T020-T023: GitHubService implementation
- T051-T052: Integration tests

### Backend Developer 3 (CLI Commands)
- T029: Typer app setup
- T030-T033: Core commands (create, submit, modify, sync)
- T034-T035: Navigation commands
- T053-T055: E2E tests

### Backend Developer 4 (CLI Commands & Features)
- T036-T039: Manipulation commands
- T040-T045: Collaboration, config, merge commands
- T046-T048: Passthrough, completion, help

### Frontend/DevOps Engineer
- T001-T003: Project setup and CI/CD
- T027-T028: Rich output formatting
- T063-T064: PyPI packaging and release automation

### QA Engineer
- T065-T070: Performance, security, coverage, integration testing, bug fixes

### Technical Writer
- T056-T062: All documentation tasks
- T071: CHANGELOG

---

## Risk Mitigation

### High-Risk Dependencies

1. **T024 (StackManager)** - Blocks many CLI commands
   - **Mitigation**: Prioritize this task, assign to most experienced developer
   - **Fallback**: Mock StackManager for parallel CLI development

2. **T068 (Test Coverage)** - Required before QA stage
   - **Mitigation**: Start test writing early, aim for incremental coverage
   - **Fallback**: Accept lower coverage for v0.1.0, improve in v0.2.0

3. **T070 (Bug Fixes)** - Unknown scope, can expand significantly
   - **Mitigation**: Allocate 20% buffer time, triage bugs by severity
   - **Fallback**: Defer non-critical bugs to v0.1.1 patch release

### Coordination Points

- **End of Stage 2**: Review data models, ensure consistency across services
- **End of Stage 4**: Review CLI command interfaces, ensure UX consistency
- **End of Stage 6**: Code freeze for testing, documentation review
- **End of Stage 7**: Final QA signoff before release

---

## AI Agent Execution Instructions

### Task Format for AI Agents

Each task should be executed with:

```yaml
task_id: T001
input_files:
  - requirements.md
  - design.md
output_files:
  - pyproject.toml
  - src/graphite_cli/__init__.py
  - README.md (initial)
validation:
  - Run: hatch env create
  - Verify directory structure exists
acceptance_criteria:
  - pyproject.toml contains all required sections
  - src/graphite_cli/ directory exists with __init__.py
  - Project can be installed with pip install -e .
```

### Parallel Execution Strategy

1. **Agent Pool**: Provision 4-6 AI coding agents
2. **Task Queue**: Maintain priority queue ordered by stage and priority
3. **Dependency Checking**: Before assigning task, verify all prerequisites complete
4. **Conflict Resolution**: Use separate branches per task, merge to integration branch
5. **Validation**: Each task runs linting, type checking, tests before marking complete

### GitHub Integration

Each task should create:
- **Branch**: `task/T{id}-{slug}` (e.g., `task/T001-project-setup`)
- **Issue**: Link to this DAG document, include acceptance criteria
- **PR**: Automated PR when task complete, request review
- **Labels**: `type:{type}`, `component:{component}`, `priority:{priority}`

---

## Success Metrics

### Completion Criteria

- **All Critical Tasks**: 100% complete (T001-T005, T013-T016, T020-T021, T024-T025, T029-T031, T049-T050)
- **All High Priority Tasks**: 100% complete
- **All Medium Priority Tasks**: ≥80% complete
- **Test Coverage**: ≥80%
- **Type Coverage**: 100%
- **Security Audit**: Zero critical vulnerabilities
- **Documentation**: README, installation guide, command reference complete

### Quality Gates

- **Stage 2 Exit**: All models pass unit tests, type checking passes
- **Stage 4 Exit**: Core commands (create, submit) functional in integration tests
- **Stage 6 Exit**: 80% test coverage achieved, all E2E tests passing
- **Stage 7 Exit**: Zero P0/P1 bugs, documentation complete

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-19  
**Status**: Ready for execution  
**Total Estimated Effort**: 320-400 hours  
**Target Completion**: 10 weeks with parallel execution
