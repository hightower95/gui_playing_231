# Collapsible Results & Context Provider System

## Summary of Changes

### 1. Collapsible Results View ✅

**Updated**: `app/document_scanner/Search/view.py`

- Replaced `QTableView` with `QTreeView`
- Results are now grouped by document name
- Each document is a collapsible section showing result count
- Individual results are shown as child items

**Display Format**:
```
📁 Document Name (2 Results)
  ├─ #1: Col1: Value, Col2: Value
  └─ #2: Col1: Value, Col2: Value
  
📁 Other Document (3 Results)
  ├─ #1: Col1: Value, Col2: Value
  ├─ #2: Col1: Value, Col2: Value [+1 context(s)]
  └─ #3: Col1: Value, Col2: Value
```

### 2. Context System ✅

**New Classes**:

#### `Context` Data Class
Located in: `app/document_scanner/search_result.py`

```python
@dataclass
class Context:
    term: str              # The relevant term
    context_owner: str     # Who provided it ("Connector", "EPD", etc.)
    data_context: Dict[str, str]  # Additional key-value data
```

#### `ContextProvider` Base Class  
Located in: `app/document_scanner/context_provider.py`

```python
class ContextProvider(ABC):
    @abstractmethod
    def get_context_name(self) -> str:
        """Name of provider (e.g., 'Connector')"""
        
    @abstractmethod
    def get_context(self, result: SearchResult) -> List[Context]:
        """Get context for a search result"""
        
    def is_enabled(self) -> bool:
        """Check if provider is active"""
```

### 3. Updated SearchResult ✅

**Location**: `app/document_scanner/search_result.py`

Added:
- `contexts: List[Context]` - List of additional context
- `add_context(context)` - Add a context object
- `has_contexts()` - Check if result has any context

### 4. Search Presenter Updates ✅

**Location**: `app/document_scanner/Search/presenter.py`

New features:
- `register_context_provider(provider)` - Register a context provider
- `_enrich_results_with_context(results)` - Enrich results with context
- Automatically calls context providers after search
- Displays context count in results

### 5. Example Implementation ✅

**Location**: `app/connector/connector_context_provider.py`

Shows how Connector tab can provide context:
```python
class ConnectorContextProvider(ContextProvider):
    def get_context(self, result: SearchResult) -> List[Context]:
        # Look for part numbers in result data
        # Look up in connector database
        # Return Context objects with connector details
```

## How to Use Context Providers

### In the Connector Tab (or any other tab):

```python
from app.connector.connector_context_provider import ConnectorContextProvider

class ConnectorPresenter:
    def __init__(self, context):
        # ... initialization ...
        
        # Create context provider
        self.context_provider = ConnectorContextProvider(self.model)
        
        # Register with Document Scanner if it exists
        if hasattr(context, 'document_scanner'):
            doc_scanner = context.document_scanner
            doc_scanner.search_presenter.register_context_provider(
                self.context_provider
            )
```

### In Main Window (connect tabs):

```python
class MainWindow(QMainWindow):
    def __init__(self, context):
        # Create tabs
        self.document_scanner = DocumentScannerModuleView(context)
        self.connectors = ConnectorsPresenter(context)
        self.epd = EpdPresenter(context)
        
        # Register context providers
        self.document_scanner.search_presenter.register_context_provider(
            self.connectors.context_provider
        )
        self.document_scanner.search_presenter.register_context_provider(
            self.epd.context_provider
        )
```

## Example Context Provider Implementation

### Connector Context Provider

```python
def get_context(self, result: SearchResult) -> List[Context]:
    contexts = []
    
    # Look for part numbers in result
    for column, value in result.matched_row_data.items():
        if 'part' in column.lower():
            # Look up in connector database
            conn_info = self.lookup_connector(value)
            
            if conn_info:
                context = Context(
                    term=value,
                    context_owner="Connector",
                    data_context={
                        'Type': conn_info['type'],
                        'Pin Count': conn_info['pins'],
                        'In Stock': 'Yes' if conn_info['qty'] > 0 else 'No'
                    }
                )
                contexts.append(context)
    
    return contexts
```

### EPD Context Provider

```python
class EpdContextProvider(ContextProvider):
    def get_context(self, result: SearchResult) -> List[Context]:
        contexts = []
        
        # Look for part numbers
        for column, value in result.matched_row_data.items():
            if 'part' in column.lower():
                # Look up EPD data
                epd_data = self.lookup_epd(value)
                
                if epd_data:
                    context = Context(
                        term=value,
                        context_owner="EPD",
                        data_context={
                            'Description': epd_data['description'],
                            'Category': epd_data['category'],
                            'Lifecycle': epd_data['lifecycle']
                        }
                    )
                    contexts.append(context)
        
        return contexts
```

## Context Display

When a result with context is selected, the detail view shows:

```
Search Result Details:

Search Term: D9P
Document: connectors.csv
Document Type: default

Matched Data:
  Part Number: D9P-123
  Description: 9-Pin D-Sub Connector
  Manufacturer: TE Connectivity

========================================
Additional Context:
========================================

[Connector]
  Term: D9P-123
  Connector Type: D-Sub
  Pin Count: 9
  Gender: Male
  In Stock: Yes
  Location: Bin A23

[EPD]
  Term: D9P-123
  Description: D-Subminiature Connector, 9 Position
  Category: Connectors
  Lifecycle: Active
```

## Benefits

1. **Collapsible View**: Clean, organized results grouped by document
2. **Context Enrichment**: Results automatically enhanced with data from other modules
3. **Extensible**: Any tab can become a context provider
4. **Non-intrusive**: Context providers are optional and don't affect search if not registered
5. **Rich Details**: Users get comprehensive information without manual lookups

## Next Steps

To enable context providers:

1. Implement `ContextProvider` in Connector tab
2. Implement `ContextProvider` in EPD tab
3. Register providers with Document Scanner in main window
4. Add lookup logic to each provider
5. Test with sample searches

## Testing

1. Add a document with part numbers
2. Search for a part number
3. Click a result
4. Should see grouped results by document
5. Should see additional context in detail view (once providers are implemented)
