# Productivity App - Quick Start Guide

## 🚀 Quick Reference for Common Tasks

This guide provides quick commands and workflows for using and developing Productivity App.

## 📦 Installation

### For End Users

```bash
# Install from PyPI (when published)
pip install productivity-app

# Run the application
productivity-app
```

### For Developers

```bash
# Clone repository
git clone https://github.com/yourusername/productivity-app.git
cd productivity-app

# Create virtual environment (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install in editable mode with dev dependencies
pip install -e .[dev]
```

## 🏃 Running the Application

### As Installed Command
```bash
# After pip installation
productivity-app
```

### Running Directly
```bash
# From project directory
python main.py

# OR as a module
python -m app.main
```

### As Library in Your Code
```python
from app.core.app_context import AppContext
from app.core.config_manager import ConfigManager
from app.document_scanner.document_scanner_model import DocumentScannerModel

# Initialize configuration
ConfigManager.initialize()

# Create app context
context = AppContext()

# Use document scanner
model = DocumentScannerModel(context)
model.load_from_config()

# Access searchable documents
documents = model.get_searchable_documents()
```

## � Development Commands

### Code Formatting
```bash
# Format Python code with Black
black .

# Sort imports with isort
isort .

# Do both
black . ; isort .
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Generate HTML coverage report
pytest --cov=app --cov-report=html
# Open htmlcov/index.html

# Run specific test file
pytest tests/test_connector/

# Run tests matching pattern
pytest -k "test_search"
```

### Code Quality Checks
```bash
# Lint with flake8
flake8 app/

# Type check with mypy
mypy app/

# Run all quality checks
black --check . ; isort --check . ; flake8 app/ ; mypy app/
```

## 🏗️ Building & Distribution

### Build Distribution Packages
```bash
# Install build tool
pip install build

# Clean old builds
Remove-Item -Recurse -Force build, dist, *.egg-info -ErrorAction SilentlyContinue

# Build wheel and source distribution
python -m build

# Output:
# dist/productivity_app-0.1.0-py3-none-any.whl
# dist/productivity_app-0.1.0.tar.gz
```

### Test Installation
```bash
# Install from local wheel
pip install dist/productivity_app-0.1.0-py3-none-any.whl

# Verify installation
productivity-app --version
```

### Publish to PyPI
```bash
# Install twine
pip install twine

# Check distribution
twine check dist/*

# Upload to Test PyPI first (recommended)
twine upload --repository testpypi dist/*

# Upload to Production PyPI
twine upload dist/*
```

## 🔑 Key Features

### Main Modules

#### Connector Management
- Search and filter connectors
- Multi-select for bulk operations
- Recent searches history
- Advanced filtering and grouping

#### Document Scanner
- Load multiple document sources (CSV, Excel, TXT)
- Excel sheet selection
- Local and cached document types
- Full-text search across all documents
- Configuration export/import

#### EPD (Engineering Product Data)
- Load and display EPD data
- Advanced search and filtering
- Column-based grouping
- Data export capabilities

#### Azure DevOps Integration
- Work item queries
- Project and sprint management
- PAT authentication
- Query history

#### Remote Documentation
- Access remote documentation
- Search documentation
- Bookmark management

## 📋 Common Workflows

### Add a New Document to Scanner

1. Open Document Scanner tab
2. Click "Add Document"
3. Select file (CSV/Excel/TXT)
4. For Excel: select sheet from dropdown
5. Set document type (Local or Cached)
6. Configure column mappings
7. Click "Save"

### Search Across All Documents

1. Enter search term in search box
2. Press Enter or click Search
3. Results show matches from all documents
4. Click result to view details

### Export Connector Data

1. Open Connectors tab
2. Select connectors using checkboxes
3. Click "Export Selected"
4. Choose export format
5. Save to file

### Run Azure DevOps Query

1. Open DevOps tab
2. Configure connection in Settings
3. Enter WIQL query or select saved query
4. Click "Run Query"
5. View results in table

## 📁 Project Structure

```
productivity-app/
├── app/                      # Main application package
│   ├── __init__.py          # Package initialization
│   ├── main.py              # Application entry point
│   ├── core/                # Core infrastructure
│   │   ├── app_context.py
│   │   ├── background_worker.py
│   │   ├── base_model.py
│   │   └── base_presenter.py
│   ├── tabs/                # Main UI tabs
│   │   ├── main_window.py
│   │   └── settings_tab.py
│   ├── connector/           # Connector management
│   ├── document_scanner/    # Document scanning
│   ├── epd/                 # EPD module
│   ├── devops/              # Azure DevOps
│   ├── remote_docs/         # Documentation viewer
│   ├── ui/                  # UI components
│   └── shared/              # Shared utilities
├── docs/                    # Documentation
│   ├── INDEX.md
│   └── *.md                 # Feature documentation
├── tests/                   # Test files
├── main.py                  # Entry point script
├── pyproject.toml           # Package configuration
├── requirements-dev.txt     # Dev dependencies
├── BUILD.md                 # Build instructions
├── CONTRIBUTING.md          # Developer guide
├── CHANGELOG.md             # Version history
├── QUICK_START.md           # This file
├── README.md                # Project overview
├── LICENSE                  # MIT License
└── MANIFEST.in              # Package data rules
```

## 🔧 Git Workflow

### Feature Development
```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/my-new-feature

# Make changes, then stage and commit
git add .
git commit -m "feat(module): add new feature"

# Push to remote
git push origin feature/my-new-feature

# Create Pull Request on GitHub
```

### Bug Fix
```bash
# Create bug fix branch
git checkout -b fix/bug-description

# Fix the bug, then commit
git add .
git commit -m "fix(module): resolve issue with X"

# Push and create PR
git push origin fix/bug-description
```

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: feat, fix, docs, style, refactor, test, chore

## 🐛 Troubleshooting

### Application Won't Start
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall
pip uninstall productivity-app
pip install productivity-app
```

### Import Errors
```bash
# Ensure installed in dev mode
pip install -e .[dev]

# Check for missing dependencies
pip check
```

### Qt Platform Plugin Error
```bash
# Reinstall PySide6
pip install --force-reinstall PySide6
```

### Tests Failing
```bash
# Update test dependencies
pip install --upgrade pytest pytest-qt pytest-cov

# Clear cache
Remove-Item -Recurse -Force .pytest_cache

# Run with verbose output
pytest -v
```

### Build Fails
```bash
# Update build tools
pip install --upgrade build setuptools wheel

# Clean old builds
Remove-Item -Recurse -Force build, dist, *.egg-info

# Rebuild
python -m build
```

### Module Not Found After Install
```bash
# Ensure you're in correct directory
cd path\to\productivity-app

# Reinstall
pip install -e .
```

## � Documentation

- **[BUILD.md](BUILD.md)** - Comprehensive build and distribution guide
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development guidelines and code style
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes
- **[README.md](README.md)** - Project overview and features
- **[docs/INDEX.md](docs/INDEX.md)** - Documentation hub
- **[LICENSE](LICENSE)** - MIT License

### Feature Documentation (docs/)
- Document Scanner implementation
- Connector context and search
- Azure DevOps integration
- EPD viewer guide
- Configuration management

## 🔗 Useful Links

- **Repository**: https://github.com/yourusername/productivity-app
- **Issues**: https://github.com/yourusername/productivity-app/issues
- **Discussions**: https://github.com/yourusername/productivity-app/discussions
- **PyPI**: https://pypi.org/project/productivity-app (when published)

## 📋 Quick Command Reference

```bash
# Install
pip install productivity-app          # From PyPI
pip install -e .[dev]                 # Dev mode

# Run
productivity-app                      # Installed command
python main.py                        # Direct

# Develop
black .                               # Format
isort .                               # Sort imports
pytest --cov=app                      # Test
flake8 app/                          # Lint
mypy app/                            # Type check

# Build
python -m build                       # Build package
twine check dist/*                    # Validate
twine upload dist/*                   # Publish

# Clean
Remove-Item -Recurse -Force build, dist, *.egg-info, __pycache__, .pytest_cache
```
