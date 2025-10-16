# E3 Loading Enhancements and Context Menu Fix

## Changes Made

### 1. Fixed Context Menu Error

**Problem**: Context menu setup was failing with unpacking error when using dict format for actions.

**Solution**: Updated `table_context_menu_mixin.py` to support both formats:
- **Old format** (tuple): `(action_name, action_callback)` - callback receives `(index, row, column)`
- **New format** (dict): `{'text': name, 'callback': func}` - callback receives no parameters

```python
for action_config in self.context_actions:
    if isinstance(action_config, dict):
        # Dict format - callback doesn't receive table context
        action_name = action_config['text']
        action_callback = action_config['callback']
        action.triggered.connect(action_callback)
    else:
        # Tuple format - callback receives (index, row, column)
        action_name, action_callback = action_config
        action.triggered.connect(
            lambda _, cb=action_callback: cb(index, row, column))
```

---

### 2. Hide E3 Section When File Loaded

**Feature**: E3 loading section automatically hides when a file is loaded (via browse or drag-drop).

**Implementation**:
- Changed `e3_frame` to `self.e3_frame` (stored as instance variable)
- In `_load_file()` after successful file load: `self.e3_frame.setVisible(False)`

**Behavior**:
```
Initial Dialog:
┌─────────────────┐
│ Drop Zone       │
└─────────────────┘
┌─────────────────┐
│ E3 Loading      │ ← Visible
└─────────────────┘

After File Loaded:
┌─────────────────┐
│ ✓ Loaded: ...   │
└─────────────────┘
│ E3 Loading      │ ← Hidden
└─────────────────┘
│ Column Select   │
│ Preview         │
└─────────────────┘
```

---

### 3. E3 Project Multiselect

**Changed**: Project selection from single QComboBox to multi-selection widget.

**Implementation**:
- Replaced `QComboBox` with `DualColumnMultiselect`
- Users can now select multiple E3 projects at once
- Uses existing DualColumnMultiselect component

**UI Changes**:
```
Before:
Select Projects: [Single Dropdown ▼]

After:
Select Projects:
┌────────────────┬────────────────┐
│ Available      │ Selected       │
│ □ Project_A    │ ☑ Project_C    │
│ □ Project_B    │ ☑ Project_D    │
│ ☑ Project_C    │                │
│ ☑ Project_D    │                │
└────────────────┴────────────────┘
```

**Updated Logic**:
```python
# Get selected projects
selected_projects = self.e3_project_multiselect.get_selected_items()

# Show message with all selected projects
project_names = ", ".join(selected_projects)
```

---

### 4. E3 Data Signals

**Added 4 new signals** to `FileUploadDialog`:

```python
# Request signals (from dialog to presenter/model)
request_e3_projects_available = Signal()
request_e3_project_caches_available = Signal()

# Response signals (from presenter/model to dialog)
e3_projects_available = Signal(list)  # List of project names
e3_project_caches_available = Signal(list)  # List of cache file paths
```

**Signal Flow**:

#### Loading E3 Projects
```
User selects "Connect to Existing Project"
    ↓
Dialog emits: request_e3_projects_available
    ↓
Presenter/Model queries E3.series for projects
    ↓
Dialog receives: e3_projects_available([project1, project2, ...])
    ↓
Dialog populates multiselect with projects
```

#### Loading Cache Files
```
User selects "Load from Cache"
    ↓
Dialog emits: request_e3_project_caches_available
    ↓
Presenter/Model scans for cache files
    ↓
Dialog receives: e3_project_caches_available([cache1.csv, cache2.csv, ...])
    ↓
Dialog sets first cache as suggested file
```

**Handler Methods**:
```python
def _on_e3_option_changed(self):
    if self.e3_connect_radio.isChecked():
        self.e3_project_multiselect.setEnabled(True)
        self.request_e3_projects_available.emit()  # ← Request projects
    elif self.e3_cache_radio.isChecked():
        self.e3_cache_path.setEnabled(True)
        self.request_e3_project_caches_available.emit()  # ← Request caches

def populate_e3_projects(self, projects: list):
    """Called when e3_projects_available signal received"""
    # TODO: Update multiselect items dynamically

def populate_e3_caches(self, caches: list):
    """Called when e3_project_caches_available signal received"""
    if caches:
        self.e3_cache_path.setText(caches[0])  # Set first as default
```

---

## Integration Points

### Presenter Side (To Be Implemented)

```python
class CheckMultipleConnectorPresenter:
    def __init__(self, ...):
        # Connect to dialog signals
        self.view.file_upload_dialog.request_e3_projects_available.connect(
            self.on_request_e3_projects)
        self.view.file_upload_dialog.request_e3_project_caches_available.connect(
            self.on_request_e3_caches)
    
    def on_request_e3_projects(self):
        """Query E3.series for available projects"""
        # TODO: Implement E3 COM connection
        projects = self.e3_service.get_available_projects()
        self.view.file_upload_dialog.e3_projects_available.emit(projects)
    
    def on_request_e3_caches(self):
        """Scan for E3 cache files"""
        cache_dir = Path("./e3_caches")
        if cache_dir.exists():
            caches = [str(f) for f in cache_dir.glob("*.csv")]
            caches.sort(reverse=True)  # Most recent first
            self.view.file_upload_dialog.e3_project_caches_available.emit(caches)
```

---

## Testing

### Test Context Menu Fix
1. Import test file with results
2. Right-click on row → "🔍 To Lookup"
3. **Expected**: No error, switches to Lookup tab
4. **Previous**: UnpackingError

### Test E3 Section Hide
1. Open "Add Parts" dialog
2. Verify E3 section is visible
3. Browse or drag-drop a file
4. **Expected**: E3 section disappears
5. **Result**: More screen space for column selection

### Test Project Multiselect
1. Open "Add Parts" dialog
2. Select "Connect to Existing Project"
3. **Expected**: Multiselect widget appears
4. Select multiple projects (Ctrl+Click)
5. Click "Load E3 Data"
6. **Expected**: Message shows all selected project names

### Test Signals (When Implemented)
1. Connect presenter handlers
2. Select "Connect to Existing Project"
3. **Expected**: `request_e3_projects_available` emitted
4. Presenter responds with projects
5. **Expected**: Multiselect populated with real projects

---

## Benefits

✅ **Context Menu Fixed**: Right-click "To Lookup" now works without errors  
✅ **Cleaner UI**: E3 section hides after file load, reducing clutter  
✅ **Multi-Project Support**: Can load data from multiple E3 projects at once  
✅ **Signal Architecture**: Clean separation between UI and E3 integration logic  
✅ **Future-Ready**: Signals in place for dynamic project/cache discovery  
✅ **Backwards Compatible**: Context menu supports both old and new action formats  

---

## Future Enhancements

### Dynamic Project List
Currently, projects are hardcoded. To make dynamic:
1. Extend `DualColumnMultiselect` with `set_items(items: list)` method
2. Call `set_items()` in `populate_e3_projects()`
3. Update multiselect when projects change

### Cache File Browser
Instead of single text field:
- Dropdown/multiselect of recent cache files
- Metadata display (creation date, row count, source project)
- Quick preview of cache contents

### Progress Indicator
For E3 project connections:
- Progress bar showing connection status
- Cancel button for long operations
- Estimated time remaining

---

## Files Modified

1. **`app/ui/table_context_menu_mixin.py`**
   - Fixed context menu action unpacking to support dict format

2. **`app/connector/CheckMultiple/view.py`**
   - Added 4 new signals for E3 project/cache discovery
   - Changed `e3_frame` to `self.e3_frame` (instance variable)
   - Hide E3 frame in `_load_file()` after successful load
   - Replaced `QComboBox` with `DualColumnMultiselect` for projects
   - Updated `_on_e3_option_changed()` to emit request signals
   - Updated `_load_e3_data()` to handle multiple projects
   - Added `populate_e3_projects()` method
   - Added `populate_e3_caches()` method
