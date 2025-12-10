# Tab Management Guide

This guide explains how to manage tabs in the productivity app

## Overview

The tab system is built around several key modules:
- **`tab_config.py`** - Single source of truth for tab definitions
- **`tab_loader.py`** - Handles lazy loading and dependency resolution
- **`tab_visibility_service.py`** - Manages tab visibility and persistence
- **`visibility_persistence.py`** - Persists visibility state to configuration
- **`main_window.py`** - Orchestrates tab loading and visibility

## Common Tasks

### How do I change a tab name?

Tab names are automatically extracted from the presenter class's `TAB_TITLE` attribute. To change a tab name:

**Option 1: Change the presenter class** (Recommended)
```python
# In your presenter class (e.g., epd_presenter.py)
class EpdPresenter:
    TAB_TITLE = "⚡ EPD Tool"  # Change this
```

**Option 2: Override in tab_config.py**
```python
# In tab_config.py, modify TAB_CONFIG
{
    'id': TabId.EPD,
    'title': '⚡ New EPD Name',  # Explicitly set title here
    'presenter_class': EpdPresenter,
    'view_class': EpdModuleView,
    'delay_ms': 50,
}
```

If both are present, the explicit `title` in `TAB_CONFIG` takes precedence over the presenter's `TAB_TITLE`.

---

### How do I change tab ordering?

Tab order is controlled by the sequence in the `TAB_CONFIG` list in `tab_config.py`.

```python
# In tab_config.py
TAB_CONFIG = [
    {
        'id': TabId.DOCUMENT_SCANNER,  # This loads first
        'presenter_class': DocumentScannerPresenter,
        'view_class': DocumentScannerModuleView,
        'delay_ms': 100,
    },
    {
        'id': TabId.EPD,  # This loads second
        'presenter_class': EpdPresenter,
        'view_class': EpdModuleView,
        'delay_ms': 50,
    },
    {
        'id': TabId.CONNECTORS,  # This loads third
        'presenter_class': ConnectorPresenter,
        'view_class': ConnectorModuleView,
        'delay_ms': 75,
    },
    # ... more tabs
]
```

**Important Notes:**
- Tabs are loaded in the order they appear in `TAB_CONFIG`
- The `delay_ms` value controls the delay *after* the previous tab loads
- Dependencies (via `depends_on`) may cause tabs to load out of order

---

### How do I change which is the default tab?

The default tab (which receives focus on startup) is set via the `default_focus` flag in `tab_config.py`.

```python
# In tab_config.py
TAB_CONFIG = [
    {
        'id': TabId.DOCUMENT_SCANNER,
        'presenter_class': DocumentScannerPresenter,
        'view_class': DocumentScannerModuleView,
        'delay_ms': 100,
        # No default_focus - not the default
    },
    {
        'id': TabId.EPD,
        'presenter_class': EpdPresenter,
        'view_class': EpdModuleView,
        'delay_ms': 50,
        'default_focus': True,  # <-- This tab gets focus on startup
    },
    # ... more tabs
]
```

**Rules:**
- Only **one** tab should have `'default_focus': True`
- If multiple tabs have this flag, the first one wins
- If no tab has this flag, no tab receives automatic focus
- The Settings tab is always added first but never receives default focus

---

### How do I switch to another tab programmatically?

Use the `TabVisibilityService` to change tabs programmatically.

**Method 1: Using the service directly**
```python
# Access the service via property (provides full type hints)
if self.services.tab_visibility:
    # Switch to a specific tab
    self.services.tab_visibility.set_focus(TabId.EPD)
```

**Method 2: From MainWindow**
```python
# In main_window.py or any class with access to services
def switch_to_epd_tab(self):
    if self.services.tab_visibility:
        self.services.tab_visibility.set_focus('epd')  # Use tab ID string
```

**Method 3: Using tab index**
```python
# Direct Qt approach (not recommended - bypasses services)
self.tabs.setCurrentIndex(2)  # Switch to third tab
```

**Finding the tab ID:**
```python
from .tab_config import TabId

# Use the enum
tab_id = TabId.EPD  # Returns 'epd'

# Or use the string directly
tab_id = 'epd'
```

---

### How do I persist tab visibility state?

Tab visibility can be persisted when you use the `TabVisibilityService` with `persist=True`.

**Show/Hide a tab with persistence:**
```python
# Access the service via property
if self.services.tab_visibility:
    # Hide a tab and persist to config
    self.services.tab_visibility.set_tab_as_hidden(TabId.EPD, persist=True)
    
    # Show a tab and persist to config
    self.services.tab_visibility.set_tab_as_visible(TabId.EPD, persist=True)
    
    # Check if a tab is visible
    is_visible = self.services.tab_visibility.is_tab_visible(TabId.EPD)
```

**Default behavior (no persistence):**
```python
# Show tab WITHOUT persisting to config (default behavior)
if self.services.tab_visibility:
    self.services.tab_visibility.set_tab_as_visible(TabId.EPD)
    
    # Hide tab WITHOUT persisting to config (default behavior)
    self.services.tab_visibility.set_tab_as_hidden(TabId.EPD)
```

**Where visibility is stored:**
- Visibility state is stored in the app settings configuration
- The configuration is managed by `AppSettingsConfig` in `core/app_settings_config.py`
- Persistence is handled by `TabVisibilityConfig` in `visibility_persistence.py`
- Settings are automatically saved to `.tool_config/app_settings.json`

**Checking visibility from config vs UI:**
```python
if self.services.tab_visibility:
    # Check config state (doesn't require tab to be loaded)
    is_visible = self.services.tab_visibility.is_tab_visible(TabId.EPD, check_ui=False)
    
    # Check actual UI state (requires tab to be loaded)
    is_visible = self.services.tab_visibility.is_tab_visible(TabId.EPD, check_ui=True)
```

---

## Advanced Configuration

### Adding a new tab

1. **Define the tab in `tab_config.py`:**
```python
from ..my_module.my_presenter import MyPresenter
from ..my_module.my_view import MyModuleView

TAB_CONFIG = [
    # ... existing tabs
    {
        'id': TabId.MY_MODULE,  # Add to TabId enum first
        'presenter_class': MyPresenter,
        'view_class': MyModuleView,
        'delay_ms': 100,
        'depends_on': ['epd'],  # Optional: load after EPD tab
        'default_focus': False,  # Optional: make this the default tab
    },
]
```

2. **Add the tab ID to the enum:**
```python
class TabId(str, Enum):
    # ... existing IDs
    MY_MODULE = 'my_module'
```

3. **The tab will automatically:**
   - Be loaded by `TabLoader`
   - Have its visibility managed by `TabVisibilityService`
   - Be available in the Settings tab for show/hide
   - Persist its visibility state

### Tab dependencies

Use `depends_on` to ensure tabs load in a specific order:

```python
{
    'id': TabId.ADVANCED_TOOL,
    'presenter_class': AdvancedPresenter,
    'view_class': AdvancedView,
    'delay_ms': 50,
    'depends_on': ['epd', 'connectors'],  # Won't load until EPD and Connectors are loaded
}
```

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│                         MainWindow                          │
│                     (Orchestration Layer)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ├─────────────────────┐
                              │                     │
                    ┌─────────▼──────────┐  ┌──────▼─────────────────┐
                    │    TabLoader       │  │ TabVisibilityService   │
                    │  (Lazy Loading)    │  │   (Show/Hide/Focus)    │
                    └─────────┬──────────┘  └──────┬─────────────────┘
                              │                     │
                              │                     │
                    ┌─────────▼──────────┐  ┌──────▼─────────────────┐
                    │    tab_config.py   │  │ visibility_persistence │
                    │ (Single Source of  │  │    (Config Storage)    │
                    │      Truth)        │  │                        │
                    └────────────────────┘  └────────────────────────┘
```

- **tab_config.py**: Define tabs, order, defaults
- **TabLoader**: Loads tabs with dependencies
- **TabVisibilityService**: Show/hide/focus tabs
- **visibility_persistence.py**: Save visibility to config
- **MainWindow**: Coordinates everything via signals

---

## Best Practices

1. **Always use `TabId` enum** instead of hardcoded strings
2. **Use `TabVisibilityService`** for programmatic tab switching, not direct Qt calls
3. **Set `persist=False`** during initial load to avoid overwriting user preferences
4. **Keep tab loading delays reasonable** (50-200ms) to balance UX and startup time
5. **Use dependencies sparingly** - they add complexity to load order
6. **One default focus tab only** - multiple defaults cause confusion
7. **Test visibility persistence** by restarting the app after hiding/showing tabs

---

## Troubleshooting

**Tab not showing up:**
- Check if it's in `TAB_CONFIG`
- Check if it's hidden in Settings → Tab Visibility
- Check console for loading errors

**Tab loads in wrong order:**
- Check `TAB_CONFIG` sequence
- Check `depends_on` dependencies
- Dependencies override config order

**Default tab not focusing:**
- Ensure only one tab has `'default_focus': True`
- Check that the tab ID exists in `tab_registry`
- Check console for warnings about missing default tab

**Visibility not persisting:**
- Ensure you're using `tab_visibility_service.set_tab_as_visible()/set_tab_as_hidden()`
- Check that `persist=True` is set (default is `False`)
- Verify `.tool_config/app_settings.json` is writable

---

## Examples from Production Code

### Example: EPD Tab Configuration
```python
{
    'id': TabId.EPD,
    'presenter_class': EpdPresenter,
    'view_class': EpdModuleView,
    'delay_ms': 50,
    'default_focus': True,  # EPD tab gets focus on startup
}
```

### Example: Switching to Document Scanner programmatically
```python
# From any presenter or view with access to services
def open_document_scanner(self):
    if self.services.tab_visibility:
        # First ensure it's visible
        self.services.tab_visibility.set_tab_as_visible(TabId.DOCUMENT_SCANNER)
        # Then switch to it
        self.services.tab_visibility.set_focus(TabId.DOCUMENT_SCANNER)
```

### Example: Conditionally showing tabs
```python
# In MainWindow or a presenter
def show_advanced_features(self, user_level: str):
    if not self.services.tab_visibility:
        return
    
    if user_level == 'advanced':
        self.services.tab_visibility.set_tab_as_visible(TabId.DEVOPS, persist=True)
        self.services.tab_visibility.set_tab_as_visible(TabId.REMOTE_DOCS, persist=True)
    else:
        self.services.tab_visibility.set_tab_as_hidden(TabId.DEVOPS, persist=True)
        self.services.tab_visibility.set_tab_as_hidden(TabId.REMOTE_DOCS, persist=True)
```
