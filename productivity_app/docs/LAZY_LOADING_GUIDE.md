# Lazy Loading Implementation Guide

## Overview

The lazy loading system improves application startup time by loading tabs progressively in the background. This creates a responsive UI that appears almost instantly, with tabs appearing one-by-one as they finish loading.

**Key Benefits:**
- ✅ **Instant startup** - Window appears in milliseconds
- ✅ **Progressive loading** - Tabs load in priority order
- ✅ **Non-blocking** - UI remains responsive during loading
- ✅ **Smart dependencies** - Handles tab interdependencies automatically
- ✅ **Configurable delays** - Control loading sequence and timing
- ✅ **Error resilient** - Failed tabs don't block others

---

## How It Works

### Loading Sequence

```
App Start
    ↓
MainWindow created (instant)
    ↓
Settings tab added (lightweight, always first)
    ↓
Window shown to user ← USER SEES APP HERE (< 100ms)
    ↓
+50ms  → Load Connectors tab
    ↓
+100ms → Load EPD tab
    ↓
+200ms → Load Document Scanner tab
    ↓
+300ms → Load Fault Finding tab (depends on EPD)
    ↓
+400ms → Load Remote Docs tab
    ↓
All tabs loaded → Register context providers
```

### Current Loading Order

Tabs are loaded in order of typical usage frequency:

1. **Connectors** (50ms) - Most frequently used
2. **EPD** (100ms) - Frequently used, required by Fault Finding
3. **Document Scanner** (200ms) - Moderately used
4. **Fault Finding** (300ms) - Depends on EPD model
5. **Remote Docs** (400ms) - Less frequently used

---

## Architecture

### Key Components

#### 1. **MainWindow.__init__**
```python
def __init__(self, context):
    # Create window shell immediately
    super().__init__()
    self.setWindowTitle("Engineering Toolkit")
    self.resize(1200, 800)
    
    # Add Settings tab first (lightweight)
    self.settings_tab = SettingsTab()
    
    # Start lazy loading
    self._start_lazy_loading()
```

#### 2. **Tab Loading Queue**
```python
self._pending_tabs = [
    ('tab_name', self._load_func, delay_ms),
    # ...
]
```

#### 3. **QTimer-based Scheduling**
Uses Qt's `QTimer.singleShot()` to schedule tab loads without blocking the UI thread.

---

## How to Add a New Tab with Lazy Loading

### Step 1: Create the Loading Function

Add a new loading method in `MainWindow`:

```python
def _load_my_new_tab(self):
    """Load My New Tab"""
    self.my_new_tab = MyNewPresenter(self.context)
    self.tab_registry['my_new_tab'] = {
        'presenter': self.my_new_tab,
        'view': self.my_new_tab.view,
        'title': self.my_new_tab.title
    }
    
    # Add tab if it should be visible
    if self.settings_tab.is_tab_visible('my_new_tab'):
        position = self._get_tab_position('my_new_tab')
        self.tabs.insertTab(position, self.my_new_tab.view, self.my_new_tab.title)
```

### Step 2: Add to Loading Queue

Edit `_start_lazy_loading()` and add your tab to the queue:

```python
def _start_lazy_loading(self):
    self._pending_tabs = [
        ('connectors', self._load_connectors_tab, 50),
        ('epd', self._load_epd_tab, 100),
        ('my_new_tab', self._load_my_new_tab, 150),  # Add here
        # ... rest of tabs
    ]
    self._schedule_next_tab()
```

### Step 3: Update Tab Order (if needed)

If your tab has specific ordering requirements, update `_get_tab_position()`:

```python
tab_order = [
    'epd', 
    'connectors', 
    'my_new_tab',      # Add to desired position
    'fault_finding',
    'document_scanner', 
    'remote_docs'
]
```

**That's it!** Your tab will now load lazily.

---

## Handling Dependencies

### Example: Fault Finding depends on EPD

```python
def _load_fault_finding_tab(self):
    """Load the Fault Finding tab (requires EPD to be loaded first)"""
    # Ensure EPD is loaded
    if not hasattr(self, 'epd'):
        print("[MainWindow] Warning: EPD not loaded yet, loading now...")
        self._load_epd_tab()
    
    # Now safe to use self.epd.model
    self.fault_finding = FaultFindingPresenter(self.context, self.epd.model)
    # ... rest of loading
```

### Best Practices for Dependencies

1. **Check with `hasattr()`**: Always check if dependency exists
2. **Load synchronously**: Call the dependency's load function directly
3. **Schedule order**: Place dependent tabs after their dependencies
4. **Document**: Add comments explaining the dependency

---

## Optimizing Load Times

### 1. **Adjust Delays**

Shorter delays = faster perceived loading (but more CPU load)
Longer delays = smoother, more staggered loading

```python
# Fast loading (aggressive)
('connectors', self._load_connectors_tab, 20),   # Very quick
('epd', self._load_epd_tab, 40),

# Smooth loading (conservative)
('connectors', self._load_connectors_tab, 100),  # More spacing
('epd', self._load_epd_tab, 300),

# Current (balanced)
('connectors', self._load_connectors_tab, 50),   # Good balance
('epd', self._load_epd_tab, 100),
```

### 2. **Optimize Presenter Initialization**

**Before (slow):**
```python
class MyPresenter:
    def __init__(self, context):
        # Loads everything immediately
        self.data = self._load_large_dataset()
        self.view = MyView()
        self.view.populate(self.data)
```

**After (fast):**
```python
class MyPresenter:
    def __init__(self, context):
        # Create view only
        self.view = MyView()
        
        # Defer data loading
        QTimer.singleShot(0, self._load_data_async)
    
    def _load_data_async(self):
        # Load data in background
        self.data = self._load_large_dataset()
        self.view.populate(self.data)
```

### 3. **Reorder by Priority**

Place most-used tabs first:
- Frequently accessed → Short delay (50-100ms)
- Moderate use → Medium delay (200-300ms)
- Rarely used → Long delay (400-500ms)

---

## Monitoring and Debugging

### Enable Detailed Logging

The system already includes logging:

```
[MainWindow] Initializing Settings tab...
[MainWindow] Window ready, starting lazy tab loading...
[MainWindow] Loading connectors tab...
[MainWindow] ✓ connectors tab loaded
[MainWindow] Loading epd tab...
[MainWindow] ✓ epd tab loaded
...
[MainWindow] ✓ All tabs loaded successfully
[MainWindow] ✓ Context providers registered
```

### Measure Load Times

Add timing code:

```python
import time

def _load_tab(self, tab_name: str, load_func):
    print(f"[MainWindow] Loading {tab_name} tab...")
    start_time = time.time()
    
    try:
        load_func()
        elapsed = (time.time() - start_time) * 1000
        print(f"[MainWindow] ✓ {tab_name} tab loaded in {elapsed:.0f}ms")
    except Exception as e:
        print(f"[MainWindow] ✗ Error loading {tab_name} tab: {e}")
    
    self._schedule_next_tab()
```

### Common Issues

**Problem:** Tab doesn't appear
- **Check:** Is `is_tab_visible()` returning True?
- **Check:** Is tab in `tab_order` list?
- **Fix:** Verify Settings tab visibility settings

**Problem:** Tabs load too slowly
- **Check:** Delays in `_pending_tabs`
- **Fix:** Reduce delay values (but watch CPU usage)

**Problem:** Dependency errors
- **Check:** Load order in `_pending_tabs`
- **Fix:** Place dependent tabs after dependencies
- **Fix:** Add explicit dependency check (see Fault Finding example)

**Problem:** Loading freezes
- **Check:** Console for exception messages
- **Check:** Presenter `__init__` for blocking operations
- **Fix:** Move heavy operations to async methods

---

## Advanced: Priority-Based Loading

Load tabs based on user behavior:

```python
def _start_lazy_loading(self):
    # Get last active tab from settings
    last_active = AppSettingsConfig.get_setting('last_active_tab', 'connectors')
    
    # Build priority queue
    priority_tabs = [last_active]  # Load last used first
    other_tabs = [t for t in ['epd', 'connectors', ...] if t != last_active]
    
    self._pending_tabs = []
    delay = 50
    
    # Add priority tabs first
    for tab in priority_tabs:
        self._pending_tabs.append((tab, self._get_load_func(tab), delay))
        delay += 50
    
    # Add remaining tabs
    for tab in other_tabs:
        self._pending_tabs.append((tab, self._get_load_func(tab), delay))
        delay += 100
    
    self._schedule_next_tab()
```

---

## Advanced: On-Demand Loading

Load tabs only when user clicks on them:

```python
def __init__(self, context):
    # ... setup code ...
    
    # Connect to tab change signal
    self.tabs.currentChanged.connect(self._on_tab_changed)
    
    # Track loaded tabs
    self._loaded_tabs = set(['settings'])

def _on_tab_changed(self, index):
    """Load tab on-demand when user switches to it"""
    widget = self.tabs.widget(index)
    
    # Check if this tab needs loading
    for tab_name, tab_info in self.tab_registry.items():
        if tab_info.get('view') == widget and tab_name not in self._loaded_tabs:
            print(f"[MainWindow] Loading {tab_name} on-demand...")
            self._load_tab_by_name(tab_name)
            self._loaded_tabs.add(tab_name)
            break
```

---

## Performance Metrics

### Typical Load Times

Based on current implementation:

| Phase | Time | Action |
|-------|------|--------|
| App start | 0ms | Python interpreter starts |
| Window created | 50-100ms | MainWindow `__init__` completes |
| Settings visible | 100ms | User sees application |
| First tab loaded | 150ms | Connectors appears |
| All tabs loaded | 500-600ms | Complete loading |

### Target Times

- **Time to window**: < 200ms
- **Time to first tab**: < 300ms
- **Time to all tabs**: < 1000ms

### Measuring Startup

```python
# In main.py
import time
start = time.time()

app = QApplication(sys.argv)
window = MainWindow(context)
window.show()

print(f"Window shown in {(time.time() - start) * 1000:.0f}ms")
```

---

## Best Practices

### 1. **Load Order**
- Settings first (always)
- Most-used tabs early
- Dependent tabs after dependencies
- Resource-heavy tabs last

### 2. **Delay Spacing**
- Use 50-100ms gaps for smooth loading
- Don't make delays too short (CPU spikes)
- Don't make delays too long (feels slow)

### 3. **Error Handling**
- Always wrap load functions in try/except
- Failed tabs shouldn't block others
- Log errors clearly

### 4. **Testing**
Test on slower systems to verify:
- Window appears quickly
- Tabs load smoothly
- No freezing or stuttering
- All tabs eventually load

### 5. **User Experience**
- Show Settings tab immediately (always works)
- Let users start working before all tabs load
- Provide visual feedback if desired (loading indicators)

---

## Migration Checklist

Converting from synchronous to lazy loading:

- [ ] Identify all tabs currently loaded in `__init__`
- [ ] Create `_load_*_tab()` method for each
- [ ] Add to `_pending_tabs` queue with appropriate delay
- [ ] Update `tab_order` list if needed
- [ ] Handle dependencies (check with `hasattr()`)
- [ ] Test on slow system
- [ ] Verify tab visibility settings still work
- [ ] Check context providers load after dependencies
- [ ] Measure and optimize load times

---

## Troubleshooting

### Tab appears blank/empty

**Cause:** View created but not initialized
**Fix:** Ensure presenter initialization is complete

```python
def _load_my_tab(self):
    self.my_tab = MyPresenter(self.context)
    # Make sure presenter fully initializes view
    self.my_tab.initialize()  # If needed
```

### Tabs load in wrong order

**Cause:** Tab order list doesn't match loading order
**Fix:** Update both `_pending_tabs` and `tab_order`

### Feature flags don't work on lazy tabs

**Cause:** Presenter not loaded when flag changes
**Fix:** Add `hasattr()` check in flag handler (already implemented)

### Context providers fail

**Cause:** Loaded before dependencies
**Fix:** Move to `_on_loading_complete()`

---

## Future Enhancements

### Possible Improvements

1. **Loading progress indicator**
   - Show progress bar in status bar
   - Display "Loading X of 5 tabs..."

2. **Adaptive loading**
   - Learn user patterns
   - Prioritize frequently-used tabs

3. **Parallel loading**
   - Load independent tabs concurrently
   - Respect dependencies

4. **Deferred initialization**
   - Load presenter structure
   - Defer data loading until tab activated

5. **Splash screen**
   - Show branded splash during initial load
   - Display loading status

---

## Related Documentation

- [MainWindow Architecture](./MAIN_WINDOW_ARCHITECTURE.md)
- [Tab Visibility System](./TAB_VISIBILITY_GUIDE.md)
- [Performance Optimization](./PERFORMANCE_GUIDE.md)

---

**Last Updated:** October 20, 2025
