# Project Overview - Graphite CLI Clone

## Purpose
A Python-based Git workflow tool that simplifies PR stacking for software development teams. Implements a "stack-based workflow" where each branch represents an atomic changeset, with branches depending on each other in a chain from trunk (main) to the most recent changes (upstack).

## Current Status
- **Version**: 0.1.0 (Under Active Development)
- **Stage**: Early development with basic project structure in place
- **Total Tasks**: 72 tasks organized in 8 stages (T001-T072)
- **Estimated Effort**: 320-400 hours total, 10 weeks with 3-4 developers

## Key Features (Planned)
- Stack-based Git workflow management
- PR stacking with dependency handling
- Automatic rebasing and restacking
- GitHub integration
- Rich CLI with tree visualization
- Branch manipulation commands

## Current Implementation Status
Partially implemented:
- Basic project structure (src/graphite_cli/)
- CLI app entry point (Typer-based)
- Repository model with GitHub detection
- Branch naming utility
- Rich output formatter
- Exception base classes

## Next Steps
Need to implement 72 tasks starting with foundation:
- T001: Project Setup (partially done)
- T002: Configure Tooling 
- T003: CI/CD Pipeline
- Then models, core services, CLI commands, tests, docs, and release