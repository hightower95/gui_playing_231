# Contributing to Productivity App

Thank you for your interest in contributing to Productivity App! This guide will help you get started.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Project Architecture](#project-architecture)

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the best outcome for the project
- Show empathy towards other contributors

## Getting Started

### 1. Set Up Development Environment

See [BUILD.md](BUILD.md) for detailed setup instructions. Quick start:

```bash
# Clone and enter directory
git clone https://github.com/yourusername/productivity-app.git
cd productivity-app

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate    # Linux/macOS

# Install in development mode
pip install -e .[dev]
```

### 2. Create a Branch

```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name

# OR for bug fixes
git checkout -b fix/bug-description
```

### 3. Make Your Changes

Follow the guidelines below while developing.

## Development Workflow

### Running the Application

```bash
# Run from command line
productivity-app

# OR run the main script directly
python main.py
```

### Development Cycle

1. **Write Code** - Implement your feature/fix
2. **Format Code** - Run `black .` and `isort .`
3. **Run Tests** - Execute `pytest`
4. **Check Quality** - Run `flake8 app/` and `mypy app/`
5. **Commit** - Write clear commit message
6. **Push** - Push to your fork
7. **Pull Request** - Submit PR for review

### Quick Quality Check Script

Create a file `check.sh` (or `check.ps1` for Windows):

```bash
#!/bin/bash
echo "Formatting code..."
black .
isort .

echo "Running linter..."
flake8 app/

echo "Type checking..."
mypy app/

echo "Running tests..."
pytest --cov=app

echo "All checks complete!"
```

**Windows PowerShell version (`check.ps1`):**
```powershell
Write-Host "Formatting code..." -ForegroundColor Green
black .
isort .

Write-Host "Running linter..." -ForegroundColor Green
flake8 app/

Write-Host "Type checking..." -ForegroundColor Green
mypy app/

Write-Host "Running tests..." -ForegroundColor Green
pytest --cov=app

Write-Host "All checks complete!" -ForegroundColor Green
```

## Code Style Guidelines

### Python Style

We follow **PEP 8** with some modifications configured in `pyproject.toml`.

#### Formatting with Black

```bash
# Format all files
black .

# Check without changes
black --check .
```

**Configuration:**
- Line length: 100 characters
- Target Python versions: 3.8+

#### Import Sorting with isort

```bash
# Sort imports
isort .
```

**Configuration:**
- Profile: black (compatible with Black formatter)
- Multi-line mode: vertical hanging indent

#### Example Well-Formatted Code

```python
"""Module docstring describing the module."""

from typing import List, Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget

from app.core.app_context import AppContext
from app.core.base_presenter import BasePresenter


class MyPresenter(BasePresenter):
    """Presenter for my feature.
    
    Attributes:
        context: Application context for dependency injection
        view: The associated view component
    """
    
    data_changed = Signal(dict)
    
    def __init__(self, context: AppContext, view: QWidget):
        """Initialize the presenter.
        
        Args:
            context: Application context
            view: Associated view widget
        """
        super().__init__()
        self.context = context
        self.view = view
        self._data: Optional[dict] = None
    
    def load_data(self) -> None:
        """Load data from the model."""
        try:
            model = self.context.get("my_model")
            self._data = model.fetch_data()
            self.data_changed.emit(self._data)
        except Exception as e:
            self.log_error(f"Failed to load data: {e}")
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `ConnectorPresenter`)
- **Functions/Methods**: `snake_case` (e.g., `load_connectors`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_COUNT`)
- **Private members**: Prefix with `_` (e.g., `_internal_method`)
- **Signals**: Descriptive names (e.g., `data_changed`, `search_completed`)

### Documentation

#### Docstrings

Use Google-style docstrings:

```python
def process_data(data: List[dict], filter_type: str = "all") -> List[dict]:
    """Process and filter data records.
    
    This function applies filtering based on the specified type and
    performs data validation.
    
    Args:
        data: List of data records to process
        filter_type: Type of filter to apply ("all", "active", "pending")
    
    Returns:
        Filtered and validated list of data records
    
    Raises:
        ValueError: If filter_type is invalid
        
    Example:
        >>> records = [{"id": 1, "status": "active"}]
        >>> process_data(records, filter_type="active")
        [{"id": 1, "status": "active"}]
    """
    if filter_type not in ["all", "active", "pending"]:
        raise ValueError(f"Invalid filter_type: {filter_type}")
    # Implementation...
```

#### Comments

```python
# Good: Explain WHY, not WHAT
# Using binary search for O(log n) performance on sorted data
result = binary_search(sorted_list, target)

# Bad: Redundant comment
# Increment counter by 1
counter += 1
```

### Type Hints

Use type hints for all function signatures:

```python
from typing import List, Optional, Dict, Any

def fetch_records(
    record_ids: List[int],
    include_deleted: bool = False
) -> Optional[Dict[str, Any]]:
    """Fetch records by IDs."""
    pass
```

## Testing Guidelines

### Test Structure

Place tests in the `tests/` directory mirroring the `app/` structure:

```
tests/
├── __init__.py
├── test_core/
│   ├── test_app_context.py
│   └── test_background_worker.py
├── test_connector/
│   └── test_connector_presenter.py
└── test_epd/
    └── test_epd_model.py
```

### Writing Tests

#### Test Naming

```python
def test_connector_model_loads_from_csv():
    """Test that ConnectorModel successfully loads data from CSV file."""
    pass

def test_presenter_handles_empty_search_results():
    """Test presenter correctly handles empty search results."""
    pass
```

#### Test Structure (Arrange-Act-Assert)

```python
def test_search_filters_by_keyword():
    """Test that search correctly filters results by keyword."""
    # Arrange
    data = [
        {"name": "Connector A", "type": "Power"},
        {"name": "Connector B", "type": "Signal"},
    ]
    presenter = ConnectorPresenter(context=mock_context)
    presenter.set_data(data)
    
    # Act
    results = presenter.search("Power")
    
    # Assert
    assert len(results) == 1
    assert results[0]["name"] == "Connector A"
```

#### Testing Qt Components

```python
from pytestqt.qtbot import QtBot

def test_button_click_triggers_search(qtbot: QtBot):
    """Test that clicking search button triggers search."""
    view = ConnectorView()
    qtbot.addWidget(view)
    
    # Set up signal spy
    with qtbot.waitSignal(view.search_requested, timeout=1000):
        qtbot.mouseClick(view.search_button, Qt.LeftButton)
```

#### Mocking

```python
from unittest.mock import Mock, patch

def test_loads_data_from_file():
    """Test data loading with mocked file access."""
    mock_file_content = "id,name\n1,Test\n"
    
    with patch("builtins.open", mock_open(read_data=mock_file_content)):
        model = MyModel()
        data = model.load_from_csv("fake_path.csv")
        
    assert len(data) == 1
    assert data[0]["name"] == "Test"
```

### Coverage Requirements

- Aim for **80%+ code coverage**
- All new features must include tests
- Bug fixes should include regression tests

```bash
# Run with coverage
pytest --cov=app --cov-report=html

# View report
# Open htmlcov/index.html
```

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

#### Examples

```
feat(connector): add multi-select for bulk operations

Implemented checkbox selection allowing users to select multiple
connectors for batch operations like export or delete.

Closes #123
```

```
fix(epd): resolve data loading error for empty files

Fixed AttributeError when loading EPD data from empty CSV files.
Now shows user-friendly message instead of crashing.

Fixes #456
```

```
docs(readme): update installation instructions

Added section for installing from PyPI and clarified
virtual environment setup steps.
```

### Commit Best Practices

- **One logical change per commit**
- **Write clear, descriptive messages**
- **Reference issue numbers** when applicable
- **Keep commits atomic** (easily reversible)

## Pull Request Process

### 1. Ensure Quality

Before submitting PR:

```bash
# Format code
black .
isort .

# Run all checks
flake8 app/
mypy app/
pytest --cov=app
```

### 2. Update Documentation

- Update README.md if adding features
- Add docstrings to new functions/classes
- Update relevant .md files in `docs/`

### 3. Create Pull Request

**PR Title Format:**
```
[Type] Brief description
```

Examples:
- `[Feature] Add Excel sheet selection for Document Scanner`
- `[Fix] Resolve connector search crash on empty query`
- `[Refactor] Simplify Settings tab checkbox management`

**PR Description Template:**

```markdown
## Description
Brief description of changes

## Motivation
Why is this change needed?

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
How was this tested?
- [ ] Unit tests added/updated
- [ ] Manual testing performed
- [ ] All existing tests pass

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Code follows project style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] All tests pass
- [ ] No new warnings
```

### 4. Code Review

- Respond to feedback promptly
- Make requested changes in new commits
- Don't force-push after review starts
- Mark conversations as resolved when addressed

### 5. Merging

- **Squash and merge** for feature branches
- **Rebase and merge** for clean history
- Delete branch after merge

## Project Architecture

### MVP Pattern

Productivity App follows **Model-View-Presenter** architecture:

```
┌─────────┐         ┌───────────┐         ┌─────────┐
│  View   │◄────────│ Presenter │────────►│  Model  │
│ (UI)    │         │ (Logic)   │         │ (Data)  │
└─────────┘         └───────────┘         └─────────┘
     │                     │                     │
     └─────────────────────┴─────────────────────┘
              AppContext (Dependency Injection)
```

#### View
- Handles UI rendering
- Delegates user actions to Presenter
- Updates UI based on Presenter signals

#### Presenter
- Contains business logic
- Coordinates between View and Model
- Emits signals for View updates

#### Model
- Manages data
- Performs data operations
- Notifies Presenter of changes

### Dependency Injection

Use `AppContext` for dependency management:

```python
# Registering services
context = AppContext()
context.register("connector_model", ConnectorModel())

# Retrieving services
model = context.get("connector_model")
```

### Background Tasks

Use `BackgroundWorker` for long-running operations:

```python
from app.core.background_worker import BackgroundWorker

def long_running_task():
    # Process data
    return result

worker = BackgroundWorker(long_running_task)
worker.finished.connect(on_task_complete)
worker.start()
```

### Configuration

- Declarative configs preferred (e.g., `TAB_CONFIG`, `TAB_VISIBILITY_CONFIG`)
- Keep configs in separate files/sections
- Use type hints for config dictionaries

## Getting Help

- **Issues**: Check existing issues or create a new one
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: See `docs/` directory for detailed guides

## Recognition

Contributors will be recognized in:
- README.md Contributors section
- Release notes
- CHANGELOG.md

Thank you for contributing to Productivity App! 🎉
