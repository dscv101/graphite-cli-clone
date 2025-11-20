# Graphite CLI

A Python-based Git workflow tool that simplifies PR stacking for software development teams.

## Status

🚧 **Under Active Development** - This project is in early development stage (v0.1.0).

## Overview

Graphite CLI (`gt`) is a command-line tool that implements a "stack-based workflow" for Git, where each branch represents an atomic changeset. Branches depend on each other in a chain from trunk (main) to the most recent changes (upstack), enabling efficient PR stacking and review workflows.

## Key Features (Planned)

- **Stack-based workflow**: Manage dependent branches as a stack
- **PR stacking**: Create dependent PRs that can be reviewed independently  
- **Automatic rebasing**: Restack descendant branches when parents change
- **GitHub integration**: Seamless PR creation and updates
- **Rich CLI**: Beautiful terminal output with tree visualization

## Installation

```bash
pip install graphite-cli
```

Or install from source:

```bash
git clone https://github.com/graphite-cli/graphite-cli
cd graphite-cli
pip install -e .
```

## Quick Start

```bash
# Initialize Graphite in your repository
gt init

# Authenticate with GitHub
gt auth

# Create a new branch in the stack
gt create -m "Add new feature"

# Submit branch as a PR
gt submit

# Visualize your stack
gt log

# Sync with remote and restack all branches
gt sync
```

## Requirements

- Python 3.11+
- Git (system dependency)
- GitHub account

## Development

This project uses [Hatch](https://hatch.pypa.io/) for development.

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
hatch run test

# Run linting
hatch run lint

# Run type checking
hatch run type-check

# Run all checks
hatch run check-all
```

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
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
├── requirements.md       # Complete requirements specification
├── design.md             # Technical design document
└── task_dag.md           # Task breakdown with dependencies
```

## Documentation

- [Requirements](requirements.md) - Complete feature specifications
- [Design](design.md) - Technical architecture and implementation details
- [Task DAG](task_dag.md) - Development roadmap and task dependencies

## License

MIT

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Acknowledgments

Inspired by the original [Graphite](https://graphite.dev/) workflow tool.
