# Removed Document Caching

## Changes Made

### Files Modified

1. **Configuration/presenter.py**
   - ✅ Removed `pandas` import (no longer needed)
   - ✅ Renamed `cache_dir` → `config_dir` (only stores config JSON)
   - ✅ Removed `_cache_document()` method
   - ✅ Updated `on_add_document()` to skip caching
   - ✅ Removed `cached_path` from document config

2. **Search/presenter.py**
   - ✅ Updated `_search_document()` to load files directly
   - ✅ Loads from `file_path` instead of `cached_path`
   - ✅ Uses `header_row` parameter when loading
   - ✅ Handles different file formats (.csv, .txt, .xlsx, .xls)

3. **Configuration/view.py**
   - ✅ Updated status label: "X document(s) configured" (removed "and cached")

## Why Caching Was Removed

### Problems with Caching:
1. **Data Staleness**: Cached files become outdated when source files change
2. **Disk Space**: Duplicates all data unnecessarily
3. **Complexity**: Extra code for cache management
4. **Confusion**: Users don't know when cache is refreshed
5. **File Sync Issues**: If source file moves/deletes, cache is orphaned

### Benefits of Direct File Access:
1. ✅ **Always Current**: Searches the latest data in source files
2. ✅ **No Duplication**: Source files are the only copy
3. ✅ **Simpler Code**: Less to maintain
4. ✅ **Transparent**: Users understand what's happening
5. ✅ **Live Updates**: File changes immediately reflected in searches

## How It Works Now

### Add Document Workflow
1. User adds document with file path and configuration
2. Configuration saved to JSON:
   ```json
   {
     "file_path": "C:/path/to/file.csv",
     "file_name": "file.csv",
     "doc_type": "default",
     "header_row": 0,
     "search_columns": ["Column1", "Column2"],
     "return_columns": ["Column1", "Column2"],
     "added_date": "2025-10-16T12:34:56"
   }
   ```
3. No caching happens - just stores the reference

### Search Workflow
1. User enters search term
2. For each configured document:
   - Load file directly using pandas:
     ```python
     if file_path.endswith('.xlsx'):
         df = pd.read_excel(file_path, header=header_row)
     else:
         df = pd.read_csv(file_path, header=header_row)
     ```
   - Search in specified columns
   - Return matches
3. Results displayed in Search tab

## Performance Considerations

### Potential Concerns:
- ❓ Loading large files on every search could be slow
- ❓ Multiple file I/O operations

### Mitigations:
- ✅ **Pandas is fast**: Efficiently loads and searches CSV/Excel files
- ✅ **User controls scope**: Only configured documents are searched
- ✅ **Lazy loading**: Files only loaded when search is executed
- ✅ **Simple searches**: Basic contains() is very fast

### Future Optimizations (if needed):
- Could add optional in-memory caching during session
- Could implement smart refresh (cache with file modification monitoring)
- Could add search indexing for very large files
- Could parallelize multi-document searches

## Configuration Storage

### What's Stored:
- `document_scanner_cache/documents_config.json`
- Contains array of document configurations
- No actual data - just metadata and file references

### What's NOT Stored:
- ❌ Cached CSV files
- ❌ Duplicate data
- ❌ Timestamps of cached files

### Example Config File:
```json
[
  {
    "file_path": "C:/data/parts.csv",
    "file_name": "parts.csv",
    "doc_type": "default",
    "header_row": 0,
    "search_columns": ["Part Number", "Description"],
    "return_columns": ["Part Number", "Description"],
    "precondition_enabled": false,
    "precondition": "",
    "added_date": "2025-10-16T10:30:00"
  },
  {
    "file_path": "C:/data/inventory.xlsx",
    "file_name": "inventory.xlsx",
    "doc_type": "default",
    "header_row": 1,
    "search_columns": ["SKU", "Name"],
    "return_columns": ["SKU", "Name"],
    "precondition_enabled": false,
    "precondition": "",
    "added_date": "2025-10-16T11:45:00"
  }
]
```

## File Access Patterns

### When Files Are Accessed:
1. **Add Document**: File opened during preview (Step 2)
2. **Search**: Files opened when search is executed
3. **Never**: Files are NOT opened on startup or configuration load

### Error Handling:
- ✅ File not found: Logged and skipped
- ✅ File format error: Caught and logged
- ✅ Missing columns: Gracefully handled
- ✅ Permission errors: Displayed to user

## Migration from Cached Version

### What Happens to Old Cached Files:
- They remain in `document_scanner_cache/` folder
- Can be manually deleted - no longer used
- Config file is updated without `cached_path` field

### Backward Compatibility:
- Old configs with `cached_path` will work
- System ignores `cached_path` and uses `file_path` instead
- Next save will remove `cached_path` from config

## Testing Checklist

- [ ] Add document with .csv file
- [ ] Add document with .txt file
- [ ] Add document with .xlsx file
- [ ] Search immediately after adding
- [ ] Modify source file externally
- [ ] Search again - verify results reflect changes
- [ ] Remove document
- [ ] Close and reopen app
- [ ] Verify documents still load from config
- [ ] Verify searches still work after restart
- [ ] Test with missing source file (moved/deleted)
- [ ] Verify error handling is graceful

## Benefits Summary

### Code Quality:
- ✅ **Less code**: Removed ~40 lines
- ✅ **Simpler logic**: One less concept to understand
- ✅ **Fewer dependencies**: Presenter doesn't need pandas

### User Experience:
- ✅ **Live data**: Always searching current file contents
- ✅ **Transparent**: Clear what's happening
- ✅ **No surprises**: No stale cache issues
- ✅ **Fast setup**: No cache creation delay

### Maintenance:
- ✅ **Fewer bugs**: Less code = less to break
- ✅ **Easier testing**: Direct file access is testable
- ✅ **Clear intent**: Code does what it says
