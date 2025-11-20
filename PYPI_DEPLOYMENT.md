# PyPI Package Deployment Guide

This document provides instructions for building and deploying the `graphite-cli` package to PyPI.

## Package Metadata

- **Package Name**: `graphite-cli`
- **Version**: 0.1.0 (defined in `pyproject.toml`)
- **License**: MIT
- **Python Requirement**: >=3.11
- **Build System**: Hatchling (PEP 517/518 compliant)

## Prerequisites

### 1. Install Build Tools

```bash
python -m pip install --upgrade build twine
```

### 2. PyPI Account Setup

1. Create an account on [PyPI](https://pypi.org/) (production) and [TestPyPI](https://test.pypi.org/) (testing)
2. Set up 2FA (Two-Factor Authentication) for security
3. Create API tokens:
   - Go to Account Settings → API tokens
   - Create a token for `graphite-cli` package (or use a global token initially)
   - Save the token securely (you won't see it again)

### 3. Configure API Tokens

Create or edit `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-<your-production-token>

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-<your-test-token>
```

**Security Note**: Set restrictive permissions:
```bash
chmod 600 ~/.pypirc
```

## Package Configuration

The package is configured via `pyproject.toml` with the following key sections:

### Build Configuration

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Package Metadata

- **Name**: `graphite-cli` (install via `pip install graphite-cli`)
- **Entry Point**: `gt` command (defined in `[project.scripts]`)
- **Dependencies**: Listed in `[project.dependencies]`
- **Dev Dependencies**: Listed in `[project.optional-dependencies]`

### Entry Points

The package provides the `gt` CLI command:

```toml
[project.scripts]
gt = "graphite_cli.cli.app:main"
```

After installation, users can run:
```bash
gt --help
gt init
gt create
# etc.
```

## Building the Package

### 1. Clean Previous Builds

```bash
rm -rf dist/ build/ *.egg-info graphite_cli.egg-info
```

### 2. Build Distribution Packages

```bash
python -m build
```

This creates:
- `dist/graphite_cli-0.1.0-py3-none-any.whl` (wheel - for installation)
- `dist/graphite_cli-0.1.0.tar.gz` (sdist - source distribution)

### 3. Verify Package Integrity

```bash
# Check package metadata and README rendering
python -m twine check dist/*

# Inspect wheel contents
unzip -l dist/graphite_cli-0.1.0-py3-none-any.whl

# Inspect sdist contents  
tar -tzf dist/graphite_cli-0.1.0.tar.gz
```

Expected output:
```
Checking dist/graphite_cli-0.1.0-py3-none-any.whl: PASSED
Checking dist/graphite_cli-0.1.0.tar.gz: PASSED
```

## Testing the Package Locally

### 1. Install in a Clean Virtual Environment

```bash
# Create and activate a new virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install the wheel
pip install dist/graphite_cli-0.1.0-py3-none-any.whl

# Test the command
gt --version
gt --help

# Deactivate when done
deactivate
```

### 2. Test Import and Functionality

```bash
python -c "from graphite_cli.cli.app import main; print('Import successful!')"
```

## Deployment Process

### Step 1: Deploy to TestPyPI (Recommended First)

TestPyPI is a separate instance of PyPI for testing packages before production release.

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# You'll be prompted for username and password
# Use __token__ as username and your API token (including pypi- prefix) as password
# Or use credentials from ~/.pypirc
```

#### Test Installation from TestPyPI

```bash
# Create a new virtual environment
python -m venv test_install
source test_install/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    graphite-cli

# Test the installation
gt --version
gt --help

# Clean up
deactivate
rm -rf test_install
```

**Note**: The `--extra-index-url` is needed because dependencies will come from production PyPI.

### Step 2: Deploy to Production PyPI

Once testing is successful:

```bash
# Upload to production PyPI
python -m twine upload dist/*
```

After successful upload, the package will be available at:
- Package page: https://pypi.org/project/graphite-cli/
- Installation: `pip install graphite-cli`

## Post-Deployment Verification

### 1. Verify Package Availability

```bash
# Wait 1-2 minutes for PyPI to index the package
pip index versions graphite-cli
```

### 2. Test Production Installation

```bash
# Create a clean environment
python -m venv prod_test
source prod_test/bin/activate

# Install from production PyPI
pip install graphite-cli

# Verify installation
gt --version
pip show graphite-cli

# Clean up
deactivate
rm -rf prod_test
```

### 3. Check Package Page

Visit https://pypi.org/project/graphite-cli/ and verify:
- ✅ Package name and version correct
- ✅ Description renders properly
- ✅ Links (Homepage, Repository, Issues) work
- ✅ Dependencies listed correctly
- ✅ Classifiers displayed properly
- ✅ README.md renders correctly

## Version Management

### Semantic Versioning

This project follows [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR**: Incompatible API changes (e.g., 1.0.0 → 2.0.0)
- **MINOR**: Backwards-compatible functionality (e.g., 0.1.0 → 0.2.0)
- **PATCH**: Backwards-compatible bug fixes (e.g., 0.1.0 → 0.1.1)

### Updating Version

1. **Update `pyproject.toml`**:
   ```toml
   [project]
   version = "0.2.0"  # Increment according to SemVer
   ```

2. **Update `src/graphite_cli/__init__.py`**:
   ```python
   __version__ = "0.2.0"
   ```

3. **Create a git tag**:
   ```bash
   git tag -a v0.2.0 -m "Release version 0.2.0"
   git push origin v0.2.0
   ```

4. **Rebuild and deploy**:
   ```bash
   rm -rf dist/
   python -m build
   python -m twine upload dist/*
   ```

## Troubleshooting

### Build Failures

**Issue**: `ModuleNotFoundError: No module named 'hatchling'`
```bash
# Solution: Install hatchling
pip install hatchling
```

**Issue**: `error: Multiple top-level packages discovered`
```bash
# Solution: Check [tool.hatch.build.targets.wheel] configuration
# Ensure packages = ["src/graphite_cli"] is correct
```

### Upload Failures

**Issue**: `403 Forbidden: Invalid or non-existent authentication`
```bash
# Solution: Verify API token
# - Check ~/.pypirc has correct token
# - Ensure token hasn't expired
# - Generate a new token if needed
```

**Issue**: `400 Bad Request: File already exists`
```bash
# Solution: You can't re-upload the same version
# - Increment version number
# - Or use a post-release identifier (e.g., 0.1.0.post1)
```

### Installation Issues

**Issue**: `ERROR: Could not find a version that satisfies the requirement graphite-cli`
```bash
# Solution: Wait a few minutes for PyPI to index
# Or check if package name is correct
pip index versions graphite-cli
# or visit https://pypi.org/project/graphite-cli/ directly
```

**Issue**: Dependency conflicts
```bash
# Solution: Check dependency versions in pyproject.toml
# Use more flexible version ranges if needed:
# "typer>=0.12.0,<1.0.0" instead of "typer>=0.12.0"
```

## CI/CD Integration (Future)

### GitHub Actions Workflow

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Check package
      run: twine check dist/*
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

**Setup**:
1. Add `PYPI_API_TOKEN` to GitHub repository secrets
2. Create a release on GitHub
3. Package will automatically build and publish

## Security Best Practices

1. **Never commit credentials**:
   - Add `.pypirc` to `.gitignore`
   - Use GitHub Secrets for CI/CD tokens
   
2. **Use API tokens, not passwords**:
   - Create scoped tokens per package
   - Rotate tokens periodically
   
3. **Enable 2FA** on PyPI account

4. **Sign releases** (optional but recommended):
   ```bash
   gpg --detach-sign -a dist/graphite_cli-0.1.0.tar.gz
   twine upload dist/graphite_cli-0.1.0.tar.gz \
       dist/graphite_cli-0.1.0.tar.gz.asc
   ```

5. **Verify build reproducibility**:
   - Build in clean environments
   - Document build dependencies

## Package Maintenance

### Yanking a Release

If you discover critical issues after release:

```bash
# Via web interface at https://pypi.org/manage/project/graphite-cli/releases/

# Or via API
pip install pkginfo httpie
http POST https://pypi.org/api/projects/graphite-cli/releases/0.1.0/yank \
    "Authorization:Bearer $PYPI_TOKEN"
```

**Note**: Yanked releases are still available but discouraged for new installations.

### Monitoring

- **PyPI Stats**: https://pypistats.org/packages/graphite-cli
- **Download Stats**: Check PyPI project page
- **Security Advisories**: Monitor GitHub security alerts

## Resources

- **PyPI**: https://pypi.org/
- **TestPyPI**: https://test.pypi.org/
- **Packaging Guide**: https://packaging.python.org/
- **PEP 517**: https://peps.python.org/pep-0517/ (Build system specification)
- **PEP 518**: https://peps.python.org/pep-0518/ (pyproject.toml)
- **Hatchling Docs**: https://hatch.pypa.io/latest/
- **Twine Docs**: https://twine.readthedocs.io/

## Quick Reference

```bash
# Build package
python -m build

# Check package
twine check dist/*

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*

# Install locally for testing
pip install dist/graphite_cli-0.1.0-py3-none-any.whl

# Install from PyPI
pip install graphite-cli

# Verify installation
gt --version
```

## Support

For issues related to:
- **Package deployment**: File an issue on the repository
- **PyPI account**: Contact PyPI support at https://pypi.org/help/
- **Package functionality**: See CONTRIBUTING.md

---

**Last Updated**: 2024-11-20
**Package Version**: 0.1.0

