# Building Productivity App

This guide covers how to build, test, and distribute the Productivity App library.

## Table of Contents
- [Development Setup](#development-setup)
- [Building the Package](#building-the-package)
- [Running Tests](#running-tests)
- [Code Quality](#code-quality)
- [Publishing](#publishing)
- [Project Structure](#project-structure)

## Development Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/productivity-app.git
cd productivity-app
```

### 2. Create a Virtual Environment
**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Development Dependencies
```bash
# Install the package in editable mode with all dev dependencies
pip install -e .[dev]

# OR install from requirements-dev.txt
pip install -r requirements-dev.txt
pip install -e .
```

### 4. Verify Installation
```bash
# Run the application
productivity-app

# OR run directly
python main.py
```

## Building the Package

### Build from Source
```bash
# Install build tools if not already installed
pip install build

# Build the distribution packages
python -m build

# This creates two files in the dist/ directory:
# - productivity_app-0.1.0-py3-none-any.whl (wheel distribution)
# - productivity_app-0.1.0.tar.gz (source distribution)
```

### Build Output
```
dist/
├── productivity_app-0.1.0-py3-none-any.whl
└── productivity_app-0.1.0.tar.gz
```

### Installing from Built Package
```bash
# Install the wheel file
pip install dist/productivity_app-0.1.0-py3-none-any.whl

# OR install from source tarball
pip install dist/productivity_app-0.1.0.tar.gz
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Tests with Coverage
```bash
pytest --cov=app --cov-report=html

# View coverage report
# Open htmlcov/index.html in a browser
```

### Run Specific Tests
```bash
# Run tests in a specific file
pytest tests/test_connectors.py

# Run a specific test
pytest tests/test_connectors.py::test_connector_model

# Run tests matching a pattern
pytest -k "test_connector"
```

### Test with Different Python Versions (using tox)
```bash
# Install tox
pip install tox

# Run tests on all configured Python versions
tox
```

## Code Quality

### Format Code with Black
```bash
# Format all Python files
black .

# Check without making changes
black --check .
```

### Sort Imports with isort
```bash
# Sort imports
isort .

# Check without making changes
isort --check-only .
```

### Run Linter (flake8)
```bash
# Check code style
flake8 app/

# With specific configuration
flake8 --max-line-length=100 app/
```

### Type Checking with mypy
```bash
# Run type checker
mypy app/
```

### Run All Quality Checks
```bash
# Format code
black .
isort .

# Check quality
flake8 app/
mypy app/
pytest
```

### Pre-commit Hooks (Recommended)
```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Publishing

### Test PyPI (Recommended First)
```bash
# Build the package
python -m build

# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ productivity-app
```

### Production PyPI
```bash
# Upload to PyPI
twine upload dist/*

# Installation from PyPI
pip install productivity-app
```

### Version Management

Update version in `pyproject.toml`:
```toml
[project]
name = "productivity-app"
version = "0.2.0"  # Update this
```

Then rebuild:
```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info

# Build new version
python -m build
```

## Project Structure

```
productivity-app/
├── app/                       # Main application package
│   ├── __init__.py
│   ├── main.py               # Entry point
│   ├── core/                 # Core functionality
│   │   ├── app_context.py
│   │   ├── background_worker.py
│   │   ├── base_model.py
│   │   └── base_presenter.py
│   ├── tabs/                 # Main tabs
│   │   ├── main_window.py
│   │   └── settings_tab.py
│   ├── connector/            # Connector module
│   ├── epd/                  # EPD module
│   ├── document_scanner/     # Document scanner module
│   ├── remote_docs/          # Remote docs module
│   ├── devops/              # Azure DevOps module
│   └── ui/                  # UI components
├── tests/                    # Test files
│   ├── __init__.py
│   └── test_*.py
├── docs/                     # Documentation
├── pyproject.toml           # Project configuration (TOML)
├── requirements-dev.txt     # Development dependencies
├── BUILD.md                 # This file
├── README.md                # Project overview
├── LICENSE                  # License file
├── MANIFEST.in             # Include additional files
└── .gitignore              # Git ignore rules
```

## Common Development Tasks

### Clean Build Artifacts
```bash
# Remove build artifacts
rm -rf build/ dist/ *.egg-info

# Remove Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

**Windows PowerShell:**
```powershell
# Remove build artifacts
Remove-Item -Recurse -Force build, dist, *.egg-info -ErrorAction SilentlyContinue

# Remove Python cache
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Filter *.pyc | Remove-Item -Force
```

### Generate Documentation
```bash
# Install documentation dependencies
pip install -e .[docs]

# Generate docs with Sphinx
cd docs
sphinx-build -b html . _build/html

# View docs
# Open docs/_build/html/index.html
```

### Update Dependencies
```bash
# Update all packages
pip install --upgrade -e .[dev]

# Update specific package
pip install --upgrade PySide6
```

## Troubleshooting

### Build Fails
- Ensure you're in the project root directory
- Check Python version: `python --version`
- Update build tools: `pip install --upgrade build setuptools wheel`

### Import Errors
- Ensure package is installed in editable mode: `pip install -e .`
- Check PYTHONPATH includes the project directory
- Verify virtual environment is activated

### Tests Fail
- Install test dependencies: `pip install -e .[dev]`
- Check Qt platform plugin is available
- Run with verbose output: `pytest -v`

## CI/CD Integration

### GitHub Actions Example
Create `.github/workflows/python-package.yml`:
```yaml
name: Python Package

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11"]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install -e .[dev]
    - name: Run tests
      run: |
        pytest --cov=app
    - name: Check code quality
      run: |
        black --check .
        flake8 app/
```

## Additional Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [setuptools Documentation](https://setuptools.pypa.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [PySide6 Documentation](https://doc.qt.io/qtforpython/)

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests and quality checks
5. Commit: `git commit -m "Add feature"`
6. Push: `git push origin feature-name`
7. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
