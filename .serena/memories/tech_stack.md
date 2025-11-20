# Tech Stack & Dependencies

## Core Technology Stack
- **Language**: Python 3.11+ (strict requirement)
- **Package Manager**: Hatch (modern Python packaging)
- **CLI Framework**: Typer ≥0.12.0
- **Output Formatting**: Rich ≥13.7.0
- **Git Operations**: GitPython ≥3.1.40
- **GitHub API**: PyGithub ≥2.1.1
- **Secure Storage**: keyring ≥24.3.0
- **Data Validation**: Pydantic ≥2.5.0

## Development Dependencies
- **Testing**: pytest ≥7.4.3, pytest-cov ≥4.1.0
- **Linting**: Ruff ≥0.1.6 (Google Python style, 100 char lines)
- **Type Checking**: Pyright ≥1.1.338 (strict mode)
- **Security**: Bandit ≥1.7.5

## Project Structure
```
graphite-cli/
├── src/graphite_cli/     # Source code
│   ├── cli/              # CLI commands and output
│   ├── core/             # Core services (Git, GitHub, Stack management)
│   ├── models/           # Data models
│   ├── utils/            # Utility functions
│   └── exceptions/       # Exception classes
├── tests/                # Test suite
└── docs/                 # Documentation
```

## Architecture Layers
1. **CLI Entry Point** (Typer)
2. **Command Router** (create/submit/modify/sync/etc.)
3. **Core Services** (StackManager, GitService, GitHubService, etc.)
4. **Data Layer** (Git repo, .graphite/ directory, system keyring)

## Key Data Models
- Branch, Stack, Repository, Config, PullRequest