# Start Page Module

## How do I make my tab appear in the start page?

Add a `TILE_CONFIG` dictionary to your tab's presenter or view class:

```python
class MyTabView(QWidget):
    MODULE_ID = 'my_module'
    
    TILE_CONFIG = {
        'module_id': MODULE_ID,
        'title': "🎯 My Feature",
        'subtitle': "Brief description of what this does",
        'bullets': [
            "Key feature 1",
            "Key feature 2", 
            "Key feature 3"
        ],
        'show_in_start_page': True,
        'user_guide_url': None  # Optional: Add URL to show User Guide button
    }
```

### Required Fields
- `module_id`: Unique identifier (should match `MODULE_ID`)
- `title`: Display title (supports emojis)
- `subtitle`: Brief description
- `bullets`: List of 3-4 key features
- `show_in_start_page`: Set to `True` to display tile

### Optional Fields
- `user_guide_url`: URL string - if provided, shows "User Guide" button on tile

### How It Works
The start page automatically scans all tabs registered in `TAB_CONFIG` (in `tab_config.py`), checks for `TILE_CONFIG`, and creates tiles for modules where `show_in_start_page` is `True`.

### Example
See `connector_tab.py`, `settings_tab.py`, or `document_scanner_tab.py` for working examples.
