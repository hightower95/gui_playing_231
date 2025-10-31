# Productivity App

A comprehensive desktop productivity application for engineering workflows.

## Features

- **Connector Management** - Search and manage connector specifications
- **Document Scanner** - Index and search multiple documents (CSV, Excel, TXT)
- **EPD Operations** - Electronic Parts Database integration
- **Azure DevOps** - Work item queries and project management
- **Remote Documentation** - Access and search documentation

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/productivity-app.git
cd productivity-app

# Create virtual environment (Windows)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install the package
pip install -e .
```

## Usage

### Programmatic Usage

```python
from productivity_app import start, __version__

print(f"Productivity App v{__version__}")
start()  # Launch the GUI application
```

## Requirements

- Python 3.8 or higher
- PySide6 (Qt for Python)
- pandas
- openpyxl

## Project Structure

```
productivity_app/
├── app/              # Main application modules
│   ├── connector/    # Connector management
│   ├── document_scanner/  # Document indexing
│   ├── epd/          # EPD operations
│   ├── devops/       # Azure DevOps integration
│   └── tabs/         # UI components
├── docs/             # Detailed documentation
├── main.py           # Application entry point
└── pyproject.toml    # Package configuration
```

## Development

See [BUILD.md](BUILD.md) for detailed build and development instructions.

```bash
# Install with dev dependencies
pip install -e .[dev]

# Run tests
pytest

```
