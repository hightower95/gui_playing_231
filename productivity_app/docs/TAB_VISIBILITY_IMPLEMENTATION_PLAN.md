# Tab Visibility Implementation Plan

**Created:** October 20, 2025  
**Status:** Settings Tab Complete - Ready for EPD Tab Integration

---

## Overview

Implementing dynamic tab visibility controls through a Settings tab. All tabs are visible by default, and users can toggle individual tab visibility with instant effect (no restart required).

**Phase 1:** Settings Tab + EPD Tab (Current)  
**Phase 2:** Remaining Tabs (Connectors, Fault Finding, Document Scanner, Remote Docs)

---

## ✅ Completed: Settings Tab

### What Was Built

**File:** `app/tabs/settings_tab.py` (343 lines)

#### Components Created:

1. **`TabVisibilityConfig` Class** - Configuration management
   - `get_visibility_settings()` - Load all tab visibility settings
   - `set_visibility_settings(settings)` - Save all settings
   - `get_tab_visibility(tab_name)` - Get specific tab state
   - `set_tab_visibility(tab_name, visible)` - Set specific tab state
   - Uses `ConfigManager` for persistence to `.tool_config/app_settings.json`

2. **`SettingsTab` Widget** - UI implementation
   - **Signals:**
     - `tab_visibility_changed(str, bool)` - Emits when a tab visibility changes
     - `settings_changed(dict)` - Emits when any setting changes
   
   - **UI Sections:**
     - **Tab Visibility Group** (collapsible)
       - Checkbox for each tab with tooltips
       - Help text explaining instant updates
       - Individual checkboxes: EPD Tools, Connectors, Fault Finding, Document Scanner, Remote Docs
     
     - **Quick Presets Group**
       - "Show All Tabs" button (green/success)
       - "Hide All Tabs" button (with confirmation)
     
     - **Action Buttons**
       - "Reset to Defaults" (restores all tabs to visible)
   
   - **Features:**
     - Changes apply instantly (no restart)
     - Settings persist across sessions
     - Signals blocked during load to prevent false triggers
     - Confirmation dialogs for destructive actions
     - Informational messages for preset actions

### Data Structure

**Config Location:** `.tool_config/app_settings.json`

```json
{
  "tab_visibility": {
    "epd": true,
    "connectors": true,
    "fault_finding": true,
    "document_scanner": true,
    "remote_docs": true
  }
}
```

**Default State:** All tabs visible (`true`)

---

## 🔄 Next Phase: EPD Tab Integration

### Implementation Plan for EPD Tab

The EPD tab needs to be dynamically shown/hidden based on the Settings tab configuration.

#### Step 1: Track Tab References in MainWindow

**File to Edit:** `app/tabs/main_window.py`

**Current Code:**
```python
self.tabs.addTab(self.epd.view, self.epd.title)
```

**New Code:**
```python
# Store reference to tab index
self.epd_tab_index = self.tabs.addTab(self.epd.view, self.epd.title)

# Store tab info for management
self.tab_registry = {
    'epd': {
        'presenter': self.epd,
        'view': self.epd.view,
        'title': self.epd.title,
        'index': self.epd_tab_index
    }
}
```

#### Step 2: Initialize Settings Tab First

**In `MainWindow.__init__`:**

```python
# Initialize Settings tab FIRST (before other tabs)
self.settings_tab = SettingsTab()

# Connect signals
self.settings_tab.tab_visibility_changed.connect(self._on_tab_visibility_changed)

# ... then initialize other presenters ...
```

#### Step 3: Apply Initial Visibility

After adding all tabs, apply saved visibility settings:

```python
def _apply_initial_tab_visibility(self):
    """Apply saved tab visibility settings on startup"""
    # EPD tab
    if not self.settings_tab.is_tab_visible('epd'):
        self._hide_tab('epd')
    
    # ... (will add more tabs in phase 2)
```

#### Step 4: Implement Dynamic Show/Hide

Add helper methods to MainWindow:

```python
def _on_tab_visibility_changed(self, tab_name: str, visible: bool):
    """Handle tab visibility change from Settings
    
    Args:
        tab_name: Name of tab (e.g., 'epd')
        visible: True to show, False to hide
    """
    if visible:
        self._show_tab(tab_name)
    else:
        self._hide_tab(tab_name)

def _show_tab(self, tab_name: str):
    """Show a tab if it's hidden
    
    Args:
        tab_name: Name of tab to show
    """
    if tab_name not in self.tab_registry:
        return
    
    tab_info = self.tab_registry[tab_name]
    
    # Check if tab is already visible
    for i in range(self.tabs.count()):
        if self.tabs.widget(i) == tab_info['view']:
            return  # Already visible
    
    # Find correct position to insert
    position = self._get_tab_position(tab_name)
    
    # Insert tab at correct position
    self.tabs.insertTab(position, tab_info['view'], tab_info['title'])
    
    print(f"✓ Shown tab: {tab_info['title']}")

def _hide_tab(self, tab_name: str):
    """Hide a tab if it's visible
    
    Args:
        tab_name: Name of tab to hide
    """
    if tab_name not in self.tab_registry:
        return
    
    tab_info = self.tab_registry[tab_name]
    
    # Find and remove tab
    for i in range(self.tabs.count()):
        if self.tabs.widget(i) == tab_info['view']:
            self.tabs.removeTab(i)
            print(f"✓ Hidden tab: {tab_info['title']}")
            break

def _get_tab_position(self, tab_name: str) -> int:
    """Get the correct position to insert a tab
    
    Maintains the tab order: EPD -> Connectors -> Fault Finding -> 
                            Document Scanner -> Remote Docs -> Settings
    
    Args:
        tab_name: Name of tab to position
        
    Returns:
        Index where tab should be inserted
    """
    # Define desired order
    tab_order = ['epd', 'connectors', 'fault_finding', 
                 'document_scanner', 'remote_docs']
    
    if tab_name not in tab_order:
        return self.tabs.count() - 1  # Before Settings tab
    
    target_index = tab_order.index(tab_name)
    
    # Count how many tabs before this one are currently visible
    position = 0
    for i in range(target_index):
        other_tab_name = tab_order[i]
        if other_tab_name in self.tab_registry:
            other_view = self.tab_registry[other_tab_name]['view']
            # Check if visible
            for j in range(self.tabs.count()):
                if self.tabs.widget(j) == other_view:
                    position += 1
                    break
    
    return position
```

#### Step 5: Add Settings Tab at End

```python
# Add Settings tab last (always visible)
self.tabs.addTab(self.settings_tab, "⚙️ Settings")
```

### Code Changes Summary for EPD Tab

**File: `app/tabs/main_window.py`**

**Changes:**
1. Import `SettingsTab`
2. Initialize `self.settings_tab` first
3. Connect `tab_visibility_changed` signal
4. Create `self.tab_registry` dictionary
5. Store EPD tab info in registry
6. Add helper methods: `_on_tab_visibility_changed`, `_show_tab`, `_hide_tab`, `_get_tab_position`
7. Call `_apply_initial_tab_visibility()` after all tabs added
8. Add Settings tab at end

**Lines to Add:** ~80-100 lines of new code

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        MainWindow                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    QTabWidget                           │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │ │
│  │  │   EPD    │  │Connector │  │  Fault   │  │Settings│ │ │
│  │  │   Tab    │  │   Tab    │  │ Finding  │  │  Tab   │ │ │
│  │  │(dynamic) │  │(dynamic) │  │(dynamic) │  │(always)│ │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ▲                                 │
│                            │ tab_visibility_changed signal   │
│                            │                                 │
│  ┌────────────────────────┴────────────────────────────┐   │
│  │              Settings Tab                            │   │
│  │  ┌────────────────────────────────────────────┐     │   │
│  │  │ Tab Visibility Controls                    │     │   │
│  │  │  ☑ EPD Tools      ☑ Connectors            │     │   │
│  │  │  ☑ Fault Finding  ☑ Document Scanner      │     │   │
│  │  └────────────────────────────────────────────┘     │   │
│  │                   ▼                                  │   │
│  │        TabVisibilityConfig                           │   │
│  │        (saves to app_settings.json)                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Signal Flow

```
User clicks checkbox in Settings Tab
        ▼
SettingsTab._on_visibility_changed()
        ▼
TabVisibilityConfig.set_tab_visibility() → Save to config
        ▼
Emit: tab_visibility_changed(tab_name, visible)
        ▼
MainWindow._on_tab_visibility_changed()
        ▼
  ┌─────────────┬─────────────┐
  ▼             ▼             ▼
_show_tab()   _hide_tab()   
  │             │
  ▼             ▼
QTabWidget.insertTab()   QTabWidget.removeTab()
  │             │
  ▼             ▼
Tab appears   Tab disappears (instantly)
```

---

## Testing Plan

### Test Cases for EPD Tab

1. **Initial Load - All Visible (Default)**
   - [ ] Launch app fresh (no config)
   - [ ] Verify EPD tab is visible
   - [ ] Verify EPD tab is in correct position (first)

2. **Initial Load - EPD Hidden**
   - [ ] Manually edit config: `"epd": false`
   - [ ] Launch app
   - [ ] Verify EPD tab is NOT visible
   - [ ] Verify other tabs are visible

3. **Hide EPD Tab at Runtime**
   - [ ] Launch app with EPD visible
   - [ ] Go to Settings tab
   - [ ] Uncheck "EPD Tools"
   - [ ] Verify EPD tab disappears immediately
   - [ ] Verify tab order maintained

4. **Show EPD Tab at Runtime**
   - [ ] Start with EPD hidden
   - [ ] Go to Settings tab
   - [ ] Check "EPD Tools"
   - [ ] Verify EPD tab appears immediately
   - [ ] Verify EPD tab is in first position

5. **Persistence**
   - [ ] Hide EPD tab
   - [ ] Close application
   - [ ] Relaunch application
   - [ ] Verify EPD tab remains hidden

6. **Show All Preset**
   - [ ] Hide EPD tab
   - [ ] Click "Show All Tabs"
   - [ ] Verify EPD tab reappears
   - [ ] Verify success message shown

7. **Hide All Preset**
   - [ ] Click "Hide All Tabs"
   - [ ] Confirm dialog
   - [ ] Verify EPD tab disappears
   - [ ] Verify Settings tab remains visible

8. **Reset to Defaults**
   - [ ] Hide EPD tab
   - [ ] Click "Reset to Defaults"
   - [ ] Confirm dialog
   - [ ] Verify EPD tab reappears
   - [ ] Verify config updated

---

## Benefits

### User Benefits
- **Customizable Workspace** - Show only tabs you use
- **Reduced Clutter** - Hide unused features
- **Instant Changes** - No restart required
- **Easy Recovery** - Settings tab always accessible
- **Quick Presets** - Show/Hide all with one click

### Developer Benefits
- **Extensible Pattern** - Easy to add more tabs
- **Clean Architecture** - Signal-based communication
- **Centralized Config** - One place for visibility settings
- **Testable** - Clear test cases for each scenario
- **Maintainable** - Tab registry keeps track of all tabs

---

## Phase 2 Preview

After EPD tab is working, we'll add the remaining tabs:

**Tabs to Add:**
1. ✅ EPD (Phase 1)
2. ⏳ Connectors (Phase 2)
3. ⏳ Fault Finding (Phase 2)
4. ⏳ Document Scanner (Phase 2)
5. ⏳ Remote Docs (Phase 2)

**Process for Each Tab:**
1. Add entry to `tab_registry` in MainWindow
2. Apply initial visibility in `_apply_initial_tab_visibility()`
3. That's it! (The infrastructure is already built)

**Estimated Time per Additional Tab:** 5-10 minutes

---

## Configuration Example

**Before any changes (fresh install):**
```json
{}
```

**After hiding EPD tab:**
```json
{
  "tab_visibility": {
    "epd": false,
    "connectors": true,
    "fault_finding": true,
    "document_scanner": true,
    "remote_docs": true
  }
}
```

**After "Hide All":**
```json
{
  "tab_visibility": {
    "epd": false,
    "connectors": false,
    "fault_finding": false,
    "document_scanner": false,
    "remote_docs": false
  }
}
```

---

## Error Handling

### Edge Cases Covered

1. **Missing Config File** - Defaults to all visible
2. **Corrupted Config** - Defaults to all visible
3. **Unknown Tab Names** - Ignored gracefully
4. **Tab Already Visible/Hidden** - No-op, no error
5. **All Tabs Hidden** - Settings tab remains visible
6. **Rapid Toggle** - Signals handled sequentially

### User Protections

1. **Hide All Confirmation** - Warns user before hiding all tabs
2. **Reset Confirmation** - Warns before resetting to defaults
3. **Settings Always Visible** - Can't hide the Settings tab
4. **Clear Status Messages** - User knows what happened

---

## Next Steps

### To Implement EPD Tab Visibility:

1. **Edit `app/tabs/main_window.py`:**
   - [ ] Import `SettingsTab`
   - [ ] Initialize `self.settings_tab` first
   - [ ] Create `self.tab_registry` with EPD entry
   - [ ] Connect `tab_visibility_changed` signal
   - [ ] Add helper methods (`_show_tab`, `_hide_tab`, etc.)
   - [ ] Call `_apply_initial_tab_visibility()`
   - [ ] Add Settings tab at end

2. **Test EPD Tab:**
   - [ ] Run through all test cases
   - [ ] Verify persistence
   - [ ] Verify instant updates

3. **Move to Phase 2:**
   - [ ] Add remaining tabs to registry
   - [ ] Update `_apply_initial_tab_visibility()`
   - [ ] Test each tab independently

---

## Questions to Consider

1. **Should Settings tab be hideable?** 
   - Current: NO (always visible)
   - Reason: Users need access to re-enable tabs

2. **Should there be a warning before hiding the last tab?**
   - Current: NO (Settings tab always remains)
   - Could add: Warning if hiding last non-Settings tab

3. **Should tab order be preserved when showing/hiding?**
   - Current: YES (`_get_tab_position()` maintains order)
   - Users expect tabs in consistent positions

4. **Should there be keyboard shortcuts for tab visibility?**
   - Future enhancement: Ctrl+1-5 to toggle tabs
   - Not in current scope

---

## Summary

✅ **Settings Tab Complete** - Full UI with visibility controls  
⏳ **EPD Tab Integration** - Plan ready, implementation next  
📋 **Clear Testing Plan** - 8 test cases defined  
🚀 **Scalable Design** - Easy to add remaining tabs

The Settings tab is built and ready. Next step is to integrate EPD tab with the visibility system using the plan above.
