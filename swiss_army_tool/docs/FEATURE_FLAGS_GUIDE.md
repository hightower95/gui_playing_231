# Feature Flags Implementation Guide

## Overview

The feature flags system allows you to control application features dynamically through the Settings tab. Feature flags are persisted to disk and apply instantly without requiring an application restart.

**Key Benefits:**
- ✅ Toggle features on/off without code changes
- ✅ Instant updates (no restart required)
- ✅ Persistent across sessions
- ✅ Thread-safe with async disk saves
- ✅ Easy to add new flags
- ✅ Scrollable UI for many flags

---

## Architecture

### Components

1. **FeatureFlagsConfig** (`app/tabs/settings_tab.py`)
   - Manages feature flag state with in-memory caching
   - Handles async persistence to `.tool_config/app_settings.json`
   - Thread-safe operations

2. **SettingsTab** (`app/tabs/settings_tab.py`)
   - Displays feature flags in a scrollable list
   - Emits `feature_flag_changed` signal when flags change
   - Auto-generates UI from flag definitions

3. **MainWindow** (`app/tabs/main_window.py`)
   - Routes feature flag changes to appropriate presenters
   - Central hub for flag change notifications

4. **Feature-specific Presenters**
   - Listen for relevant flag changes
   - Update their views accordingly
   - Example: `RemoteDocsPresenter` controls upload section visibility

---

## How to Add a New Feature Flag

### Step 1: Define the Feature Flag

Edit `app/tabs/settings_tab.py` and add your flag to the `FEATURE_FLAGS` dictionary in `FeatureFlagsConfig`:

```python
class FeatureFlagsConfig:
    # ...
    
    FEATURE_FLAGS = {
        'remote_docs_upload': (
            'Remote Docs Upload', 
            'Show file upload section in Remote Documents tab',
            True  # Default value
        ),
        
        # Add your new flag here:
        'my_new_feature': (
            'My New Feature',           # Display name (shown in UI)
            'Description of feature',   # Tooltip description
            False                        # Default: enabled (True) or disabled (False)
        ),
    }
```

**That's it!** The checkbox will automatically appear in the Settings tab.

---

### Step 2: Check Feature Flag in Your Code

Use `FeatureFlagsConfig.is_enabled()` to check if a flag is enabled:

```python
from app.tabs.settings_tab import FeatureFlagsConfig

# In your presenter's __init__ or wherever needed:
if FeatureFlagsConfig.is_enabled('my_new_feature'):
    # Feature is enabled
    self.view.show_experimental_section()
else:
    # Feature is disabled
    self.view.hide_experimental_section()
```

---

### Step 3: React to Flag Changes (Optional)

If you need to respond to flag changes while the app is running:

#### 3a. Add Handler to Your Presenter

```python
class MyPresenter(QObject):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.view = MyView()
        
        # Initialize based on current flag state
        self._update_feature_visibility()
    
    def _update_feature_visibility(self):
        """Update UI based on feature flag"""
        enabled = FeatureFlagsConfig.is_enabled('my_new_feature')
        self.view.set_feature_visible(enabled)
    
    def on_feature_flag_changed(self, flag_id: str, enabled: bool):
        """Handle feature flag changes
        
        Args:
            flag_id: ID of the feature flag that changed
            enabled: New state of the flag
        """
        if flag_id == 'my_new_feature':
            self.view.set_feature_visible(enabled)
            print(f"[MyPresenter] Feature visibility changed to: {enabled}")
```

#### 3b. Connect to MainWindow Signal

Edit `app/tabs/main_window.py` and add routing in `_on_feature_flag_changed`:

```python
def _on_feature_flag_changed(self, flag_id: str, enabled: bool):
    """Handle feature flag change from Settings"""
    print(f"MainWindow: Feature flag changed - {flag_id} -> {enabled}")
    
    # Route to appropriate presenter
    if flag_id == 'remote_docs_upload':
        self.remote_docs.on_feature_flag_changed(flag_id, enabled)
    
    # Add your routing here:
    elif flag_id == 'my_new_feature':
        self.my_presenter.on_feature_flag_changed(flag_id, enabled)
```

---

## Complete Example: Adding a Debug Mode Flag

### 1. Define the Flag

```python
# In app/tabs/settings_tab.py - FeatureFlagsConfig class
FEATURE_FLAGS = {
    'remote_docs_upload': (...),  # existing flags
    
    'debug_mode': (
        'Debug Mode',
        'Show debug information and additional logging',
        False  # Disabled by default
    ),
}
```

### 2. Use in Your Code

```python
# In any presenter or view
from app.tabs.settings_tab import FeatureFlagsConfig

class MyPresenter(QObject):
    def __init__(self, context):
        super().__init__()
        self.debug_mode = FeatureFlagsConfig.is_enabled('debug_mode')
        
    def process_data(self, data):
        if self.debug_mode:
            print(f"[DEBUG] Processing data: {data}")
        
        # ... normal processing ...
```

### 3. React to Changes (Optional)

```python
# In presenter
def on_feature_flag_changed(self, flag_id: str, enabled: bool):
    if flag_id == 'debug_mode':
        self.debug_mode = enabled
        if enabled:
            print("[DEBUG] Debug mode enabled")
        else:
            print("[DEBUG] Debug mode disabled")

# In main_window.py - _on_feature_flag_changed
elif flag_id == 'debug_mode':
    # Broadcast to all presenters that need it
    self.epd.on_feature_flag_changed(flag_id, enabled)
    self.connectors.on_feature_flag_changed(flag_id, enabled)
    self.fault_finding.on_feature_flag_changed(flag_id, enabled)
```

---

## API Reference

### FeatureFlagsConfig

**Static Methods:**

```python
# Check if a flag is enabled
enabled = FeatureFlagsConfig.is_enabled('flag_id')
# Returns: bool

# Get all flags and their states
all_flags = FeatureFlagsConfig.get_all_flags()
# Returns: dict[str, bool]

# Set a flag (rarely needed - usually done via UI)
FeatureFlagsConfig.set_flag('flag_id', True)
# Returns: bool (always True, save is async)
```

### SettingsTab Signals

```python
# Emitted when any feature flag changes
settings_tab.feature_flag_changed.connect(handler)
# Signal signature: (flag_id: str, enabled: bool)

# Example handler:
def on_flag_changed(flag_id: str, enabled: bool):
    print(f"Flag {flag_id} changed to {enabled}")
```

---

## Best Practices

### 1. **Naming Conventions**

- Use `snake_case` for flag IDs: `my_feature_flag`
- Use descriptive names: `remote_docs_upload` not `upload`
- Prefix related flags: `search_advanced`, `search_fuzzy`, `search_regex`

### 2. **Default Values**

- **Stable features**: Default to `True` (enabled)
- **Experimental features**: Default to `False` (disabled)
- **Breaking changes**: Default to `False`, enable after testing

### 3. **Descriptions**

Write clear, user-friendly descriptions:

```python
# ❌ Bad
'experimental_search': ('Exp Search', 'New search', False)

# ✅ Good
'experimental_search': (
    'Experimental Search',
    'Enable new search algorithm with fuzzy matching and regex support',
    False
)
```

### 4. **Flag Cleanup**

Remove flags when features are:
- Fully stable and always enabled → Remove flag, enable permanently
- Fully deprecated → Remove flag and feature code

### 5. **Testing**

Test both states of each flag:
```python
# Test with flag enabled
FeatureFlagsConfig.set_flag('my_feature', True)
assert my_view.is_feature_visible()

# Test with flag disabled
FeatureFlagsConfig.set_flag('my_feature', False)
assert not my_view.is_feature_visible()
```

---

## Common Use Cases

### 1. **Control UI Section Visibility**

```python
# In view
def set_advanced_panel_visible(self, visible: bool):
    self.advanced_panel.setVisible(visible)

# In presenter
def _update_advanced_panel(self):
    enabled = FeatureFlagsConfig.is_enabled('show_advanced_panel')
    self.view.set_advanced_panel_visible(enabled)
```

### 2. **Enable/Disable Functionality**

```python
def on_search_clicked(self):
    if FeatureFlagsConfig.is_enabled('regex_search'):
        results = self._regex_search(self.query)
    else:
        results = self._simple_search(self.query)
```

### 3. **Beta Features**

```python
# In __init__
if FeatureFlagsConfig.is_enabled('beta_features'):
    self.view.add_beta_tab()
    self.view.show_beta_badge()
```

### 4. **Performance Optimization Toggles**

```python
def load_data(self):
    if FeatureFlagsConfig.is_enabled('fast_loading'):
        return self._load_with_cache()
    else:
        return self._load_from_disk()
```

---

## Storage Format

Feature flags are stored in `.tool_config/app_settings.json`:

```json
{
  "tab_visibility": {
    "epd": true,
    "connectors": true,
    "fault_finding": true,
    "document_scanner": true,
    "remote_docs": true
  },
  "feature_flags": {
    "remote_docs_upload": true,
    "debug_mode": false,
    "experimental_search": false
  }
}
```

---

## Troubleshooting

### Flag doesn't appear in Settings UI

**Check:**
1. Is the flag defined in `FEATURE_FLAGS` dictionary?
2. Did you restart the application after adding it?
3. Check console for errors during Settings tab initialization

### Flag state doesn't persist

**Check:**
1. `.tool_config` directory exists and is writable
2. No errors in console about disk saves
3. `AppSettingsConfig` is configured correctly

### Flag change doesn't update UI

**Check:**
1. Is your presenter's `on_feature_flag_changed` method connected?
2. Is the routing in `MainWindow._on_feature_flag_changed` correct?
3. Does your view's visibility method work correctly?

### Flag value is always the default

**Check:**
1. Call `FeatureFlagsConfig.is_enabled()` each time, don't cache the value
2. Or, update cached value in `on_feature_flag_changed` handler

---

## Migration Guide

### From Hardcoded Boolean to Feature Flag

**Before:**
```python
class MyPresenter:
    def __init__(self):
        self.enable_upload = True  # Hardcoded
```

**After:**
```python
class MyPresenter:
    def __init__(self):
        # Check flag on initialization
        self._update_upload_visibility()
    
    def _update_upload_visibility(self):
        enabled = FeatureFlagsConfig.is_enabled('my_upload_feature')
        self.view.set_upload_visible(enabled)
    
    def on_feature_flag_changed(self, flag_id: str, enabled: bool):
        if flag_id == 'my_upload_feature':
            self.view.set_upload_visible(enabled)
```

---

## Advanced: Multiple Flags for One Feature

Sometimes a feature needs multiple related flags:

```python
FEATURE_FLAGS = {
    'search_fuzzy': ('Fuzzy Search', 'Enable fuzzy matching', False),
    'search_regex': ('Regex Search', 'Enable regex patterns', False),
    'search_case_sensitive': ('Case Sensitive', 'Match case exactly', True),
}

# In search logic:
def search(self, query):
    options = {
        'fuzzy': FeatureFlagsConfig.is_enabled('search_fuzzy'),
        'regex': FeatureFlagsConfig.is_enabled('search_regex'),
        'case_sensitive': FeatureFlagsConfig.is_enabled('search_case_sensitive'),
    }
    return self.search_engine.search(query, **options)
```

---

## Summary Checklist

When adding a new feature flag:

- [ ] Add to `FEATURE_FLAGS` dictionary with clear name and description
- [ ] Set appropriate default value (True for stable, False for experimental)
- [ ] Use `FeatureFlagsConfig.is_enabled('flag_id')` in your code
- [ ] Add `on_feature_flag_changed` handler if dynamic updates needed
- [ ] Route flag changes in `MainWindow._on_feature_flag_changed`
- [ ] Test both enabled and disabled states
- [ ] Document the flag's purpose in code comments
- [ ] Update this guide if adding complex patterns

---

## Related Documentation

- [Settings Tab Implementation](./SETTINGS_TAB_IMPLEMENTATION.md)
- [Tab Visibility System](./TAB_VISIBILITY_GUIDE.md)
- [Configuration Management](./CONFIG_MANAGEMENT.md)

---

**Last Updated:** October 20, 2025
