# Context Menu "To Lookup" and E3 Data Loading

## New Features Added

### 1. Context Menu "To Lookup"

**Feature**: Right-click on selected rows in results table and choose "To Lookup" to switch to the Lookup tab with those Part Numbers.

#### Implementation Details

**View (`view.py`)**:
- Added custom action to context menu: `🔍 To Lookup`
- Method: `_context_menu_to_lookup()`
  - Extracts Part Numbers from selected rows
  - Finds "Part Number" column in table
  - Collects Part Numbers from all selected rows
  - Emits `to_lookup_requested` signal with list of Part Numbers

**Presenter (`presenter.py`)**:
- Enhanced `on_to_lookup_requested()` method
  - Smart detection: Checks if inputs are already Part Numbers or search terms
  - If Part Numbers (contain `/`, `-`, or known prefixes): Use as-is
  - If search terms: Perform lookup to get actual Part Numbers
  - Emits `switch_to_lookup` signal to trigger tab switch

#### Usage Flow

1. **Run batch operation** (Lookup, Get Material, etc.)
2. **Results appear** with Part Numbers
3. **Select one or more rows** (Ctrl+Click or Shift+Click)
4. **Right-click** → Choose "🔍 To Lookup"
5. **Automatically switches** to Lookup tab
6. **Part Numbers populated** in search field
7. **Search triggered** automatically

#### Comparison: Button vs Context Menu

| Method | Source | Input Type |
|--------|--------|------------|
| **To Lookup Button** | Imported data search column | Search terms → lookup → Part Numbers |
| **Context Menu** | Selected result rows | Part Numbers (direct) |

Both end up emitting the same signal and switching to Lookup tab with Part Numbers.

---

### 2. E3 Data Loading in File Import Dialog

**Feature**: Load connector data directly from E3.series projects or cached E3 exports.

#### UI Components

**Section**: "⚡ Load E3 Data" (added to FileUploadDialog)

**Option 1: Connect to Existing Project**
- Radio button to select this option
- **Project dropdown** with sample projects:
  - Project_Alpha_Rev3
  - Project_Beta_Final
  - Connector_Library_Master
  - System_Integration_2024
  - Prototype_Assembly_v2
- **Warning**: "⚠️ This operation can take several minutes"
- Currently shows as **not yet implemented** (placeholder for future)

**Option 2: Load from Cache**
- Radio button to select this option
- **Cache file path** input field
- **Suggested default**: `e3_connector_cache_2024-10-16.csv`
- **Browse button** to select different cache file
- Loads cache file like a normal CSV import

#### Implementation Details

**UI State Management**:
```python
def _on_e3_option_changed():
    if Connect to Project:
        - Enable: project dropdown
        - Show: warning message
        - Disable: cache file input
    elif Load from Cache:
        - Disable: project dropdown
        - Hide: warning message
        - Enable: cache file input
```

**Load E3 Data Button**:
- Disabled until an option is selected
- Clicking triggers `_load_e3_data()`
- For cache: Calls `_load_file(cache_file)` (same as browse/drop)
- For project: Shows "not yet implemented" message (future feature)

#### Usage Flow

**Loading from Cache**:
1. Open "Import File" dialog
2. Select "Load from Cache" radio button
3. Default cache file appears: `e3_connector_cache_2024-10-16.csv`
4. (Optional) Click "Browse..." to select different cache file
5. Click "📥 Load E3 Data"
6. File loads as normal CSV
7. Select search column and context columns
8. Click "Import"

**Loading from Project** (future):
1. Open "Import File" dialog
2. Select "Connect to Existing Project" radio button
3. Warning appears: "⚠️ This operation can take several minutes"
4. Select project from dropdown
5. Click "📥 Load E3 Data"
6. (Future) Connection established, data extracted
7. Select search column and context columns
8. Click "Import"

---

## Technical Details

### Signal Flow: Context Menu To Lookup

```
User right-clicks row(s)
    ↓
Context menu appears with "🔍 To Lookup"
    ↓
User clicks "To Lookup"
    ↓
_context_menu_to_lookup() extracts Part Numbers
    ↓
Emits: to_lookup_requested([part_numbers])
    ↓
Presenter: on_to_lookup_requested([part_numbers])
    ↓
Detects: These are Part Numbers (not search terms)
    ↓
Emits: switch_to_lookup(part_numbers_str)
    ↓
connector_tab.py: _switch_to_lookup_with_search()
    ↓
Switches to Lookup tab
    ↓
Populates search field with comma-separated Part Numbers
    ↓
Triggers search
```

### File Structure

**Modified Files**:
- `app/connector/CheckMultiple/view.py`
  - Added QRadioButton import
  - Added `_context_menu_to_lookup()` method
  - Added E3 loading UI in FileUploadDialog
  - Added `_on_e3_option_changed()` handler
  - Added `_browse_cache_file()` handler
  - Added `_load_e3_data()` handler

- `app/connector/CheckMultiple/presenter.py`
  - Enhanced `on_to_lookup_requested()` with smart Part Number detection

---

## Future Enhancements

### E3 Project Connection (To Be Implemented)

When "Connect to Existing Project" is fully implemented:

1. **Establish E3.series COM connection**
2. **Query project for connector data**
3. **Extract connector properties**:
   - Part Numbers
   - Part Codes
   - Materials
   - Database Status
   - Family/Type information
4. **Create DataFrame** from extracted data
5. **Display preview** and column selection
6. **Handle connection errors** gracefully

### Cache File Management

Potential future features:
- **Auto-generate cache** from E3 project
- **Cache expiration** warnings
- **Multiple cache files** (recent list)
- **Cache metadata** (date created, source project, row count)
- **Refresh cache** button

---

## Testing

### Test Context Menu To Lookup

1. Import `test_connectors.csv`
2. Select "Part Numbers" as search column
3. Run "Lookup" operation
4. Results appear with multiple connectors
5. Select 2-3 rows (Ctrl+Click)
6. Right-click → "🔍 To Lookup"
7. Verify: Switches to Lookup tab
8. Verify: Part Numbers appear in search field
9. Verify: Search executes automatically

### Test E3 Cache Loading

1. Create test cache file: `e3_test_cache.csv`
   ```csv
   Part Number,Material,Database Status,Notes
   D38999/26WA35PN,Aluminum,Active,Test connector 1
   MS3470L16-10P,Aluminum,Active,Test connector 2
   ```
2. Click "📁 Add Parts"
3. Select "Load from Cache"
4. Browse to `e3_test_cache.csv`
5. Click "📥 Load E3 Data"
6. Verify: File loads successfully
7. Verify: Preview shows 2 rows
8. Select "Part Number" as search column
9. Click "Import"
10. Verify: Data appears in results

---

## Benefits

✅ **Faster Navigation**: Right-click to lookup without re-typing Part Numbers  
✅ **Multi-Select Support**: Send multiple Part Numbers to Lookup at once  
✅ **E3 Integration**: Direct loading from E3.series (when implemented)  
✅ **Cache Support**: Fast loading from pre-exported E3 data  
✅ **User-Friendly**: Clear warnings and suggested cache files  
✅ **Flexible**: Both project connection and cache loading options  

## Configuration

No additional configuration needed. E3 project list is hardcoded in the dropdown but can be made dynamic in future versions.
