# Suggested Commands

## Development Commands

### Hatch Environment Management
```bash
# Create development environment
hatch env create

# Install project in development mode
pip install -e ".[dev]"
```

### Testing
```bash
# Run all tests
hatch run test

# Run tests with coverage
hatch run test-cov

# Run tests with coverage and generate HTML report
pytest --cov=graphite_cli --cov-report=term-missing --cov-report=html tests/
```

### Code Quality
```bash
# Run linting
hatch run lint
# Alternative: ruff check src tests

# Run auto-formatting
hatch run format
# Alternative: ruff format src tests

# Check formatting (no changes)
hatch run format-check
# Alternative: ruff format --check src tests

# Run type checking
hatch run type-check
# Alternative: pyright src

# Run security audit
hatch run security
# Alternative: bandit -r src -ll

# Run all checks
hatch run check-all
```

### Installation & Running
```bash
# Install from source
pip install -e .

# Run CLI (after installation)
gt --version
gt --help
```

### Git Operations
```bash
# Standard git operations
git status
git add .
git commit -m "message"
git push origin branch-name

# Branch operations for stacked PRs
git checkout -b task/T001-project-setup
git checkout -b task/T002-configure-tooling
```

### System Commands (Linux)
```bash
# File operations
ls -la
find . -name "*.py"
grep -r "pattern" src/
cd directory_name

# Python environment
python --version
pip list
pip freeze
```