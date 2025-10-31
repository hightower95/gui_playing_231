# Swiss Army Tool - Installation & Usage Guide

## Table of Contents
1. [Installation](#installation)
2. [Running the Application](#running-the-application)
3. [Using as a Library](#using-as-a-library)
4. [Development Setup](#development-setup)
5. [Building and Distribution](#building-and-distribution)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Option 1: Install from Source (Editable Mode)
This is recommended for development or if you want to modify the code.

```bash
# Navigate to the swiss_army_tool directory
cd path/to/swiss_army_tool

# Install in editable mode
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

### Option 2: Install from Source (Standard)
```bash
cd path/to/swiss_army_tool
pip install .
```

### Option 3: Install from PyPI (When Published)
```bash
pip install swiss-army-tool
```

### Verify Installation
```bash
# Check if command is available
swiss-army-tool --help

# Or import in Python
python -c "import app; print(app.__version__)"
```

## Running the Application

### As a Standalone Application

#### Method 1: Using the Installed Command
If you installed the package:
```bash
swiss-army-tool
```

#### Method 2: Running main.py Directly
```bash
cd swiss_army_tool
python main.py
```

#### Method 3: Running as a Module
```bash
python -m app.main
```

### Configuration
On first run, the application will create a `.tool_config` directory in the swiss_army_tool folder to store:
- Document scanner configurations
- Search history
- Module-specific settings

## Using as a Library

### Basic Usage

#### Example 1: Using ConfigManager
```python
from app.core.config_manager import ConfigManager, DocumentScannerConfig

# Initialize configuration system
ConfigManager.initialize()

# Load document configurations
documents = DocumentScannerConfig.load_documents()
print(f"Loaded {len(documents)} documents")

# Load search history
history = DocumentScannerConfig.load_search_history()
print(f"Search history: {history}")
```

#### Example 2: Using Document Scanner Model
```python
from app.document_scanner.document_scanner_model import DocumentScannerModel
from app.document_scanner.searchable_document import SearchableDocument

# Create model
model = DocumentScannerModel()

# Load documents from configuration
model.load_from_config()

# Wait for loading to complete (in production, use signals)
# model.loading_finished signal will emit when done

# Get searchable documents
documents = model.get_searchable_documents()

# Perform search
for doc in documents:
    results = doc.search("search_term")
    for result in results:
        print(f"Found in {result.document_name}: {result.matched_row_data}")
```

#### Example 3: Creating a Custom Context Provider
```python
from typing import List
from app.document_scanner.context_provider import ContextProvider
from app.document_scanner.search_result import SearchResult, Context

class CustomContextProvider(ContextProvider):
    """Custom context provider example"""
    
    def __init__(self, data_source=None):
        self.data_source = data_source
        self.enabled = True
    
    def get_context_name(self) -> str:
        return "CustomModule"
    
    def get_context(self, result: SearchResult) -> List[Context]:
        """Add custom context to search results"""
        contexts = []
        
        # Check result data
        for column, value in result.matched_row_data.items():
            # Look up value in your data source
            if self.data_source and value in self.data_source:
                context = Context(
                    term=str(value),
                    context_owner="CustomModule",
                    data_context=self.data_source[value]
                )
                contexts.append(context)
        
        return contexts
    
    def is_enabled(self) -> bool:
        return self.enabled

# Register with document scanner
from app.document_scanner.Search.presenter import SearchPresenter

search_presenter = SearchPresenter(context, model)
custom_provider = CustomContextProvider(my_data)
search_presenter.register_context_provider(custom_provider)
```

#### Example 4: Programmatic Document Management
```python
from app.core.config_manager import DocumentScannerConfig

# Add a new document configuration
new_doc = {
    "file_path": "/path/to/document.csv",
    "file_name": "document.csv",
    "doc_type": "csv",
    "has_header": True,
    "header_row": 0,
    "search_columns": ["Column1", "Column2"],
    "return_columns": ["Column1", "Column2", "Result"],
    "precondition": None  # Optional search filter
}

# Load existing documents
documents = DocumentScannerConfig.load_documents()

# Add new document
documents.append(new_doc)

# Save back
DocumentScannerConfig.save_documents(documents)
```

### Advanced Usage with Qt Integration

```python
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject
from app.core.app_context import AppContext
from app.document_scanner.document_scanner_model import DocumentScannerModel

class MyApp(QObject):
    def __init__(self):
        super().__init__()
        
        # Create model
        self.model = DocumentScannerModel()
        
        # Connect signals
        self.model.loading_finished.connect(self.on_documents_loaded)
        self.model.loading_progress.connect(self.on_progress)
        self.model.documents_changed.connect(self.on_documents_changed)
        
        # Start loading
        self.model.load_from_config()
    
    def on_documents_loaded(self, documents):
        print(f"Loaded {len(documents)} documents")
        self.perform_search()
    
    def on_progress(self, current, total, message):
        print(f"Progress: {current}/{total} - {message}")
    
    def on_documents_changed(self, documents):
        print("Documents changed")
    
    def perform_search(self):
        documents = self.model.get_searchable_documents()
        for doc in documents:
            results = doc.search("my_search_term")
            print(f"Found {len(results)} results in {doc.file_name}")

# Run with Qt event loop
app = QApplication([])
my_app = MyApp()
app.exec()
```

## Development Setup

### Setting Up Development Environment

1. **Clone or navigate to the repository**
```bash
cd swiss_army_tool
```

2. **Create a virtual environment (recommended)**
```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

3. **Install development dependencies**
```bash
pip install -e ".[dev]"
```

4. **Verify installation**
```bash
python -c "import app; print(app.__version__)"
```

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
# Format all Python files
black app/

# Check specific files
black app/core/config_manager.py
```

### Type Checking
```bash
mypy app/
```

### Linting
```bash
flake8 app/
```

## Building and Distribution

### Building the Package

#### Build wheel and source distribution
```bash
pip install build
python -m build
```

This creates:
- `dist/swiss_army_tool-0.1.0-py3-none-any.whl` (wheel package)
- `dist/swiss_army_tool-0.1.0.tar.gz` (source distribution)

### Installing from Built Package
```bash
pip install dist/swiss_army_tool-0.1.0-py3-none-any.whl
```

### Publishing to PyPI (When Ready)

1. **Install twine**
```bash
pip install twine
```

2. **Upload to TestPyPI (testing)**
```bash
twine upload --repository testpypi dist/*
```

3. **Upload to PyPI (production)**
```bash
twine upload dist/*
```

## Project Structure

```
swiss_army_tool/
├── app/                    # Main application package
│   ├── __init__.py        # Package initialization
│   ├── connector/         # Connector management module
│   ├── document_scanner/  # Document scanning module
│   ├── epd/              # EPD integration
│   ├── e3/               # E3 integration
│   ├── core/             # Core functionality
│   │   ├── config_manager.py
│   │   ├── app_context.py
│   │   └── ...
│   ├── ui/               # UI components
│   ├── shared/           # Shared utilities
│   └── ...
├── docs/                  # Documentation
│   ├── INDEX.md
│   └── *.md              # Feature documentation
├── tests/                 # Unit tests (create this)
├── .tool_config/         # Runtime configuration
├── main.py               # Application entry point
├── setup.py              # Package setup (legacy)
├── pyproject.toml        # Modern package configuration
├── MANIFEST.in           # Package data inclusion
├── README.md             # Project overview
├── LICENSE               # License file
├── requirements.txt      # Dependencies
└── .gitignore           # Git ignore rules
```

## Troubleshooting

### Import Errors
If you get `ModuleNotFoundError: No module named 'app'`:
```bash
# Make sure you're in the swiss_army_tool directory
cd swiss_army_tool

# Install in editable mode
pip install -e .
```

### Configuration Not Found
If configuration files aren't found:
```python
from app.core.config_manager import ConfigManager
ConfigManager.initialize()  # Creates .tool_config directory
```

### Qt Platform Plugin Issues
If you get "Could not find the Qt platform plugin":
```bash
pip install --upgrade PySide6
```

### Missing Dependencies
```bash
pip install -r requirements.txt
```

## Next Steps

- Read the [Documentation Index](docs/INDEX.md)
- Check out [Document Scanner Guide](docs/DOCUMENT_SCANNER_COMPLETE.md)
- Learn about [Context Providers](docs/CONNECTOR_CONTEXT_IMPLEMENTATION.md)
- Explore [Configuration Options](docs/CONFIG_MIGRATION.md)
