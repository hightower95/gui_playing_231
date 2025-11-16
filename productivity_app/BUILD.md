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

### Automated Build (Recommended)

Use the automated build script for smart version management:

```bash
# Run automated build - detects changes and auto-increments version
python package_builder.py

# Build without incrementing version
python package_builder.py --no-increment
```

The automated build script:
- ✅ Checks git status (refuses to build with uncommitted changes)
- ✅ Detects changes in source code and config files
- ✅ Auto-increments version number (patch/minor/major) or keeps current version
- ✅ Updates `pyproject.toml` with new version (unless `--no-increment` used)
- ✅ Builds both wheel and source distributions
- ✅ Provides next steps for testing and release

### Manual Build

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
# Install from wheel
pip install dist/productivity_app-0.1.0-py3-none-any.whl

# Test it works
python -c "import productivity_app; productivity_app.start()"
```

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

### Automated Version Management (Recommended)

The `package_builder.py` script handles version increments automatically:

- **Patch version** (0.1.0 → 0.1.1): Default for code changes
- **Minor version** (0.1.0 → 0.2.0): Use `--minor` flag  
- **Major version** (0.1.0 → 1.0.0): Use `--major` flag
- **No increment** (keeps current version): Use `--no-increment` flag

```bash
# Auto-increment patch version (default)
python package_builder.py

# Increment minor version
python package_builder.py --minor

# Increment major version  
python package_builder.py --major

# Build without changing version
python package_builder.py --no-increment
```

### Manual Version Management

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

**Package builder produces 0 files:**

1. **Check pyproject.toml exists and is valid:**
```bash
# Verify file exists
ls pyproject.toml

# Check content
Get-Content pyproject.toml | Select-String "name|version|build-system"
```

2. **Verify Python packages are detected:**
```bash
# Check for __init__.py files
ls productivity_app/__init__.py
ls productivity_app/productivity_core/__init__.py

# List all Python packages
Get-ChildItem -Recurse -Name "__init__.py"
```

3. **Check build tools:**
```bash
# Verify build module
python -c "import build; print('Build module found')"

# Install if missing
pip install build
```

4. **Manual build with verbose output:**
```bash
# Clean first
Remove-Item -Recurse -Force build, dist, *.egg-info -ErrorAction SilentlyContinue

# Build with verbose output
python -m build --verbose

# Check what was created
ls dist/
```

5. **Check current directory:**
```bash
# Ensure you're in the right directory
pwd
ls pyproject.toml  # Should exist

# Check directory structure
ls -la
```

6. **Validate environment:**
```bash
# Check Python version
python --version

# Check pip version
pip --version

# List installed packages
pip list | Select-String "build|setuptools|wheel"
```

**Manual diagnostic commands:**
```bash
# Full diagnostic check
python -c "
import sys, os
from pathlib import Path

print(f'Python: {sys.executable}')
print(f'Working dir: {os.getcwd()}')
print(f'pyproject.toml exists: {Path(\"pyproject.toml\").exists()}')

try:
    import build
    print(f'Build module: OK')
except ImportError:
    print(f'Build module: MISSING')

# Check for packages
for pkg_dir in Path('.').iterdir():
    if pkg_dir.is_dir() and (pkg_dir / '__init__.py').exists():
        print(f'Python package found: {pkg_dir.name}')
"
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
├── requirements-dev.txt # Dev dependencies
└── README.md            # This file
```

## Quick Reference

### Development Workflow
```bash
# Setup
pip install -e .[dev]

# Test
pytest --cov=app

# Format
black . && isort .

# Automated build (recommended)
python package_builder.py

# Publish
twine upload dist/*
```

### Build Script Features
- **Git Integration**: Validates clean working directory
- **Smart Detection**: Monitors source code and config changes
- **Auto Versioning**: Increments version automatically or keeps current version
- **Full Build**: Creates both wheel (.whl) and source (.tar.gz)
- **Next Steps**: Provides testing and release instructions

### Build Script Options
```bash
# Default patch increment
python package_builder.py

# Version increment options
python package_builder.py --minor
python package_builder.py --major
python package_builder.py --no-increment

# Help
python package_builder.py --help
```

### Manual Commands
```bash
# Manual build
python -m build

# Check git status
git status --porcelain

# View current version
grep version pyproject.toml
```

## Troubleshooting Build Issues

### Issue: "Built 0 files" or "No dist directory found"

This typically indicates the build process completed but didn't create any distribution files.

**Step-by-step diagnosis:**

1. **Verify you're in the correct directory:**
```bash
# Should be in productivity_app directory
pwd
ls pyproject.toml  # Must exist
```

2. **Check package structure:**
```bash
# Ensure main package exists
ls productivity_app/__init__.py

# Check for nested packages
ls productivity_app/productivity_core/__init__.py
```

3. **Validate pyproject.toml content:**
```bash
# Check for required sections
Get-Content pyproject.toml | Select-String "\[build-system\]|\[project\]|name.*=|version.*="
```

4. **Test build command directly:**
```bash
# Remove any existing build artifacts
Remove-Item -Recurse -Force build, dist, *.egg-info -ErrorAction SilentlyContinue

# Run build with maximum verbosity
python -m build --verbose --no-isolation

# Check if dist directory was created
ls dist/ -ErrorAction SilentlyContinue
```

5. **Environment verification:**
```bash
# Check Python and build tools
python --version
pip show build setuptools wheel
```

6. **Alternative build methods:**
```bash
# Try setuptools directly
python -m pip install -e .

# Or use setup.py if it exists
python setup.py bdist_wheel
```

### Issue: Package builder script fails silently

The enhanced package builder includes comprehensive diagnostics. Look for these key messages:

- `[VALIDATE] Checking pyproject.toml content...` - Config file validation
- `[PACKAGE-CHECK] Looking for Python packages...` - Package detection
- `[DEBUG] About to start build process...` - Build attempt checkpoint
- `[INFO] Using Python: ...` - Python executable confirmation
- `[DEBUG] About to run subprocess with:` - Exact build command

If any of these messages are missing, the script is failing at that specific step.
