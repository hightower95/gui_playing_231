# Swiss Army Tool - Documentation

Welcome to the Swiss Army Tool documentation. This comprehensive engineering toolkit provides connector management, document scanning, EPD operations, and more.

## Table of Contents

### Getting Started
- [README](../README.md) - Main project overview and quick start
- [Installation Guide](#installation)
- [Configuration Guide](#configuration)

### Core Features

#### Document Scanner
- [Document Scanner Implementation](DOCUMENT_SCANNER_IMPLEMENTATION.md) - Technical implementation details
- [Document Scanner Complete Guide](DOCUMENT_SCANNER_COMPLETE.md) - Comprehensive user guide
- [Simplified Add Document](SIMPLIFIED_ADD_DOCUMENT.md) - How to add documents easily
- [Search History Feature](SIMPLE_SEARCH_HISTORY.md) - Using search history
- [Reload Documents Feature](RELOAD_DOCUMENTS_FEATURE.md) - Refreshing document data
- [Collapsible Results and Context](COLLAPSIBLE_RESULTS_AND_CONTEXT.md) - Understanding the results view
- [Debug Search Logging](DEBUG_SEARCH_LOGGING.md) - Troubleshooting searches

#### Connector Management
- [Connector Context Implementation](CONNECTOR_CONTEXT_IMPLEMENTATION.md) - Context enrichment system

#### Bug Fixes & Updates
- [History and Context Fixes](HISTORY_AND_CONTEXT_FIXES.md) - Recent bug fixes
- [Dialog Updates v2](DIALOG_UPDATES_v2.md) - UI improvements
- [Expandable Steps Dialog](EXPANDABLE_STEPS_DIALOG.md) - Enhanced dialogs

### Configuration & Migration
- [Configuration Migration Guide](CONFIG_MIGRATION.md) - Upgrading configurations
- [No Caching Design](NO_CACHING.md) - Architecture decision

## Installation

### From Source
```bash
cd swiss_army_tool
pip install -e .
```

### For Development
```bash
pip install -e ".[dev]"
```

## Configuration

Configuration files are stored in `.tool_config/`:
- `document_scanner.json` - Document scanner settings
- See [.tool_config/README.md](../.tool_config/README.md) for details

## Architecture

### Package Structure
```
app/
├── connector/          # Connector lookup and management
├── document_scanner/   # Document indexing and search
├── epd/               # EPD database integration
├── e3/                # E3 system integration
├── core/              # Base classes and configuration
├── ui/                # Reusable UI components
├── shared/            # Shared utilities
├── models/            # Data models
├── presenters/        # MVP presenters
├── views/             # MVP views
└── tabs/              # Main application tabs
```

### Design Patterns
- **MVP (Model-View-Presenter)** - Separation of concerns
- **Context Provider Pattern** - Extensible context enrichment
- **Configuration Manager** - Centralized config handling
- **Background Threading** - Non-blocking operations

## API Reference

### Core Classes

#### ConfigManager
```python
from app.core.config_manager import ConfigManager, DocumentScannerConfig

# Initialize config directory
ConfigManager.initialize()

# Save/load configurations
DocumentScannerConfig.save_documents(documents)
documents = DocumentScannerConfig.load_documents()
```

#### Document Scanner Model
```python
from app.document_scanner.document_scanner_model import DocumentScannerModel

model = DocumentScannerModel()
model.load_from_config()
documents = model.get_searchable_documents()
```

#### Context Provider
```python
from app.document_scanner.context_provider import ContextProvider
from app.document_scanner.search_result import SearchResult, Context

class MyContextProvider(ContextProvider):
    def get_context_name(self) -> str:
        return "MyModule"
    
    def get_context(self, result: SearchResult) -> List[Context]:
        # Add context based on search results
        return contexts
```

## Contributing

### Development Setup
1. Clone the repository
2. Install development dependencies: `pip install -e ".[dev]"`
3. Run tests: `pytest`
4. Format code: `black app/`

### Code Style
- Follow PEP 8
- Use type hints where possible
- Document public APIs
- Write tests for new features

## Support

For issues, questions, or contributions:
- GitHub Issues: [Report a bug or request a feature](https://github.com/yourusername/swiss-army-tool/issues)
- Documentation: Browse docs in this directory

## Version History

### 0.1.0 (Current)
- Initial library release
- Document scanner with context enrichment
- Connector management
- EPD integration
- Search history
- Configuration management

## License

MIT License - See [LICENSE](../LICENSE) file for details
