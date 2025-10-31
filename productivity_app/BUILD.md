# Building Productivity App

Instructions for building and distributing the Productivity App package.

## Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

## Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/productivity-app.git
cd productivity-app

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
# source .venv/bin/activate    # Linux/macOS

# Install in editable mode with dev dependencies
pip install -e .[dev]
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# View coverage report
# Open htmlcov/index.html
```

## Code Quality

```bash
# Format code
black .
isort .

# Lint
flake8 app/

# Type check
mypy app/
```

## Building Distribution

```bash
# Clean old builds
Remove-Item -Recurse -Force build, dist, *.egg-info -ErrorAction SilentlyContinue

# Build wheel and source distribution
python -m build

# Output in dist/:
# - productivity_app-0.1.0-py3-none-any.whl
# - productivity_app-0.1.0.tar.gz
```

## Testing the Build

```bash
# Create a fresh virtual environment for testing
python -m venv .venv-test
.\.venv-test\Scripts\Activate.ps1

# Install from wheel
pip install dist/productivity_app-0.1.0-py3-none-any.whl

# Test that it imports correctly
python -c "import productivity_app; print(f'✓ Successfully installed v{productivity_app.__version__}')"

# Clean up test environment
deactivate
Remove-Item -Recurse -Force .venv-test
```

**Note:** Don't call `productivity_app.start()` in the test as it will launch the GUI application.

## Publishing to PyPI

```bash
# Install twine
pip install twine

# Check distribution files
twine check dist/*

# Upload to Test PyPI (recommended first)
twine upload --repository testpypi dist/*

# Test install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ productivity-app

# Upload to Production PyPI
twine upload dist/*
```

## Version Management

Update version in `pyproject.toml`:

```toml
[project]
version = "0.2.0"  # Update this
```

Then rebuild:

```bash
# Clean and rebuild
Remove-Item -Recurse -Force build, dist, *.egg-info -ErrorAction SilentlyContinue
python -m build
```

## Common Issues

**Build module not found:**
```bash
pip install build
```

**Import errors after install:**
```bash
pip install -e .  # Reinstall in editable mode
```

**Tests fail:**
```bash
pip install -e .[dev]  # Ensure dev dependencies installed
```

## Development Dependencies

Included in `[dev]` optional dependencies:

- **Testing**: pytest, pytest-qt, pytest-cov
- **Formatting**: black, isort
- **Linting**: flake8, pylint, mypy
- **Building**: build, twine, wheel

Install all at once:
```bash
pip install -e .[dev]
```

## Project Structure

```
productivity_app/
├── app/                  # Application code
├── docs/                 # Documentation
├── tests/                # Test files
├── main.py              # Entry point
├── pyproject.toml       # Build configuration
└── README.md            # This file
```

## Quick Reference

```bash
# Setup
pip install -e .[dev]

# Test
pytest --cov=app

# Format
black . && isort .

# Build
python -m build

# Publish
twine upload dist/*
```
