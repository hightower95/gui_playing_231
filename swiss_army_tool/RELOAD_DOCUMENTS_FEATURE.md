# Reload All Documents Feature

## Summary
Added a "Reload All Documents" button to the Document Scanner Search tab that reloads all configured documents from disk. This is useful when source files have been updated externally and you want to pick up the changes without restarting the application or reconfiguring documents.

## Changes Made

### 1. Search View - Added Reload Button
**File**: `app/document_scanner/Search/view.py`

**Changes**:
- Added `reload_requested` signal
- Added "🔄 Reload All Documents" button next to the search button
- Added tooltip: "Reload all documents from disk to pick up any changes"
- Connected button to `_on_reload_requested()` handler
- Button is enabled/disabled based on document count (disabled when no documents configured)

### 2. Search Presenter - Connected Reload Signal
**File**: `app/document_scanner/Search/presenter.py`

**Changes**:
- Connected `view.reload_requested` signal to `on_reload_documents()` handler
- Added `on_reload_documents()` method that:
  - Prints reload message to console
  - Updates view status to show "Reloading all documents..."
  - Calls `model.reload_documents()`
  - Updates view status to show "Documents reloaded successfully"

### 3. Model - Existing Reload Support
**File**: `app/document_scanner/document_scanner_model.py`

**No changes needed** - The model already has a `reload_documents()` method that:
- Calls `_load_documents_async()` with current document configs
- Loads documents in background thread
- Emits `documents_changed` signal when complete

## How It Works

1. **User clicks "🔄 Reload All Documents" button**
2. **View emits `reload_requested` signal**
3. **Presenter handles signal**:
   - Updates status label to "Reloading all documents..."
   - Calls `model.reload_documents()`
4. **Model reloads documents**:
   - Creates new DocumentLoaderThread
   - Loads each document from disk in background thread
   - Updates progress as it goes
5. **Model emits `documents_changed` signal** when complete
6. **Presenters receive updated documents**:
   - Search presenter updates document count
   - Configuration presenter updates document list
7. **Status updated to "Documents reloaded successfully"**

## Use Cases

### 1. External File Updates
If you're editing a CSV/Excel file externally and want the Document Scanner to see the changes:
- Save your file
- Click "🔄 Reload All Documents"
- Search again to see updated results

### 2. File Content Changes
If the structure of your file hasn't changed but the data has:
- No need to reconfigure the document
- Just reload to pick up new/changed rows

### 3. Troubleshooting
If search results seem stale or incorrect:
- Reload to ensure you're working with current file contents

## Button State

The reload button is:
- **Enabled** when documents are configured (count > 0)
- **Disabled** when no documents are configured (count = 0)
- Shows tooltip on hover explaining its purpose

## UI Layout

```
[Search Term: ____________] [🔍 Search All Documents] [🔄 Reload All Documents]
```

## Console Output

When reload is triggered:
```
🔄 Reloading all documents...
Loading documents...
  ✓ Loaded: document1.csv (50 rows, 5 columns)
  ✓ Loaded: document2.xlsx (100 rows, 8 columns)
```

## Future Enhancements

Potential improvements:
- Add keyboard shortcut (e.g., Ctrl+R)
- Show progress bar during reload
- Add auto-reload option (watch files for changes)
- Reload individual documents (per-document reload button)
- Show last reload timestamp
