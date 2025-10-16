# Recent Searches Enhancements & Multi-Term Search

## Overview
Enhanced the recent searches feature with better formatting, full search restoration, scrolling support, and added comma-separated multi-term search capability.

## New Features

### 1. Enhanced Recent Search Display

#### Display Format
**Old Format:**
```
Text: 'D38999' | Standard: D38999 | Material: Aluminum
```

**New Format:**
```
Advanced Search (25 results)
Input: D38999 (12 results)
Input: D38999, VG95234 (8 results)
```

#### Format Logic
- **Advanced Search**: When any multiselect filters are used
- **Input: {text}**: When only search text is used (no filters)
- **Result count**: Shows number of results found

#### Implementation
```python
def _add_to_recent_searches(self, filters: dict, result_count: int):
    # Determine if advanced filters are used
    is_advanced = bool(any filter selections)
    
    if is_advanced:
        search_type = "Advanced Search"
    else:
        search_type = f"Input: {search_text}"
    
    # Format: "Advanced Search (25 results)"
    search_description = f"{search_type} ({result_count} result{'s' if result_count != 1 else ''})"
```

### 2. Increased Capacity with Scrolling

#### Specifications
- **Maximum searches**: 35 (increased from 10)
- **Visible items**: 15 (scrolls after 15)
- **Scroll behavior**: Automatic vertical scrollbar when > 15 items

#### Implementation
```python
# In __init__:
self.recent_searches = deque(maxlen=35)

# In _setup_footer:
self.recent_searches_combo.setMaxVisibleItems(15)  # Scroll after 15 items
```

### 3. Full Search Restoration

#### Feature
Clicking a recent search now fully restores:
- Search text input
- All multiselect filter selections
- Automatically executes the search

#### Implementation

**New Method: `_on_recent_search_selected()`**
```python
def _on_recent_search_selected(self, search_text: str):
    # Get stored filters
    filters = self.recent_searches_data[search_text]
    
    # Clear current state
    self._clear_all_selections()
    
    # Restore search text
    if filters.get('search_text'):
        self.search_input.setText(filters['search_text'])
    
    # Restore all multiselect filters
    self._restore_multiselect_selections(...)
    
    # Execute search
    self.search_requested.emit(filters)
```

**New Method: `_clear_all_selections()`**
```python
def _clear_all_selections(self):
    """Clear all filter selections and search text"""
    self.search_input.clear()
    # Clear all 14 list widgets (7 filters × 2 columns)
    self.standard_list_left.clearSelection()
    # ... etc
```

**New Method: `_restore_multiselect_selections()`**
```python
def _restore_multiselect_selections(self, left_list, right_list, selected_values: list):
    """Restore selections in a dual-column multiselect"""
    # Block signals to prevent cascading
    left_list.blockSignals(True)
    right_list.blockSignals(True)
    
    # Select matching items
    for i in range(left_list.count()):
        item = left_list.item(i)
        if item and item.text() in selected_values:
            item.setSelected(True)
    
    # Re-enable signals
    left_list.blockSignals(False)
    right_list.blockSignals(False)
```

### 4. Search Data Storage

#### Data Structure
```python
# In __init__:
self.recent_searches = deque(maxlen=35)  # Display strings
self.recent_searches_data = {}  # Maps display string to filters dict
```

#### Storage Pattern
```python
# Key: Display string
"Advanced Search (25 results)"

# Value: Full filters dict
{
    'search_text': 'D38999',
    'standard': ['D38999', 'VG'],
    'shell_type': ['26 - Plug'],
    'material': ['Aluminum'],
    'shell_size': [],
    'insert_arrangement': [],
    'socket_type': [],
    'keying': []
}
```

### 5. Result Count Tracking

#### Flow
```
User Performs Search
    ↓
Presenter: on_search(filters)
    ↓
Store filters: self.current_filters = filters.copy()
    ↓
SearchWorker executes (async)
    ↓
Presenter: _on_search_finished(filtered_df)
    ↓
result_count = len(filtered_df)
    ↓
View: add_search_to_history(filters, result_count)
    ↓
Search added to history with count
```

#### Implementation
```python
# Presenter
def on_search(self, filters: dict):
    self.current_filters = filters.copy()  # Store for later
    # ... execute search

def _on_search_finished(self, filtered_df):
    # ... update table
    result_count = len(filtered_df)
    self.view.add_search_to_history(self.current_filters, result_count)
```

### 6. Comma-Separated Multi-Term Search

#### Feature
Search input now supports multiple search terms separated by commas:
- `D38999, VG95234` → Finds records matching either term
- `Aluminum, Stainless` → Finds records with either material
- Terms are OR'd together (matches any term)

#### Placeholder Update
```
"part code, number, alias or property (comma-separated for multiple)"
```

#### Implementation in SearchWorker
```python
if self.filters.get('search_text'):
    search_text = self.filters['search_text'].strip()
    
    # Check if comma-separated (multiple search terms)
    if ',' in search_text:
        # Split by comma and trim each term
        search_terms = [term.strip().lower() for term in search_text.split(',') if term.strip()]
        
        # Create OR condition - match any term
        mask = pd.Series([False] * len(filtered_df), index=filtered_df.index)
        for term in search_terms:
            term_mask = filtered_df.apply(lambda row: row.astype(
                str).str.lower().str.contains(term, regex=False).any(), axis=1)
            mask = mask | term_mask
        
        filtered_df = filtered_df[mask]
    else:
        # Single search term
        search_text = search_text.lower()
        mask = filtered_df.apply(lambda row: row.astype(
            str).str.lower().str.contains(search_text, regex=False).any(), axis=1)
        filtered_df = filtered_df[mask]
```

#### Search Logic
1. **Detect commas**: Check if ',' present in search text
2. **Split terms**: Split by comma, trim whitespace
3. **OR logic**: Create boolean mask for each term
4. **Combine**: OR all masks together (`mask = mask | term_mask`)
5. **Filter**: Apply combined mask to DataFrame

#### Examples
```python
# Single term
"D38999" → Matches any record containing "D38999"

# Multiple terms (OR)
"D38999, VG95234" → Matches records containing "D38999" OR "VG95234"

# Multiple terms (OR)
"Aluminum, Stainless, Titanium" → Matches records with any of these materials
```

### 7. Data Limiting for Performance

#### Feature
Limit initial connector data load to 100 records to prevent sending large datasets to the GUI.

#### Implementation
```python
def _convert_to_dataframe(self, data: dict) -> pd.DataFrame:
    """Convert connector data to DataFrame, limiting to first 100 results"""
    connectors = data['connectors']
    
    # Limit to 100 connectors to avoid sending too much data to GUI
    limited_connectors = connectors[:100]
    
    # Log if we're limiting
    if len(connectors) > 100:
        print(f"Limited connector data from {len(connectors)} to 100 records for initial display")
    
    return pd.DataFrame(limited_connectors)
```

#### Rationale
- Large datasets (10,000+ connectors) slow down GUI
- Initial load only needs representative sample
- Search/filter operations work on this subset
- Can load more data on demand later

## Updated UI Elements

### Search Input
```
+-------------------------------------------------------------------------+
| [part code, number, alias or property (comma-separated for multiple) ] |
+-------------------------------------------------------------------------+
```

### Recent Searches Dropdown
```
+-------------------------------------------------------------------------+
| Recent Searches: [▼ Advanced Search (25 results)                    ]  |
|                   | Advanced Search (12 results)                      |
|                   | Input: D38999 (8 results)                         |
|                   | Input: D38999, VG95234 (15 results)               |
|                   | Advanced Search (3 results)                       |
|                   | ... (scrolls after 15 items)                      |
+-------------------------------------------------------------------------+
```

### Record Count Label
```
Showing 25 of 100 connectors from database
```

## Data Flow

### Add to History Flow
```
User Performs Search
    ↓
Presenter: on_search(filters)
    ↓
Store: current_filters = filters
    ↓
SearchWorker executes (background thread)
    ↓
SearchWorker: finished(filtered_df)
    ↓
Presenter: _on_search_finished(filtered_df)
    ↓
Get: result_count = len(filtered_df)
    ↓
View: add_search_to_history(filters, result_count)
    ↓
Create display string: "Advanced Search (25 results)"
    ↓
Store: recent_searches_data[display_string] = filters
    ↓
Add: recent_searches.appendleft(display_string)
    ↓
Update combo box
```

### Restore from History Flow
```
User Selects Recent Search
    ↓
View: _on_recent_search_selected(search_text)
    ↓
Get: filters = recent_searches_data[search_text]
    ↓
Clear all current selections
    ↓
Restore search input text
    ↓
Restore all multiselect filters (with signals blocked)
    ↓
Emit: search_requested(filters)
    ↓
Presenter executes search with restored filters
    ↓
Results displayed
```

### Multi-Term Search Flow
```
User Enters: "D38999, VG95234"
    ↓
Search triggered
    ↓
SearchWorker: run()
    ↓
Detect comma in search_text
    ↓
Split: ['D38999', 'VG95234']
    ↓
For each term:
    Create mask for rows containing term
    ↓
Combine masks with OR
    ↓
Apply combined mask to DataFrame
    ↓
Return filtered results
```

## Performance Optimizations

### 1. Data Limiting
- Initial load: 100 records max
- Prevents GUI slowdown with large datasets
- Reduces memory usage

### 2. Signal Blocking
- Block signals during filter restoration
- Prevents cascading filter change events
- Avoids multiple searches during restore

### 3. Deque for History
- O(1) insertion at front (`appendleft`)
- Automatic size limiting (no manual cleanup)
- Memory efficient (max 35 items)

### 4. Lazy Combo Update
- Only updates combo when search completes
- Blocks signals during update
- Prevents selection change events

## Edge Cases Handled

### Recent Searches
1. **Duplicate searches**: Moved to top, not duplicated
2. **Empty searches**: Not added to history
3. **Search with 0 results**: Still added (shows "0 results")
4. **Maximum capacity**: Oldest removed when > 35
5. **Missing data**: Checks if search_text in data dict

### Multi-Term Search
1. **Empty terms**: Filtered out (`if term.strip()`)
2. **Whitespace**: Trimmed from each term
3. **Single term with comma**: Handled as single term
4. **No results**: Returns empty DataFrame gracefully

### Filter Restoration
1. **Missing filters**: Checks for existence before restore
2. **Invalid values**: Only selects items that exist in list
3. **Empty selections**: Handled gracefully
4. **Signal blocking**: Prevents infinite loops

## Testing Recommendations

### Recent Searches
1. **Test capacity**: Add >35 searches, verify oldest removed
2. **Test scrolling**: Add >15 searches, verify scrollbar appears
3. **Test restoration**: Select search, verify all filters restored
4. **Test result counts**: Verify counts match actual results
5. **Test advanced vs input**: Verify correct label format

### Multi-Term Search
1. **Single term**: "D38999" → Verify works as before
2. **Two terms**: "D38999, VG95234" → Verify OR logic
3. **Many terms**: "A, B, C, D, E" → Verify all terms work
4. **Whitespace**: " D38999 , VG95234 " → Verify trimming
5. **No matches**: "INVALID1, INVALID2" → Verify empty result

### Data Limiting
1. **Small dataset**: <100 records → All loaded
2. **Large dataset**: >100 records → Limited to 100
3. **Search after limit**: Verify search works on subset
4. **Filter after limit**: Verify filters work correctly

## Code Locations

### View (`app/connector/Lookup/view.py`)
- `__init__()` - Initialize deque(maxlen=35) and data dict
- `_setup_footer()` - Set maxVisibleItems=15
- `add_search_to_history()` - New public method
- `_add_to_recent_searches()` - Enhanced with result count and formatting
- `_on_recent_search_selected()` - Full search restoration
- `_clear_all_selections()` - Clear all filters
- `_restore_multiselect_selections()` - Restore individual filter

### Presenter (`app/connector/Lookup/presenter.py`)
- `__init__()` - Add current_filters tracking
- `on_search()` - Store current_filters
- `_on_search_finished()` - Call add_search_to_history()
- `_convert_to_dataframe()` - Limit to 100 records
- SearchWorker.run() - Multi-term search logic

## Future Enhancements

1. **Smart data loading**: Load more data on demand when searching
2. **Search term highlighting**: Highlight matched terms in results
3. **Search analytics**: Track most common searches
4. **Export/import history**: Save favorite searches
5. **Search templates**: Pre-defined common searches
6. **Fuzzy matching**: Handle typos in search terms
7. **Search suggestions**: Auto-complete based on history
