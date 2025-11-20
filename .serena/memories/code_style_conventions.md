# Code Style & Conventions

## Code Style
- **Style Guide**: Google Python Style Guide
- **Line Length**: 100 characters maximum
- **Formatting**: Ruff (automated)
- **Linting**: Ruff with extensive rule set (E, W, F, I, N, D, UP, ANN, S, B, etc.)

## Type Hints & Documentation
- **Type Coverage**: Target 100% type hints for all functions
- **Type Checker**: Pyright in strict mode
- **Docstrings**: Google style docstrings required for all public APIs
- **Method Documentation**: Include examples in docstrings where helpful

## Naming Conventions
- **Functions/Variables**: snake_case
- **Classes**: PascalCase
- **Constants**: UPPER_SNAKE_CASE
- **Private Members**: Leading underscore (_private)
- **Exception Classes**: Follow Graphite prefix pattern (GraphiteException)

## File Organization
- **Modules**: One logical unit per file
- **Imports**: Organized with ruff/isort
- **Structure**: Models, utils, core services, CLI commands separated

## Error Handling
- **Exception Hierarchy**: Custom exceptions inherit from GraphiteException
- **Error Messages**: User-friendly, actionable error messages
- **Validation**: Use Pydantic for data validation

## Testing Requirements
- **Framework**: pytest + pytest-cov
- **Coverage**: 80%+ target
- **Test Types**: Unit, integration, E2E
- **Test Organization**: Mirror source structure in tests/