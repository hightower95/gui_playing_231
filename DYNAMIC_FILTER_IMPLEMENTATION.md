# Dynamic Filter Implementation

## Overview
Implemented dynamic filtering where the available options in dependent filters (Shell Type, Material, Shell Size, Insert Arrangement, Socket Type, Keying) automatically update based on the selected Standard(s).

## Key Concept
When a user selects/deselects standards (e.g., D38999, VG), the other filters will only show options that are available for those selected standards. If a filter value is only linked to D38999 and the user deselects D38999, that option disappears from the filter.

## Architecture

### 1. **Model Layer** (`app/connector/connector_model.py`)

#### New Method: `get_available_filter_options()`
```python
def get_available_filter_options(self, selected_standards: List[str] = None) -> Dict[str, List[str]]
```

**Purpose**: Returns available options for each filter based on selected standards

**Logic**:
1. If `selected_standards` is empty/None → return all available options
2. If standards are selected → filter connectors to only those matching selected standards
3. Extract unique values for each property from the filtered connectors
4. Return sorted lists for each filter type

**Return Value**:
```python
{
    'shell_types': ['26 - Plug', '24 - Receptacle', ...],
    'materials': ['Aluminum', 'Stainless Steel', ...],
    'shell_sizes': ['8', '9', '10', ...],
    'insert_arrangements': ['A - 1', 'B - 2', ...],
    'socket_types': ['Type A', 'Type B', ...],
    'keyings': ['A', 'B', 'C', ...]
}
```

**Thread Safety**: Uses `QMutexLocker` for thread-safe access to connector data

**Example**:
- If user selects only "D38999":
  - Returns only shell types used in D38999 connectors
  - Returns only materials used in D38999 connectors
  - etc.
- If user selects "D38999" AND "VG":
  - Returns union of options from both standards

### 2. **View Layer** (`app/connector/Lookup/view.py`)

#### New Signal: `standards_changed`
```python
standards_changed = Signal(list)  # emits list of selected standard names
```

**Emitted When**: User changes selection in the Standard multiselect filter

#### New Method: `update_filter_options()`
```python
def update_filter_options(self, filter_options: dict)
```

**Purpose**: Updates all dependent filters with new available options

**Features**:
- Updates each dual-column multiselect with new items
- Preserves existing selections where possible
- Removes selections that are no longer valid
- Maintains dual-column layout with proper padding

#### New Method: `_update_multiselect_options()`
```python
def _update_multiselect_options(self, left_list, right_list, new_items: list)
```

**Purpose**: Updates a single dual-column multiselect with new items

**Algorithm**:
1. **Store current selections**: Collect all selected items from both lists
2. **Filter selections**: Keep only selections that exist in new items
3. **Block signals**: Temporarily disable signals to prevent cascading updates
4. **Clear lists**: Remove all current items
5. **Split new items**: Divide into left and right columns
6. **Add padding**: Add empty items if count is odd (for synchronized scrolling)
7. **Populate lists**: Add items and restore selections
8. **Disable padding items**: Set `Qt.NoItemFlags` on empty padding items
9. **Unblock signals**: Re-enable signals

**Key Points**:
- Uses `blockSignals(True/False)` to prevent infinite loops
- Maintains selection state across updates
- Handles odd-numbered lists with padding
- Preserves dual-column appearance and scrolling

#### Modified Method: `_connect_filter_signals()`
**Changes**:
- Standard filter now connects to `_on_standard_filter_changed()` instead of `_on_filter_changed()`
- All other filters connect to `_on_filter_changed()` as before

#### New Method: `_on_standard_filter_changed()`
```python
def _on_standard_filter_changed(self)
```

**Actions**:
1. Get currently selected standards
2. Emit `standards_changed` signal with selected standards
3. Emit `search_requested` signal to trigger search

### 3. **Presenter Layer** (`app/connector/Lookup/presenter.py`)

#### New Signal Connection
```python
self.view.standards_changed.connect(self.on_standards_changed)
```

#### New Method: `on_standards_changed()`
```python
def on_standards_changed(self, selected_standards: list)
```

**Purpose**: Handle changes to standard filter and update view

**Flow**:
1. Receive list of selected standards from view
2. Call `model.get_available_filter_options(selected_standards)`
3. Call `view.update_filter_options(filter_options)`
4. Log the changes for debugging

**Thread Safety**: Model method is thread-safe, view update happens on main thread

## Data Flow

```
User Changes Standard Filter
    ↓
View: _on_standard_filter_changed()
    ↓
Collect selected standards
    ↓
Emit: standards_changed(selected_standards)
    ↓
Presenter: on_standards_changed(selected_standards)
    ↓
Model: get_available_filter_options(selected_standards)
    ↓
Filter connectors by selected standards
    ↓
Extract unique values for each property
    ↓
Return filter_options dict
    ↓
Presenter → View: update_filter_options(filter_options)
    ↓
View: _update_multiselect_options() for each filter
    ↓
Store current selections
    ↓
Clear and repopulate with new options
    ↓
Restore valid selections
    ↓
View: Updated filters displayed
    ↓
Emit: search_requested(filters)
    ↓
Search executes with updated filters
```

## Example Scenarios

### Scenario 1: User selects D38999 only
1. User clicks "D38999" in Standard filter
2. View emits `standards_changed(['D38999'])`
3. Model returns options only from D38999 connectors:
   - Shell Types: Only types used in D38999
   - Materials: Only materials used in D38999
   - etc.
4. View updates all filter multiselects
5. Search executes with D38999 filter

### Scenario 2: User deselects last standard
1. User deselects D38999 (now nothing selected)
2. View emits `standards_changed([])`
3. Model returns ALL available options (no filtering)
4. View shows complete lists again
5. Search shows all connectors

### Scenario 3: User has existing filter selections
1. User has "Aluminum" selected in Material filter
2. User selects only "VG" in Standard filter
3. If VG has Aluminum connectors:
   - "Aluminum" remains selected
4. If VG doesn't have Aluminum:
   - "Aluminum" selection is removed (not in new options)
   - Material filter shows only VG materials

### Scenario 4: Multiple standards selected
1. User selects both "D38999" and "VG"
2. Model returns UNION of options from both standards
3. View shows all options available in either standard
4. Search returns connectors from both standards

## Signal Blocking Strategy

**Why Block Signals?**
When updating filter options, we temporarily block signals to prevent:
- Cascading filter updates
- Multiple search executions
- Infinite loops
- UI flicker

**Where Applied**:
```python
left_list.blockSignals(True)
right_list.blockSignals(True)
# ... update lists ...
left_list.blockSignals(False)
right_list.blockSignals(False)
```

**Result**: Only the final state triggers signals, not intermediate updates

## Performance Considerations

1. **Model Query**: `O(n)` where n = number of connectors (single pass filtering)
2. **Unique Extraction**: `O(n)` using sets for uniqueness
3. **View Update**: `O(m)` where m = number of items in filter (typically < 20)
4. **Signal Blocking**: Prevents unnecessary searches during updates
5. **Thread Safety**: Mutex locks are fast for small datasets

## Edge Cases Handled

1. **Empty Selection**: When no standards selected → show all options
2. **Invalid Selection**: Selections removed if option no longer available
3. **Odd Item Count**: Padding items added for synchronized scrolling
4. **Rapid Changes**: Signal blocking prevents update storms
5. **No Matching Data**: Returns empty lists gracefully

## Future Enhancements

1. **Cascading Filters**: Apply to other filters (e.g., Shell Type affects Insert Arrangement)
2. **Visual Indicators**: Show count of available connectors per option
3. **Disabled vs Hidden**: Gray out unavailable options instead of hiding
4. **Animation**: Smooth transitions when filters update
5. **Caching**: Cache filter options for common standard combinations
6. **Multi-level Dependencies**: Handle complex filter relationships

## Testing Recommendations

1. **Test standard selection combinations**:
   - Single standard
   - Multiple standards
   - All standards
   - No standards

2. **Test selection preservation**:
   - Valid selections maintained
   - Invalid selections removed
   - Mixed valid/invalid selections

3. **Test edge cases**:
   - Empty filter results
   - All items filtered out
   - Rapid standard changes
   - Concurrent filter changes

4. **Test UI responsiveness**:
   - No lag during updates
   - Scrolling remains synchronized
   - Selections visually correct

## Code Locations

- **Model**: `app/connector/connector_model.py` - `get_available_filter_options()`
- **View**: `app/connector/Lookup/view.py` - `update_filter_options()`, `_update_multiselect_options()`
- **Presenter**: `app/connector/Lookup/presenter.py` - `on_standards_changed()`
- **Signals**: `standards_changed` signal in view
