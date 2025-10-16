# Connector Search Implementation

## Overview
Implemented asynchronous search functionality for the Connector Lookup feature, connecting multiselect filters and text search to the model without blocking the GUI thread.

## Architecture

### 1. **View Layer** (`app/connector/Lookup/view.py`)

#### Signal Connections
- All multiselect widgets (left and right) are connected to `itemSelectionChanged` signal
- Text search input connected to `returnPressed` signal
- Search button connected to `clicked` signal
- All trigger `_on_filter_changed()` or `_on_search_clicked()`

#### Filter Collection
```python
def _get_selected_filters(self) -> dict:
    """Returns dict with lists of selected values for each filter"""
    {
        'search_text': str,
        'standard': [list of selected standards],
        'shell_type': [list of selected shell types],
        'material': [list of selected materials],
        'shell_size': [list of selected shell sizes],
        'insert_arrangement': [list of selected insert arrangements],
        'socket_type': [list of selected socket types],
        'keying': [list of selected keyings]
    }
```

#### Key Methods
- `_connect_filter_signals()`: Connects all 14 list widgets (7 filters × 2 columns) to filter change handler
- `_on_filter_changed()`: Triggered when any multiselect changes - emits `search_requested` signal
- `_on_search_clicked()`: Triggered by search button or Enter key - emits `search_requested` signal
- `_on_clear_clicked()`: Clears all filters and search input

### 2. **Presenter Layer** (`app/connector/Lookup/presenter.py`)

#### SearchWorker (QObject)
**Purpose**: Performs filtering in a background thread to avoid blocking the GUI

**Key Features**:
- Runs in separate QThread
- Applies all filters to DataFrame
- Supports multiple selections per filter (uses `isin()` for filtering)
- Can be cancelled if new search is triggered

**Filter Logic**:
```python
# Text search - searches across all columns
if search_text:
    mask = df.apply(lambda row: row.astype(str).str.lower().str.contains(search_text).any(), axis=1)

# Multiselect filters - uses isin() for multiple selections
if standards:
    filtered_df = filtered_df[filtered_df['Family'].isin(standards)]
```

#### Async Search Flow
1. User changes filter → `search_requested` signal emitted
2. `on_search()` receives filters dict
3. Cancel any existing search thread
4. Create new `SearchWorker` with current DataFrame and filters
5. Create new `QThread` and move worker to it
6. Connect signals and start thread
7. Worker runs filtering in background
8. `_on_search_finished()` receives filtered DataFrame
9. Update table model and statistics

### 3. **Thread Safety**

#### Why This Approach is Thread-Safe:
- **SearchWorker runs in background thread**: No GUI blocking during filtering
- **DataFrame is copied**: Worker operates on copy, original data unchanged
- **Signal/Slot mechanism**: Qt's signal/slot system is thread-safe across threads
- **GUI updates only on main thread**: `_on_search_finished()` runs on main thread via signal

#### Key Points:
- Search operations run asynchronously using `QThread`
- GUI remains responsive during filtering
- Multiple rapid filter changes handled gracefully (previous search cancelled)
- Model data loading also uses separate `ConnectorDataWorker` thread

## User Interactions

### Multiselect Filter Change
1. User clicks item in any multiselect → `itemSelectionChanged` emitted
2. View collects all current filter values
3. `search_requested` signal emitted with filters dict
4. Presenter starts async search
5. Results updated when complete

### Text Search
1. User types in search box and presses Enter → `returnPressed` emitted
2. OR user clicks Search button → `clicked` emitted
3. Both trigger `_on_search_clicked()`
4. Same async search flow as filter change

### Clear Filters
1. User clicks Clear button
2. All multiselects cleared
3. Search input cleared
4. `clear_filters_requested` signal emitted
5. Presenter resets to full dataset

## Data Flow

```
User Action
    ↓
View (collects filters)
    ↓
Signal: search_requested(filters: dict)
    ↓
Presenter: on_search(filters)
    ↓
Create SearchWorker + QThread
    ↓
SearchWorker.run() [BACKGROUND THREAD]
    ↓
Apply filters to DataFrame copy
    ↓
Signal: finished(filtered_df)
    ↓
Presenter: _on_search_finished() [MAIN THREAD]
    ↓
Update table model
    ↓
View updates table display
```

## Performance Considerations

1. **Filtering is fast**: Pandas operations are optimized for large datasets
2. **Thread overhead minimal**: Thread creation is fast, searching is the bottleneck
3. **Cancellation prevents queue buildup**: Rapid filter changes don't stack up
4. **DataFrame copy is cheap**: Copy-on-write semantics in pandas

## Future Enhancements

1. **Debouncing**: Add small delay before triggering search (e.g., 300ms) to avoid excessive searches
2. **Loading indicator**: Show spinner or progress during search
3. **Result caching**: Cache results for common filter combinations
4. **Incremental filtering**: Apply filters incrementally rather than all at once
5. **Search history**: Track and allow reverting to previous search states

## Testing Recommendations

1. **Test rapid filter changes**: Click multiple filters quickly, verify no crashes
2. **Test large datasets**: Load 10,000+ records, verify no GUI freezing
3. **Test all filter combinations**: Ensure all 7 filters work correctly
4. **Test empty results**: Verify graceful handling when no matches
5. **Test clear functionality**: Ensure clear resets all state correctly
