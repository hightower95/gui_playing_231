# Swiss Army Tool

A comprehensive engineering toolkit for connector management, EPD operations, and document scanning with intelligent context enrichment.

## Features

### 🔌 Connector Management
- Lookup and search connector specifications
- Check multiple connectors simultaneously
- Find alternative and mating connectors
- Database-backed connector information

### 📄 Document Scanner
- Index and search multiple documents (CSV, Excel)
- Intelligent context enrichment from other modules
- Collapsible, organized results view
- Search history with quick re-run
- Background document loading for performance
- Configurable search columns and return columns

### 🔍 Context Provider System
- Extensible architecture for adding context from any module
- Connector context automatically enriches search results
- Easy to add new context providers (EPD, E3, etc.)

### 📊 EPD Operations
- Electronic Parts Database integration
- Search and identify best EPD matches
- Part information lookup

### 🛠️ Fault Finding
- Troubleshooting assistance tools
- Contextual help system

## Installation

### From Source
```bash
# Clone the repository
git clone https://github.com/yourusername/swiss-army-tool.git
cd swiss-army-tool

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### From PyPI (when published)
```bash
pip install swiss-army-tool
```

## Quick Start

### Running the Application
```bash
# If installed via pip
swiss-army-tool

# Or run directly
python main.py
```

### Using as a Library
```python
from app.core.app_context import AppContext
from app.connector.connector_model import ConnectorModel
from app.document_scanner.document_scanner_model import DocumentScannerModel

# Initialize context
context = AppContext()

# Use connector model
connector_model = ConnectorModel(context)
connector_model.load_async()

# Use document scanner
doc_scanner = DocumentScannerModel()
doc_scanner.load_from_config()
```

## Configuration

The tool stores configuration in `.tool_config/` directory:
- `document_scanner.json` - Document configurations and search history
- Other module configurations as needed

### Document Scanner Configuration
```json
{
  "documents": [
    {
      "file_path": "/path/to/document.csv",
      "file_name": "document.csv",
      "doc_type": "csv",
      "has_header": true,
      "header_row": 0,
      "search_columns": ["Column1", "Column2"],
      "return_columns": ["Column1", "Column2", "Column3"]
    }
  ],
  "search_history": [
    "search_term_1",
    "search_term_2"
  ]
}
```

## Documentation

### Feature Documentation
- [Document Scanner Implementation](DOCUMENT_SCANNER_IMPLEMENTATION.md)
- [Document Scanner Complete Guide](DOCUMENT_SCANNER_COMPLETE.md)
- [Connector Context Implementation](CONNECTOR_CONTEXT_IMPLEMENTATION.md)
- [Search History Feature](SIMPLE_SEARCH_HISTORY.md)
- [Reload Documents Feature](RELOAD_DOCUMENTS_FEATURE.md)
- [Collapsible Results and Context](COLLAPSIBLE_RESULTS_AND_CONTEXT.md)
- [History and Context Fixes](HISTORY_AND_CONTEXT_FIXES.md)

### Configuration & Migration
- [Configuration Migration Guide](CONFIG_MIGRATION.md)
- [Simplified Add Document](SIMPLIFIED_ADD_DOCUMENT.md)
- [Dialog Updates](DIALOG_UPDATES_v2.md)
- [Expandable Steps Dialog](EXPANDABLE_STEPS_DIALOG.md)

### Technical Documentation
- [Debug Search Logging](DEBUG_SEARCH_LOGGING.md)
- [No Caching Design](NO_CACHING.md)

## Architecture

### Core Components
- **app.core** - Base classes, configuration management, application context
- **app.connector** - Connector lookup and management
- **app.document_scanner** - Document indexing and search
- **app.epd** - Electronic Parts Database integration
- **app.e3** - E3 system integration
- **app.ui** - Reusable UI components
- **app.shared** - Shared utilities and helpers

### Key Design Patterns
- **Model-View-Presenter (MVP)** - Clean separation of concerns
- **Context Provider Pattern** - Extensible context enrichment
- **Background Threading** - Non-blocking document loading
- **Configuration Manager** - Centralized config handling
- **Signal/Slot Pattern** - Qt-based event communication

## Development

### Setting Up Development Environment
```bash
# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black app/

# Type checking
mypy app/
```

### Project Structure
```
swiss_army_tool/
├── app/
│   ├── connector/          # Connector management
│   ├── document_scanner/   # Document scanning & search
│   ├── epd/               # EPD operations
│   ├── e3/                # E3 integration
│   ├── core/              # Base classes & config
│   ├── ui/                # Reusable UI components
│   ├── shared/            # Shared utilities
│   ├── models/            # Data models
│   ├── presenters/        # Presenters (MVP pattern)
│   ├── views/             # Views (MVP pattern)
│   └── tabs/              # Main tab implementations
├── .tool_config/          # Configuration directory
├── docs/                  # Documentation (*.md files)
├── tests/                 # Unit tests
├── main.py               # Application entry point
├── setup.py              # Package setup
├── pyproject.toml        # Modern Python packaging
└── README.md             # This file
```

## Requirements
- Python >= 3.8
- PySide6 >= 6.0.0
- pandas >= 1.3.0
- openpyxl >= 3.0.0

## License
MIT License - See LICENSE file for details

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## Authors
- Your Name - Initial work

## Acknowledgments
- Built with PySide6 (Qt for Python)
- Uses pandas for data manipulation
- Inspired by the need for integrated engineering tools
