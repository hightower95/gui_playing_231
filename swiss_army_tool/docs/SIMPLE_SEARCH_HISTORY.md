# Simple Search History Feature

## Summary
Implemented a simple search history feature that:
- Retains the last 10 searches
- Allows clicking on a search term to re-run that search
- Persists history to `.tool_config/document_scanner.json`
- Fixed ConnectorContextProvider to check all values (not just specific columns)

## Changes Made

### 1. History View - Simple List UI
**File**: `app/document_scanner/History/view.py`

**Changes**:
- Replaced placeholder with functional UI
- Added `QListWidget` to display search history
- Added "🗑️ Clear History" button
- Added signals: `history_item_selected(str)`, `clear_history_requested()`
- Click on any item to re-run that search
- Shows "No search history yet" when empty

**UI Features**:
- Numbered list (1, 2, 3...)
- Most recent searches at top
- Clear history button (disabled when empty)
- Details shown in context area when clicked

### 2. History Presenter - Wire Up History
**File**: `app/document_scanner/History/presenter.py`

**Changes**:
- Replaced placeholder with functional presenter
- Takes `model` parameter (needs shared model)
- Added signal: `search_requested(str)` - emitted when history item clicked
- Methods:
  - `refresh_history()` - Updates view from model
  - `on_history_item_selected(search_term)` - Emits search_requested signal
  - `on_clear_history()` - Clears history in model
  - `on_search_performed(search_term)` - Called when search happens (currently unused, model handles it directly)

### 3. Document Scanner Model - History Storage
**File**: `app/document_scanner/document_scanner_model.py`

**Added Methods**:
- `get_search_history()` - Returns list of search terms (most recent first)
- `add_to_search_history(search_term)` - Adds term to history
  - Removes duplicates (moves to front)
  - Keeps only last 10
  - Saves to config
- `clear_search_history()` - Clears all history

### 4. Config Manager - History Persistence
**File**: `app/core/config_manager.py`

**Added to DocumentScannerConfig**:
- `save_search_history(history: List[str])` - Saves to config file
- `load_search_history()` - Loads from config file

**Storage Format**:
```json
{
  "documents": [...],
  "search_history": [
    "D38999",
    "connector",
    "USB",
    ...
  ]
}
```

### 5. Document Scanner Tab - Connect History to Search
**File**: `app/document_scanner/document_scanner_tab.py`

**Changes**:
- Pass `model` to HistoryPresenter
- Connect `history_presenter.search_requested` to `on_history_search_requested()`
- Added `on_history_search_requested()` method:
  - Switches to Search tab
  - Populates search input
  - Triggers search

### 6. Search Presenter - Record History
**File**: `app/document_scanner/Search/presenter.py`

**Changes**:
- Added `self.model.add_to_search_history(search_term)` at start of `on_search()`
- History is recorded every time a search is performed

### 7. Connector Context Provider - Fixed Lookup
**File**: `app/connector/connector_context_provider.py`

**Changes**:
- Removed test/debug context
- Now checks ALL values in result (not just specific columns)
- Skips empty values
- Looks up each value in connector database
- Returns first match found
- Adds descriptive console output when match found

## How It Works

### Recording History
1. User types search term and clicks Search
2. `SearchPresenter.on_search()` is called
3. **First thing it does**: `model.add_to_search_history(search_term)`
4. Model:
   - Gets current history from config
   - Removes duplicate if exists (to move to front)
   - Adds new term to front
   - Keeps only 10 most recent
   - Saves to `.tool_config/document_scanner.json`

### Viewing History
1. User switches to History tab
2. HistoryPresenter loads history from model
3. View displays as numbered list (most recent first)

### Re-running Search from History
1. User clicks on history item (e.g., "2. connector")
2. View emits `history_item_selected("connector")`
3. Presenter emits `search_requested("connector")`
4. DocumentScannerTab catches signal
5. Tab switches to Search tab
6. Populates search input with term
7. Triggers search

### Connector Context Provider Fix
**Before**: Only looked at specific column names (part number, pn, etc.)
**Now**: Looks at ALL values in the result

**Why**: Documents might have part numbers in columns named differently (e.g., "Component", "Part", "ID", etc.)

**How it works**:
- Iterates through all `matched_row_data` key-value pairs
- Skips empty values
- Tries to look up each value in connector database
- If match found, adds context and breaks (only one context per result)

## Usage Examples

### Example 1: Basic Usage
```
User searches for "D38999"
→ History adds "D38999" to top of list
→ Search results show with connector context

User searches for "USB"
→ History adds "USB" to top
→ List now: [USB, D38999]

User searches for "D38999" again
→ "D38999" moves back to top
→ List now: [D38999, USB]
```

### Example 2: History Re-run
```
History Tab shows:
  1. D38999
  2. connector
  3. USB-C

User clicks "2. connector"
→ Switches to Search tab
→ Search input shows "connector"
→ Search executes automatically
→ Results displayed
```

### Example 3: Connector Context
```
Document has columns: [Component, Description, Location]
Row data: {Component: "D38999/26WA35PN", Description: "Connector", Location: "A23"}

ConnectorContextProvider checks:
  - "D38999/26WA35PN" → Found in connector DB! ✓
  - Adds context with connector details
  
Result shows both:
  - Matched Data: Component, Description, Location
  - Additional Context [Connector]: Family, Shell Type, Material, etc.
```

## Configuration File Structure

`.tool_config/document_scanner.json`:
```json
{
  "documents": [
    {
      "file_path": "...",
      "file_name": "...",
      ...
    }
  ],
  "search_history": [
    "D38999",
    "connector",
    "USB-C",
    "cable",
    "EPD-123"
  ]
}
```

## Features

✅ **Last 10 Searches** - Automatically keeps most recent 10
✅ **Deduplication** - Same search moves to top (not duplicated)
✅ **Persistence** - Saved to config file, survives app restarts
✅ **Click to Search** - Click any history item to re-run
✅ **Clear History** - Button to wipe all history
✅ **Auto-Switch Tabs** - Clicking history switches to Search tab
✅ **Auto-Populate** - Search input filled automatically
✅ **Connector Context** - Now checks all values, not just specific columns

## Future Enhancements

Potential improvements:
- Show timestamp for each search
- Show result count for each search
- Filter/search within history
- Export history to file
- Pin favorite searches
- Delete individual history items
- Show which documents were searched
