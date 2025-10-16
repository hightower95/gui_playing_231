# Configuration System Migration to .tool_config

## Summary

Successfully implemented a centralized configuration system using a `.tool_config` directory to store document locations and settings between sessions.

## Changes Made

### 1. Created Centralized Configuration Manager

**File:** `app/core/config_manager.py`

New module with three classes:

#### `ConfigManager` (Base Class)
- Manages the `.tool_config` directory
- Provides generic save/load/delete operations for JSON files
- Handles initialization and error logging

**Methods:**
- `initialize()` - Creates .tool_config directory on startup
- `save_config(name, data)` - Save any JSON-serializable data
- `load_config(name, default)` - Load data with fallback default
- `config_exists(name)` - Check if config file exists
- `delete_config(name)` - Remove a config file

#### `DocumentScannerConfig` (Helper Class)
- Specialized helper for Document Scanner configurations
- Wraps documents in proper JSON structure

**Methods:**
- `save_documents(documents)` - Save list of document configs
- `load_documents()` - Load document configs (returns list)
- `clear_documents()` - Remove all document configs

#### `AppSettingsConfig` (Helper Class)
- For future application-wide settings
- Key-value storage with get/set methods

**Methods:**
- `save_settings(settings)` - Save settings dictionary
- `load_settings()` - Load settings dictionary
- `get_setting(key, default)` - Get single setting
- `set_setting(key, value)` - Set single setting

### 2. Updated Document Scanner Configuration Presenter

**File:** `app/document_scanner/Configuration/presenter.py`

**Changes:**
- ✅ Removed `json` and `Path` imports (now uses config_manager)
- ✅ Removed `self.config_dir` and `self.config_file` attributes
- ✅ Updated `_save_config()` to use `DocumentScannerConfig.save_documents()`
- ✅ Updated `_load_config()` to use `DocumentScannerConfig.load_documents()`
- ✅ Simplified error handling (delegated to ConfigManager)

**Before:**
```python
self.config_dir = Path("document_scanner_cache")
self.config_file = self.config_dir / "documents_config.json"
with open(self.config_file, 'w') as f:
    json.dump(self.documents, f, indent=2)
```

**After:**
```python
DocumentScannerConfig.save_documents(self.documents)
```

### 3. Updated Main Application

**File:** `main.py`

**Changes:**
- ✅ Added `ConfigManager.initialize()` call on startup
- ✅ Creates `.tool_config` directory before app runs

**Before:**
```python
def main():
    app = QApplication(sys.argv)
    context = AppContext()
```

**After:**
```python
def main():
    app = QApplication(sys.argv)
    ConfigManager.initialize()  # Create .tool_config directory
    context = AppContext()
```

### 4. Created Documentation

**File:** `.tool_config/README.md`

- Explains directory structure
- Documents configuration file formats
- Lists all configuration fields
- Provides usage notes

### 5. Created Migration Script

**File:** `migrate_config.py`

Standalone script to migrate existing configurations:
- Reads old `document_scanner_cache/documents_config.json`
- Saves to new `.tool_config/document_scanner.json`
- Creates backup of old file
- Provides detailed migration summary

**Usage:**
```bash
python migrate_config.py
```

### 6. Updated .gitignore

Added entries to ignore configuration directories:
```
.tool_config/
document_scanner_cache/
e3_caches/
```

## New Directory Structure

```
swiss_army_tool/
├── .tool_config/                    # ← NEW: Centralized config directory
│   ├── README.md                    # Documentation
│   └── document_scanner.json        # Document locations
├── app/
│   └── core/
│       └── config_manager.py        # ← NEW: Configuration manager
├── main.py                          # Updated to initialize config
└── migrate_config.py                # ← NEW: Migration script
```

## Configuration File Format

**Location:** `.tool_config/document_scanner.json`

```json
{
  "documents": [
    {
      "file_path": "C:/data/parts.csv",
      "file_name": "parts.csv",
      "doc_type": "default",
      "header_row": 0,
      "search_columns": ["Part Number", "Description"],
      "return_columns": ["Part Number", "Description"],
      "precondition_enabled": false,
      "precondition": "",
      "added_date": "2025-10-16T12:34:56"
    }
  ]
}
```

## Benefits

### ✅ Centralized Configuration
- All config files in one location (`.tool_config/`)
- Easy to find and manage
- Consistent naming scheme

### ✅ Better Code Organization
- Single source of truth for config operations
- Reusable across different modules
- Eliminates duplicate file I/O code

### ✅ Future-Proof
- Easy to add new config types
- `AppSettingsConfig` ready for app-wide settings
- Extensible base classes

### ✅ Error Handling
- Centralized error logging
- Graceful fallbacks with defaults
- Full exception tracebacks

### ✅ Git-Friendly
- `.tool_config/` ignored by default
- Prevents user-specific paths in version control
- Clean repository

## Migration Path

### For Existing Users

1. **Run migration script:**
   ```bash
   python migrate_config.py
   ```

2. **Verify migration:**
   - Check `.tool_config/document_scanner.json` exists
   - Run application and verify documents load
   - Test adding/removing documents

3. **Clean up (optional):**
   ```bash
   # After verifying everything works
   Remove-Item -Recurse document_scanner_cache/
   ```

### For New Users

Nothing needed! The `.tool_config` directory is created automatically on first run.

## Usage Examples

### Saving Document Configurations

```python
from app.core.config_manager import DocumentScannerConfig

documents = [
    {
        'file_path': 'C:/data/parts.csv',
        'file_name': 'parts.csv',
        'header_row': 0,
        'search_columns': ['Part Number'],
        # ... other fields
    }
]

DocumentScannerConfig.save_documents(documents)
```

### Loading Document Configurations

```python
from app.core.config_manager import DocumentScannerConfig

documents = DocumentScannerConfig.load_documents()
# Returns [] if no config exists
```

### Future: Application Settings

```python
from app.core.config_manager import AppSettingsConfig

# Save a setting
AppSettingsConfig.set_setting('theme', 'dark')

# Load a setting
theme = AppSettingsConfig.get_setting('theme', default='light')
```

### Future: Custom Config Files

```python
from app.core.config_manager import ConfigManager

# Save custom data
my_data = {'key': 'value'}
ConfigManager.save_config('my_feature.json', my_data)

# Load custom data
my_data = ConfigManager.load_config('my_feature.json', default={})
```

## Testing

### Verify Configuration System

1. **Start application:**
   ```bash
   python main.py
   ```
   
   Console should show:
   ```
   ✓ Configuration directory: C:\path\to\.tool_config
   ```

2. **Add a document:**
   - Drag/drop a CSV file
   - Configure columns
   - Add to list

3. **Check config file created:**
   ```bash
   cat .tool_config/document_scanner.json
   ```

4. **Restart application:**
   - Document should reload automatically
   - Console shows: `Documents found: 1`

5. **Remove document:**
   - Delete from list
   - Config file updates immediately

## Rollback Plan

If issues occur, you can rollback to the old system:

1. Restore the Configuration presenter imports:
   ```python
   import json
   from pathlib import Path
   ```

2. Restore old attributes in `__init__`:
   ```python
   self.config_dir = Path("document_scanner_cache")
   self.config_file = self.config_dir / "documents_config.json"
   self.config_dir.mkdir(exist_ok=True)
   ```

3. Restore old `_save_config()` and `_load_config()` methods

4. Remove `ConfigManager.initialize()` from main.py

## Future Enhancements

### Potential Uses for AppSettingsConfig

- Window size/position persistence
- Last used directories
- Recent file lists
- User preferences (theme, font size, etc.)
- Feature flags/toggles

### Potential New Config Types

- `E3Config` - E3 cache settings
- `ConnectorConfig` - Recent searches, favorites
- `EpdConfig` - Filter presets, saved queries
- `UserPreferences` - UI customization

## Notes

- Config directory is created in the project root (same level as main.py)
- All paths in configs are absolute (portable across sessions)
- JSON format allows manual editing if needed
- Files are saved with 2-space indentation for readability
- Migration script is idempotent (safe to run multiple times)
