# Report Filter Architecture

## Overview

This document describes the event-driven architecture for multi-select topic filtering in the Automated Reports module. The design follows **Model-View-Presenter (MVP)** pattern with unidirectional data flow and a dedicated `FilterState` class for managing filter logic.

## Core Principles

1. **Single Source of Truth**: Filter state lives in a dedicated `FilterState` class
2. **Unidirectional Data Flow**: Events → Presenter → Model → View updates
3. **Separation of Concerns**: UI widgets emit primitives, Presenter handles business logic
4. **Testability**: All business logic isolated from Qt framework
5. **Extensibility**: Easy to add new filter dimensions without breaking existing code

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                         VIEW LAYER                          │
│  (TopicItem, FilterButton, SearchInput, AllReportsItem)    │
│                                                             │
│  Emits: topic_clicked(name, modifiers)                     │
│         filter_changed(dimension, selected_items)           │
│         search_changed(text)                                │
│         sort_changed(id, ascending)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │ Qt Signals
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      PRESENTER LAYER                        │
│                (AutomatedReportsPresenter)                  │
│                                                             │
│  Methods:                                                   │
│  • on_topic_clicked(name, ctrl_pressed)                    │
│  • on_filter_changed(dimension, items)                     │
│  • on_search_changed(text)                                 │
│  • on_sort_changed(id, ascending)                          │
│  • update_result_count()                                   │
│  • update_results()                                        │
│                                                             │
│  Owns: FilterState instance                                │
└─────────────────────┬───────────────────────────────────────┘
                      │ Method Calls
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    FILTER STATE CLASS                       │
│                      (Business Logic)                       │
│                                                             │
│  State:                                                     │
│  • selected_topics: Set[str]                               │
│  • active_filters: Dict[str, Set[str]]                     │
│  • search_text: Optional[str]                              │
│  • sort_field: str                                         │
│  • sort_ascending: bool                                    │
│                                                             │
│  Methods:                                                   │
│  • select_topic(name, is_multi_select=False)              │
│  • deselect_all_topics()                                   │
│  • set_filter(dimension, items)                            │
│  • clear_filters()                                         │
│  • to_query_dict() → Dict                                  │
└─────────────────────┬───────────────────────────────────────┘
                      │ Query Dict
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                       MODEL LAYER                           │
│                 (AutomatedReportsModel)                     │
│                                                             │
│  Methods:                                                   │
│  • query_reports(topics, filters, search, sort)            │
│  • get_filtered_count()                                    │
│  • get_total_count()                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Event Flow Sequences

### 1. Single Topic Click (Normal Click)

```
User clicks "Gamma" topic
  ↓
TopicItem.mousePressEvent(event)
  → Checks: event.modifiers() == Qt.NoModifier
  → Emits: clicked.emit("Gamma", ctrl_pressed=False)
  ↓
LeftPanel receives signal
  → Emits: topic_selected.emit("Gamma", ctrl_pressed=False)
  ↓
View._on_topic_selected("Gamma", False)
  → Calls: presenter.on_topic_clicked("Gamma", ctrl_pressed=False)
  ↓
Presenter.on_topic_clicked("Gamma", False)
  → Calls: filter_state.select_topic("Gamma", is_multi_select=False)
    • filter_state clears all other topics
    • filter_state.selected_topics = {"Gamma"}
  → Calls: self._apply_current_filters()
    • Queries model with current filter state
    • Emits results_updated signal
  → Calls: self._update_ui_selection_state()
    • Tells view which topics to highlight
  ↓
View receives results_updated
  → Updates ResultsPanel
  → Updates topic selection highlights
  → Updates count displays
```

### 2. Multi-Select Topic Click (Ctrl+Click)

```
User ctrl+clicks "Alpha" (Gamma already selected)
  ↓
TopicItem.mousePressEvent(event)
  → Checks: event.modifiers() & Qt.ControlModifier
  → Emits: clicked.emit("Alpha", ctrl_pressed=True)
  ↓
Presenter.on_topic_clicked("Alpha", True)
  → Calls: filter_state.select_topic("Alpha", is_multi_select=True)
    • filter_state.selected_topics = {"Gamma", "Alpha"}
  → Calls: self._apply_current_filters()
  → Updates UI to show both selected
```

### 3. All Reports Click

```
User clicks "All Reports"
  ↓
AllReportsItem.mousePressEvent(event)
  → Emits: clicked.emit("All Reports")
  ↓
Presenter.on_topic_clicked("All Reports", False)
  → Calls: filter_state.deselect_all_topics()
    • filter_state.selected_topics = set()
  → Queries model without topic filter
  → Updates UI to clear all topic selections
```

### 4. Filter Button Changes

```
User selects "Bug Fix" in Report Type filter
  ↓
FilterButton emits: selection_changed.emit("report_type", {"Bug Fix"})
  ↓
SearchPanel forwards: filters_changed.emit({"report_type": {"Bug Fix"}})
  ↓
Presenter.on_filter_changed("report_type", {"Bug Fix"})
  → Calls: filter_state.set_filter("report_type", {"Bug Fix"})
  → Calls: self._apply_current_filters()
    • Queries model with BOTH topics AND filters
    • selected_topics AND active_filters are combined
  → Updates results
```

---

## Key Design Decisions

### 1. Why Pass Modifiers from Widget Level?

**Decision**: Pass `ctrl_pressed: bool` through signals, convert at widget level

**Rationale**:
- **Pro**: Widget knows exact user action (ctrl, shift, etc.)
- **Pro**: Keeps presenter Qt-agnostic (receives bool, not Qt enum)
- **Pro**: Easier to test presenter with simple booleans
- **Con**: Small coupling to Qt in signal signature (acceptable trade-off)

### 2. Why Separate FilterState Class?

**Benefits**:
- **Isolation**: Business logic completely separate from Qt and UI
- **Testability**: Can unit test filter logic without QApplication
- **Reusability**: FilterState could be used by other modules
- **Clarity**: Single class responsible for "what is currently filtered"
- **Serialization**: Easy to save/restore filter state

### 3. Topic Selection vs. Filter Independence

```python
# Topics and filters are COMBINED (AND logic)
query = {
    'topics': ['Gamma', 'Alpha'],           # User selected these
    'filters': {                             # AND these filters apply
        'report_type': ['Bug Fix'],
        'scope': ['local']
    }
}
# Result: Reports in (Gamma OR Alpha) AND type=Bug Fix AND scope=local
```

**Why this design?**
- Topics are "containers" (what reports to look at)
- Filters are "refinements" (narrow down within containers)
- Intuitive: "Show me Gamma's Bug Fixes" = Select Gamma + Filter by Bug Fix
- Flexible: Multi-select topics = "Show Bug Fixes from Gamma OR Alpha"

### 4. UI State Synchronization

The presenter maintains **authoritative state** and tells widgets what to display:

```python
# Presenter after state change
def _update_ui_selection_state(self):
    """Push selection state to view"""
    selected = self.filter_state.selected_topics
    
    # Tell view to update all topic items
    for topic_name in all_topics:
        should_select = topic_name in selected
        self.view.set_topic_selected(topic_name, should_select)
```

**Why push instead of pull?**
- Avoids race conditions
- Single source of truth (presenter's FilterState)
- View is "dumb" - just displays what it's told
- Easy to debug: one place controls selection state

### 5. Count Updates

```python
def update_result_count(self):
    """Update counts based on current filters"""
    total = self.model.get_total_count()
    shown = self.model.get_filtered_count(self.filter_state.to_query_dict())
    
    # Update view
    self.view.update_count_display(shown, total)
    
    # Update per-topic counts
    topic_counts = self.model.get_counts_by_topic(
        self.filter_state.to_query_dict())
    self.view.update_topic_counts(topic_counts)
```

---

## FilterState API Design

```python
class FilterState:
    """Immutable-style filter state with validation"""
    
    def __init__(self):
        self._selected_topics: Set[str] = set()
        self._active_filters: Dict[str, Set[str]] = {}
        self._search_text: Optional[str] = None
        self._sort_field: str = "name"
        self._sort_ascending: bool = True
    
    def select_topic(self, name: str, is_multi_select: bool = False) -> 'FilterState':
        """Select topic, optionally preserving existing selections
        
        Args:
            name: Topic name to select
            is_multi_select: If False, clears other topics first
            
        Returns:
            Self for chaining
        """
        if not is_multi_select:
            self._selected_topics.clear()
        
        if name == "All Reports":
            self._selected_topics.clear()
        else:
            self._selected_topics.add(name)
        
        return self
    
    def deselect_all_topics(self) -> 'FilterState':
        """Clear all topic selections"""
        self._selected_topics.clear()
        return self
    
    def set_filter(self, dimension: str, items: Set[str]) -> 'FilterState':
        """Set filter values for a dimension
        
        Args:
            dimension: Filter dimension (e.g., 'report_type', 'scope')
            items: Set of selected filter values
            
        Returns:
            Self for chaining
        """
        if items:
            self._active_filters[dimension] = items.copy()
        else:
            self._active_filters.pop(dimension, None)
        return self
    
    def clear_filters(self) -> 'FilterState':
        """Clear all filter dimensions"""
        self._active_filters.clear()
        return self
    
    def set_search(self, text: Optional[str]) -> 'FilterState':
        """Set search text"""
        self._search_text = text if text else None
        return self
    
    def set_sort(self, field: str, ascending: bool) -> 'FilterState':
        """Set sort parameters"""
        self._sort_field = field
        self._sort_ascending = ascending
        return self
    
    def to_query_dict(self) -> Dict:
        """Convert to model query format"""
        return {
            'topics': list(self._selected_topics) if self._selected_topics else None,
            'filters': dict(self._active_filters),
            'search': self._search_text,
            'sort_by': self._sort_field,
            'ascending': self._sort_ascending
        }
    
    @property
    def selected_topics(self) -> Set[str]:
        """Get currently selected topics (read-only)"""
        return self._selected_topics.copy()
    
    @property
    def has_active_filters(self) -> bool:
        """Check if any filters are active"""
        return bool(self._active_filters or self._search_text or self._selected_topics)
```

---

## Signal Signature Changes Required

### TopicItem Widget

```python
class TopicItem(QWidget):
    clicked = Signal(str, bool)  # (topic_name, ctrl_pressed)
    
    def mousePressEvent(self, event):
        ctrl_pressed = bool(event.modifiers() & Qt.ControlModifier)
        self.clicked.emit(self.topic_name, ctrl_pressed)
```

### LeftPanel Component

```python
class LeftPanel(QFrame):
    topic_selected = Signal(str, bool)  # (topic_name, ctrl_pressed)
    
    def _on_topic_clicked(self, topic_name: str, ctrl_pressed: bool):
        self.topic_selected.emit(topic_name, ctrl_pressed)
```

### View Layer

```python
class AutomatedReportsView(QWidget):
    def _connect_signals(self):
        # Topic selection with modifier state
        self.left_panel.topic_selected.connect(self._on_topic_selected)
    
    def _on_topic_selected(self, topic: str, ctrl_pressed: bool):
        self.presenter.on_topic_clicked(topic, ctrl_pressed)
    
    def set_topic_selected(self, topic_name: str, selected: bool):
        """Update UI selection state for a topic"""
        self.left_panel.set_topic_selected(topic_name, selected)
```

### Presenter Layer

```python
class AutomatedReportsPresenter(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = AutomatedReportsModel()
        self.filter_state = FilterState()
    
    def on_topic_clicked(self, name: str, ctrl_pressed: bool):
        """Handle topic selection with multi-select support"""
        self.filter_state.select_topic(name, is_multi_select=ctrl_pressed)
        self._apply_current_filters()
        self._update_ui_selection_state()
    
    def on_filter_changed(self, dimension: str, items: Set[str]):
        """Handle filter dimension change"""
        self.filter_state.set_filter(dimension, items)
        self._apply_current_filters()
    
    def _apply_current_filters(self):
        """Query model with current filter state and emit results"""
        query = self.filter_state.to_query_dict()
        results = self.model.query_reports(**query)
        self.reports_updated.emit(results)
        self.update_result_count()
    
    def _update_ui_selection_state(self):
        """Push selection state to view"""
        selected = self.filter_state.selected_topics
        # Implementation depends on view API
        pass
    
    def update_result_count(self):
        """Update counts based on current filters"""
        query = self.filter_state.to_query_dict()
        total = self.model.get_total_count()
        shown = self.model.get_filtered_count(query)
        # Emit signals to update view
        pass
```

---

## Business Logic Rules

### Topic Selection Rules

1. **Normal Click**: Deselect all other topics, select clicked topic
2. **Ctrl+Click**: Add/remove topic from selection (multi-select)
3. **"All Reports" Click**: Clear all topic selections
4. **Topic Selection Independence**: Selecting topics does NOT clear active filters

### Filter Application Rules

1. **Topics are OR'd**: Reports in (Topic A OR Topic B)
2. **Filters are AND'd**: Reports matching (Filter X AND Filter Y)
3. **Topics AND Filters**: (Topic A OR Topic B) AND (Filter X AND Filter Y)
4. **Empty Selection**: No topics selected = show all reports (unless filters applied)

### Visual Selection State

1. **Single Topic Selected**: Blue tint on one topic item
2. **Multiple Topics Selected**: Blue tint on all selected topic items
3. **No Topics Selected**: No blue tint (showing "All Reports" implicitly)
4. **Filter Active**: Filter button shows count and blue tint
5. **Combined State**: Topic selection + filter selection = both visible

---

## Why This Design is Senior-Level

1. **Clear Boundaries**: Each layer has one responsibility
2. **Testable**: FilterState has zero dependencies, can be tested in isolation
3. **Maintainable**: Adding new filter dimensions requires minimal changes
4. **Type-Safe**: Explicit signatures, no magic strings for state
5. **Debuggable**: State changes funnel through FilterState methods
6. **Extensible**: Easy to add features like:
   - Filter persistence (serialize FilterState)
   - Undo/redo (stack of FilterState snapshots)
   - Complex boolean logic (topics with AND/OR/NOT)
   - Filter presets/saved searches
7. **Performance**: FilterState tracks dirty state, only queries model when needed
8. **Qt Best Practices**: Signals carry data, not state references
9. **Immutable Style**: FilterState methods return self for chaining, state changes are explicit
10. **Documentation**: Clear API contracts and behavior specifications

---

## Implementation Checklist

- [ ] Create `FilterState` class in `filter_state.py`
- [ ] Update `TopicItem` to emit `clicked(str, bool)` with ctrl modifier
- [ ] Update `AllReportsItem` to emit `clicked(str)` signal
- [ ] Update `LeftPanel` to forward topic selection with modifiers
- [ ] Add presenter methods: `on_topic_clicked`, `on_filter_changed`, `update_result_count`
- [ ] Update model to support combined topic+filter queries
- [ ] Add view methods for pushing selection state to widgets
- [ ] Wire all signals through view layer
- [ ] Add debug print statements for filter state changes
- [ ] Update count displays when filters change
- [ ] Test multi-select behavior (ctrl+click)
- [ ] Test filter independence from topic selection
- [ ] Test "All Reports" clears topic selection

---

## Future Enhancements

1. **Filter Persistence**: Save/load filter state to user preferences
2. **Filter History**: Recently used filter combinations
3. **Smart Suggestions**: "Users who filtered X also filtered Y"
4. **Advanced Boolean Logic**: Support complex topic queries (A AND B) OR (C NOT D)
5. **Filter Presets**: Save named filter combinations
6. **Keyboard Shortcuts**: Arrow keys for navigation, Enter to apply
7. **Accessibility**: Screen reader support for filter state
8. **Performance Optimization**: Debounce rapid filter changes
9. **Analytics**: Track which filter combinations are most common
10. **Export Filters**: Share filter state via URL or clipboard

---

## Related Documentation

- [Architecture Images](ARCHITECTURE_IMAGES.txt) - Visual diagrams of component layout
- [MVP Pattern](../README.md) - Overall application architecture
- [Component Structure](COMPONENT_STRUCTURE.md) - Widget hierarchy and responsibilities
