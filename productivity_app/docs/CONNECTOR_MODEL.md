# Connector Model Architecture

## Overview

The Connector Model is a comprehensive system for managing connector database lookups with multi-threaded data loading, advanced search capabilities, and alternative/opposite connector matching. It follows the MVP (Model-View-Presenter) pattern with signal-based communication and thread-safe operations.

## 🏗️ Architecture Overview

### Component Hierarchy
```
ConnectorModuleView (Main Tab)
├── ConnectorPresenter (Main Coordinator)
│   └── ConnectorModel (Data Management + Threading)
│       └── ConnectorDataWorker (Background Loading)
├── LookupConnectorPresenter (Search/Filter/Lookup)
│   └── LookupConnectorView (Search UI)
└── CheckMultipleConnectorPresenter (Batch Processing)
    └── CheckMultipleConnectorView (Batch UI)
```

### Data Flow Chain
```
User Action → Presenter → Model → Worker Thread → Data Source → Signals → Model → Presenter → View
```

## 🔄 Initialization Chain

### 1. Tab Creation (main_window.py)
```python
# From TAB_CONFIG
ConnectorPresenter(context)
├── creates ConnectorModel(context)  
├── creates ConnectorModuleView(context, model)
│   ├── creates LookupConnectorPresenter(context, model)
│   └── creates CheckMultipleConnectorPresenter(context, model) 
└── connects all signals between presenters and model
```

### 2. Data Loading Sequence
```python
ConnectorPresenter.start_loading()
├── ConnectorModel.load_async()
├── ConnectorDataWorker created in background thread
├── ConnectorDataWorker.run() executes data loading
├── Worker emits progress signals during loading
├── Worker emits finished signal with loaded data
├── Model processes data and emits data_loaded signal
└── All sub-presenters receive updated data
```

## 🧵 Threading Architecture

### ConnectorDataWorker Class
```python
class ConnectorDataWorker(QObject):
    # Signals for communication with main thread
    progress = Signal(int, str)      # progress_percent, status_message
    finished = Signal(object)        # loaded_data_dict
    error = Signal(str)             # error_message
    
    def run(self):
        """Execute data loading in background thread"""
        # Step 1: Connect to data source (20% progress)
        # Step 2: Load connector data (50% progress) 
        # Step 3: Process/validate data (75% progress)
        # Step 4: Emit finished signal (100% progress)
```

### Thread Safety with QMutex
```python
# All data access methods use mutex locking
def get_all(self) -> Optional[Dict]:
    with QMutexLocker(self._data_mutex):
        return self.data.copy() if self.data else None
```

### Loading States Management
- `loading_started` - UI shows loading indicator
- `loading_progress` - Progress bar updates with percentage and message
- `loading_completed` - Loading indicator hidden, data available
- `loading_failed` - Error message displayed to user

## 📊 Data Structure Requirements

### Expected Data Format
```python
{
    'connectors': [
        {
            'Part Number': 'D38999/26WA35PN',
            'Part Code': 'D38999-26WA35PN', 
            'Minified Part Code': 'D3899926WA35PN',
            'Material': 'Aluminum',
            'Database Status': 'Active',
            'Family': 'D38999',
            'Shell Type': '26 - Plug',
            'Shell Size': '10',
            'Insert Arrangement': 'A - 1',
            'Socket Type': 'Type A',
            'Keying': 'A'
        }
        # ... additional connectors
    ],
    'families': ['D38999', 'VG', 'MS', 'EN', 'MIL'],
    'shell_types': ['26 - Plug', '24 - Receptacle', '20 - Receptacle B'],
    'insert_arrangements': ['A - 1', 'B - 2', 'C - 3', 'A - 10', 'B - 3'],
    'socket_types': ['Type A', 'Type B', 'Type C', 'Type D'],
    'keyings': ['A', 'B', 'C', 'D', 'E', 'F', 'N']
}
```

### Required Connector Fields
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| Part Number | string | Full part number with slashes | `D38999/26WA35PN` |
| Part Code | string | Standardized part code | `D38999-26WA35PN` |
| Minified Part Code | string | Compressed version | `D3899926WA35PN` |
| Material | string | Construction material | `Aluminum`, `Stainless Steel` |
| Database Status | string | Availability status | `Active`, `Obsolete` |
| Family | string | Connector family/standard | `D38999`, `VG`, `MS` |
| Shell Type | string | Physical shell configuration | `26 - Plug`, `24 - Receptacle` |
| Shell Size | string | Size designation | `10`, `12`, `14` |
| Insert Arrangement | string | Pin/socket layout | `A - 1`, `B - 2` |
| Socket Type | string | Socket configuration | `Type A`, `Type B` |
| Keying | string | Keying/polarization | `A`, `B`, `Normal` |

## 🎯 Core Model Methods

### Data Loading (Already Implemented)
```python
def load_async(self):
    """Load connector data asynchronously in background thread"""
    # Creates ConnectorDataWorker and QThread
    # Connects signals for progress/completion/error handling
    # Starts background loading process
```

### Data Access Methods (Thread-Safe)
```python
def get_all(self) -> Optional[Dict]:
    """Get complete dataset"""

def get_families(self) -> List[str]:
    """Get list of connector families (D38999, VG, MS, etc.)"""

def get_shell_types(self) -> List[str]:
    """Get available shell types"""

def get_insert_arrangements(self) -> List[str]:
    """Get available insert arrangements"""  

def get_socket_types(self) -> List[str]:
    """Get available socket types"""

def get_keyings(self) -> List[str]:
    """Get available keying options"""

def get_connectors(self) -> List[Dict]:
    """Get raw connector list as array of dictionaries"""
```

### Advanced Filtering (Already Implemented)
```python
def filter_connectors(self, filters: Dict) -> List[Dict]:
    """Filter connectors based on multiple criteria"""
    # Supports: family, shell_type, insert_arrangement, socket_type, keying
    # Supports text search across all fields
    # Returns filtered list of connector dictionaries

def get_available_filter_options(self, selected_standards: List[str]) -> Dict:
    """Get dynamic filter options based on selected standards"""
    # Returns available options for each filter category
    # Filters options based on currently selected standards
    # Enables dynamic UI updates when standards change
```

### Lookup Methods (Need Implementation)
```python
def find_alternative(self, part_code: str) -> List[Dict[str, Any]]:
    """Find alternative connectors for a given part code
    
    Args:
        part_code: The part code to find alternatives for
    
    Returns:
        List of alternative connector dictionaries with 'Reason' field
        
    Implementation Ideas:
        - Match same family with different materials
        - Match same shell size with different keying
        - Match same insert arrangement with different shell type
        - Include 'Reason' field explaining why it's an alternative
    """

def find_opposite(self, part_code: str) -> Optional[Dict[str, Any]]:
    """Find opposite (mating) connector for a given part code
    
    Args:
        part_code: The part code to find opposite for
    
    Returns:
        Opposite connector dictionary with 'Reason' field or None
        
    Implementation Ideas:
        - Convert Plug ↔ Receptacle
        - Maintain same insert arrangement and shell size
        - Match compatible keying
        - Include 'Reason' field explaining the mating relationship
    """
```

## 🔍 Search Architecture

### Multi-Level Search Support
1. **Text Search** - Search across all connector fields
2. **Multi-Select Filters** - Family, Shell Type, Material, etc.
3. **Dynamic Filter Updates** - Filter options change based on selected standards
4. **Comma-Separated Search** - Support for multiple search terms
5. **Async Search Worker** - Non-blocking UI during large searches

### Search Worker Threading
```python
class SearchWorker(QObject):
    """Background thread for search operations"""
    finished = Signal(object)  # filtered DataFrame
    error = Signal(str)       # error message
    
    def run(self):
        """Execute search filtering in background"""
        # Apply text filters (single term or comma-separated)
        # Apply multi-select filters for each category
        # Return filtered DataFrame for UI display
```

### Search History Tracking
- Automatic recording of all search operations
- Stores search parameters and result counts
- Tracks special actions (Find Alternative, Find Opposite)
- Provides search replay functionality

## 🚀 Integration Points

### Signal-Based Communication
```python
# Model Signals
class ConnectorModel(BaseModel):
    loading_progress = Signal(int, str)    # progress_percent, status_message
    loading_failed = Signal(str)           # error_message
    data_loaded = Signal(object)           # loaded_data
    data_filtered = Signal(object)         # filtered_data

# Worker Signals  
class ConnectorDataWorker(QObject):
    progress = Signal(int, str)            # progress_percent, status_message
    finished = Signal(object)              # loaded_data
    error = Signal(str)                    # error_message
```

### Multi-Tab Coordination
```python
class ConnectorModuleView(QWidget):
    """Main connector tab containing sub-tabs"""
    
    # Sub-tabs share the same ConnectorModel instance
    def __init__(self, context, connector_model):
        self.lookup_presenter = LookupConnectorPresenter(context, connector_model)
        self.check_multiple_presenter = CheckMultipleConnectorPresenter(context, connector_model)
        
    def _switch_to_lookup_with_search(self, part_numbers_str: str):
        """Cross-tab navigation with data passing"""
```

### Data Sharing Between Tabs
- **Lookup Tab** - Primary search and filtering interface
- **Check Multiple Tab** - Batch processing of part numbers
- **Shared Model** - Both tabs use the same ConnectorModel instance
- **Cross-Navigation** - Check Multiple can send results to Lookup tab

## 🔧 Implementation Requirements

### What Needs Real Implementation

#### 1. ConnectorDataWorker._load_connector_data()
```python
def _load_connector_data(self) -> Dict:
    """Replace hardcoded data with actual data source
    
    Implementation Options:
    - Database connection (SQLite, PostgreSQL, SQL Server)
    - REST API calls to connector service
    - File parsing (CSV, Excel, JSON)
    - Web scraping from connector websites
    
    Requirements:
    - Return data in the expected format structure
    - Handle connection errors and timeouts
    - Support authentication if needed
    - Implement data caching for offline use
    """
```

#### 2. Alternative Connector Logic
```python
def find_alternative(self, part_code: str) -> List[Dict[str, Any]]:
    """Implement real alternative matching logic
    
    Algorithm Ideas:
    1. Parse part code to extract key characteristics
    2. Find connectors with similar characteristics:
       - Same shell size, different material
       - Same insert arrangement, different keying
       - Same family, different shell type (if compatible)
    3. Rank alternatives by similarity score
    4. Include reason for each alternative match
    5. Limit to top N most relevant alternatives
    """
```

#### 3. Opposite Connector Logic  
```python
def find_opposite(self, part_code: str) -> Optional[Dict[str, Any]]:
    """Implement mating connector logic
    
    Algorithm Ideas:
    1. Determine if connector is plug or receptacle
    2. Find matching connector with opposite shell type:
       - 26 (Plug) ↔ 24 (Receptacle)  
       - Keep same insert arrangement
       - Keep same shell size
       - Match compatible keying
    3. Validate electrical compatibility
    4. Return best mating match with reason
    """
```

### Configuration Requirements
- **Connection Settings** - Database URL, API endpoints, file paths
- **Authentication** - API keys, database credentials, certificates
- **Caching Strategy** - Local cache for offline operation, cache expiration
- **Performance Tuning** - Connection pooling, query optimization, data limits
- **Error Handling** - Retry logic, fallback data sources, user notifications

## 💡 Usage Examples

### Basic Search Flow
```python
# User searches for "D38999"
1. LookupPresenter.on_search({'search_text': 'D38999'})
2. SearchWorker created in background thread
3. SearchWorker.run() filters DataFrame asynchronously  
4. SearchWorker.finished.emit(filtered_df)
5. LookupPresenter._on_search_finished(filtered_df)
6. PandasTableModel.update(filtered_df)
7. View updates with results + statistics
```

### Alternative Lookup Flow
```python
# User selects connector and clicks "Find Alternative"
1. LookupPresenter.on_find_alternative('D38999-26WA35PN')
2. ConnectorModel.find_alternative('D38999-26WA35PN') # ← Needs Implementation
3. Combine original + alternatives into DataFrame
4. Update table with combined results
5. Add to search history as special action
6. Update UI statistics and context display
```

### Data Loading Flow
```python
# Application startup or user clicks refresh
1. ConnectorPresenter.start_loading()
2. ConnectorModel.load_async()
3. ConnectorDataWorker created and moved to background thread
4. Worker.run() connects to data source and loads data # ← Needs Implementation
5. Progress signals update UI loading indicator
6. Worker.finished.emit(data) signals completion
7. Model processes and stores data with thread safety
8. Model.data_loaded.emit(data) notifies all presenters
9. All sub-tabs update their views with new data
```

## 🔒 Thread Safety Considerations

### Mutex Protection
- All data access methods use `QMutexLocker(self._data_mutex)`
- Prevents race conditions during concurrent access
- Ensures data integrity during background loading

### Signal-Slot Communication
- All cross-thread communication uses Qt's signal-slot mechanism
- Automatically handles thread-safe message passing
- Prevents direct manipulation of UI from worker threads

### Worker Thread Management
- Only one ConnectorDataWorker active at a time
- Previous workers are cancelled before starting new ones
- Proper cleanup of threads on completion or error

## 📋 Testing Strategy

### Unit Tests Needed
- Data loading with various data source formats
- Filter logic with edge cases and empty results
- Alternative/opposite matching algorithms
- Thread safety under concurrent access
- Error handling for connection failures

### Integration Tests
- Full search workflow from UI to results
- Cross-tab data sharing and navigation
- Loading progress and error scenarios
- Performance with large datasets

### Mock Data Sources
- Test with various connector databases
- Simulate connection failures and timeouts
- Test with malformed or incomplete data
- Verify graceful degradation scenarios

## 🚧 Future Enhancements

### Performance Optimizations
- **Data Pagination** - Load large datasets in chunks
- **Intelligent Caching** - Cache frequently accessed data
- **Index Optimization** - Pre-build search indexes for faster filtering
- **Lazy Loading** - Load detailed data on demand

### Advanced Features
- **Fuzzy Matching** - Handle typos and variations in part numbers
- **Machine Learning** - Learn from user selections to improve suggestions
- **Real-time Updates** - Live synchronization with remote databases
- **Offline Support** - Full functionality when network is unavailable

### Integration Capabilities
- **CAD Integration** - Import/export connector data to CAD systems
- **BOM Processing** - Batch validate bill of materials
- **Standards Compliance** - Validate against industry standards
- **Cost Analysis** - Include pricing and availability data

This architecture provides a robust, scalable foundation for connector database management with room for significant future enhancement while maintaining clean separation of concerns and thread-safe operation.