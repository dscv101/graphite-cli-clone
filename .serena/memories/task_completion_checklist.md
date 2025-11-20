# Task Completion Checklist

## When Task Implementation is Complete

### 1. Code Quality Checks (Required)
```bash
# Format code
hatch run format

# Run linting
hatch run lint

# Type checking
hatch run type-check

# Security scan
hatch run security

# Or run all at once
hatch run check-all
```

### 2. Testing (Required)
```bash
# Run relevant tests
hatch run test

# Check coverage
hatch run test-cov

# Ensure coverage meets 80% target for new code
```

### 3. Validation Steps
- [ ] All new code follows Google Python style
- [ ] Type hints added to all new functions
- [ ] Docstrings added to all public APIs
- [ ] Error handling implemented appropriately
- [ ] Tests written for new functionality
- [ ] No security vulnerabilities (Bandit clean)
- [ ] Code formatted and linted (Ruff clean)
- [ ] Type checking passes (Pyright clean)

### 4. Git Workflow for Stacked PRs
```bash
# Create task branch
git checkout -b task/T{id}-{slug}

# Make changes and commit
git add .
git commit -m "T{id}: {description}"

# Push branch
git push origin task/T{id}-{slug}

# Create PR via GitHub CLI or web interface
gh pr create --title "T{id}: {title}" --body "{description}"
```

### 5. PR Requirements
- [ ] Branch named: `task/T{id}-{slug}`
- [ ] Commit message format: `T{id}: {description}`
- [ ] PR title format: `T{id}: {title}`
- [ ] All CI checks pass
- [ ] Code review requested if needed
- [ ] Links to related issues/tasks

### 6. Documentation Updates (if applicable)
- [ ] Update relevant .md files in project root
- [ ] Update docstrings and type hints
- [ ] Add examples to README if new user-facing feature