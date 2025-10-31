# Context Callbacks API Guide

**Interactive Context System for Document Search**

This guide explains how to create **interactive, collapsible Context objects** with clickable action buttons for the Document Scanner Search feature.

---

## 📋 Overview

The Context system allows modules (Connector, EPD, etc.) to provide **additional context** when search results are selected. Contexts can include:

- ✅ **Data fields** (key-value pairs displayed cleanly)
- ✅ **Action buttons** (hyperlink-style buttons that trigger callbacks)
- ✅ **Collapsible sections** (minimize clutter with expandable/collapsible UI)

Each context appears as a **collapsible card** with a colored header showing the module name and matched term.

---

## 🏗️ Core Classes

### `ContextCallback`

Represents a single clickable action in a context.

```python
@dataclass
class ContextCallback:
    label: str              # Button text (e.g., "Open Connector", "View EPD")
    callback: Callable      # Function to call when clicked
    tooltip: Optional[str]  # Optional tooltip text
```

### `Context`

Represents contextual information with data and interactive actions.

```python
@dataclass
class Context:
    term: str                              # Term that triggered this context
    context_owner: str                     # Source module name
    data_context: Dict[str, str]           # Key-value data fields
    callbacks: List[ContextCallback]       # Interactive actions
```

**Methods:**
- `add_callback(label, callback, tooltip=None)` - Add an action button
- `add_data(key, value)` - Add a data field
- `has_callbacks() -> bool` - Check if has actions
- `has_data() -> bool` - Check if has data

---

## 🎨 Visual Design

Contexts are displayed as **minimalist collapsible cards**:

```
┌─────────────────────────────────────────────────────┐
│ Matched Data                                        │
│ ─────────────────────────────────────────────────── │
│ Part Number:  D38999-26WA35PN                       │
│ Location:     Drawing A-123, Page 5                 │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ ▼ Connector • 'D38999-26WA35PN'        [Blue Header]│ ← Clickable
├─────────────────────────────────────────────────────┤
│ Part Number: D38999/26WA35PN                        │
│ Material:    Aluminum                               │
│ Shell Type:  26 - Plug                              │
│ Status:      Active                                 │
│                                                     │
│ Open in Lookup  Find Alternatives  Find Opposite    │ ← Hyperlinks
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ ▶ EPD • 'EPD-001'                      [Blue Header]│ ← Collapsed
└─────────────────────────────────────────────────────┘
```

**Design Features:**
- ✅ Minimal padding (5px margins, 3px spacing)
- ✅ Blue gradient headers with white text
- ✅ Hyperlink-style buttons (underlined, blue text)
- ✅ Collapsible sections (click header to expand/collapse)
- ✅ Arrow indicators (▼ expanded, ▶ collapsed)

---

## 📝 Usage Patterns

### Pattern 1: Build Context Incrementally

```python
from app.document_scanner.search_result import Context

# Create empty context
context = Context(
    term="D38999-26WA35PN",
    context_owner="Connector"
)

# Add data fields
context.add_data("Part Number", "D38999/26WA35PN")
context.add_data("Material", "Aluminum")
context.add_data("Shell Size", "10")
context.add_data("Status", "Active")

# Add action callbacks
context.add_callback(
    label="Open in Lookup",
    callback=lambda: self._open_in_lookup("D38999-26WA35PN"),
    tooltip="Jump to Connector tab and search for this part"
)

context.add_callback(
    label="Find Alternatives",
    callback=lambda: self._find_alternatives("D38999-26WA35PN"),
    tooltip="Search for alternative connectors"
)

context.add_callback(
    label="Find Opposite",
    callback=lambda: self._find_opposite("D38999-26WA35PN"),
    tooltip="Find mating connector (plug ↔ receptacle)"
)

return [context]
```

### Pattern 2: Create Context with All Data Upfront

```python
context = Context(
    term="D38999-26WA35PN",
    context_owner="Connector",
    data_context={
        "Part Number": "D38999/26WA35PN",
        "Material": "Aluminum",
        "Shell Size": "10",
        "Status": "Active"
    },
    callbacks=[
        ContextCallback(
            label="Open in Lookup",
            callback=lambda: self._open_in_lookup("D38999-26WA35PN"),
            tooltip="Jump to Connector tab and search for this part"
        ),
        ContextCallback(
            label="Find Alternatives",
            callback=lambda: self._find_alternatives("D38999-26WA35PN"),
            tooltip="Search for alternative connectors"
        )
    ]
)
```

---

## 💡 Complete Examples

### Example 1: Connector Context Provider

```python
# In app/connector/connector_context_provider.py

from app.document_scanner.context_provider import ContextProvider
from app.document_scanner.search_result import Context, SearchResult
from typing import List


class ConnectorContextProvider(ContextProvider):
    """Provides context for connector-related search results"""
    
    def __init__(self, connector_tab, main_window):
        self.connector_tab = connector_tab
        self.main_window = main_window
    
    def get_context_name(self) -> str:
        return "Connector"
    
    def is_enabled(self) -> bool:
        return True
    
    def get_context(self, search_result: SearchResult) -> List[Context]:
        """Search for connector matches and create contexts"""
        contexts = []
        
        # Search for connector part numbers in the result data
        for key, value in search_result.matched_row_data.items():
            if self._looks_like_part_number(value):
                connector_data = self._search_connector_db(value)
                
                if connector_data:
                    # Create context
                    ctx = Context(
                        term=str(value),
                        context_owner="Connector"
                    )
                    
                    # Add connector data (minimal, relevant fields only)
                    ctx.add_data("Part Number", connector_data['Part Number'])
                    ctx.add_data("Material", connector_data['Material'])
                    ctx.add_data("Shell Type", connector_data['Shell Type'])
                    
                    # Add interactive actions
                    ctx.add_callback(
                        label="Open in Lookup",
                        callback=lambda pn=value: self._open_in_lookup(pn),
                        tooltip="Jump to Connector tab and search for this part"
                    )
                    
                    ctx.add_callback(
                        label="Find Alternatives",
                        callback=lambda pn=value: self._find_alternatives(pn),
                        tooltip="Search for alternative connectors"
                    )
                    
                    ctx.add_callback(
                        label="Find Opposite",
                        callback=lambda pn=value: self._find_opposite(pn),
                        tooltip="Find mating connector (plug ↔ receptacle)"
                    )
                    
                    contexts.append(ctx)
        
        return contexts
    
    def _looks_like_part_number(self, value: str) -> bool:
        """Check if value looks like a connector part number"""
        value_str = str(value).upper()
        # D38999, MS27467, etc.
        return value_str.startswith(('D38999', 'MS27467', 'M83723'))
    
    def _search_connector_db(self, part_number: str) -> dict:
        """Search connector database for matching part"""
        # Query connector model
        model = self.connector_tab.model
        # ... implementation ...
        return None  # or dict with data
    
    def _open_in_lookup(self, part_number: str):
        """Switch to Connector tab and search for part number"""
        # Switch to Connector tab
        self.main_window.tab_widget.setCurrentWidget(self.connector_tab)
        
        # Switch to Lookup sub-tab
        self.connector_tab.switch_to_subtab("Lookup")
        
        # Trigger search
        lookup_view = self.connector_tab.lookup_presenter.view
        lookup_view.search_input.setText(part_number)
        lookup_view._on_search_clicked()
    
    def _find_alternatives(self, part_number: str):
        """Find alternative connectors"""
        self.main_window.tab_widget.setCurrentWidget(self.connector_tab)
        self.connector_tab.switch_to_subtab("Lookup")
        self.connector_tab.lookup_presenter.on_find_alternative_requested(part_number)
    
    def _find_opposite(self, part_number: str):
        """Find opposite (mating) connector"""
        self.main_window.tab_widget.setCurrentWidget(self.connector_tab)
        self.connector_tab.switch_to_subtab("Lookup")
        self.connector_tab.lookup_presenter.on_find_opposite_requested(part_number)
```

### Example 2: EPD Context Provider

```python
# In app/epd/epd_context_provider.py

class EpdContextProvider(ContextProvider):
    """Provides context for EPD-related search results"""
    
    def __init__(self, epd_tab, main_window):
        self.epd_tab = epd_tab
        self.main_window = main_window
    
    def get_context_name(self) -> str:
        return "EPD"
    
    def is_enabled(self) -> bool:
        return True
    
    def get_context(self, search_result: SearchResult) -> List[Context]:
        """Search for EPD matches and create contexts"""
        contexts = []
        
        # Search for EPD IDs in the result data
        for key, value in search_result.matched_row_data.items():
            if self._looks_like_epd_id(value):
                epd_record = self._search_epd_db(value)
                
                if epd_record:
                    ctx = Context(
                        term=str(value),
                        context_owner="EPD"
                    )
                    
                    # Add minimal EPD data
                    ctx.add_data("EPD ID", epd_record['EPD'])
                    ctx.add_data("Cable Type", epd_record['Cable'])
                    ctx.add_data("Rating", f"{epd_record['Rating (A)']}A")
                    ctx.add_data("Pins", str(epd_record['Pins']))
                    
                    # Add interactive actions
                    ctx.add_callback(
                        label="View EPD Details",
                        callback=lambda epd_id=value: self._view_epd_details(epd_id),
                        tooltip="Open full EPD record in EPD tab"
                    )
                    
                    ctx.add_callback(
                        label="Identify Best EPD",
                        callback=lambda epd_id=value: self._identify_best_epd(epd_id),
                        tooltip="Find best EPD for specifications"
                    )
                    
                    contexts.append(ctx)
        
        return contexts
    
    def _view_epd_details(self, epd_id: str):
        """Switch to EPD tab and show details"""
        self.main_window.tab_widget.setCurrentWidget(self.epd_tab)
        self.epd_tab.switch_to_subtab("Search EPD")
        self.epd_tab.search_presenter.view.search_input.setText(epd_id)
        self.epd_tab.search_presenter.view._emit_search()
    
    def _identify_best_epd(self, epd_id: str):
        """Jump to Identify Best EPD tab"""
        self.main_window.tab_widget.setCurrentWidget(self.epd_tab)
        self.epd_tab.switch_to_subtab("Identify Best EPD")
        # Could pre-populate filters based on EPD
```

---

## ⚙️ Integration

### Registering Context Providers

Context providers must be registered with the Search presenter:

```python
# In document_scanner_tab.py or main.py initialization

# Create context providers with references to tabs and main window
connector_context_provider = ConnectorContextProvider(
    connector_tab=connector_tab,
    main_window=main_window
)

epd_context_provider = EpdContextProvider(
    epd_tab=epd_tab,
    main_window=main_window
)

# Register with Search presenter
search_presenter.register_context_provider(connector_context_provider)
search_presenter.register_context_provider(epd_context_provider)
```

### Context Provider Interface

All context providers must implement:

```python
from abc import ABC, abstractmethod

class ContextProvider(ABC):
    @abstractmethod
    def get_context_name(self) -> str:
        """Return name of this context provider"""
        pass
    
    @abstractmethod
    def is_enabled(self) -> bool:
        """Return True if this provider is active"""
        pass
    
    @abstractmethod
    def get_context(self, search_result: SearchResult) -> List[Context]:
        """Return list of Context objects for this search result"""
        pass
```

---

## ✅ Best Practices

### 1. **Minimal Data Display**

Only show the most relevant fields. Users can click buttons for more details.

```python
# ✅ Good - essential info only
ctx.add_data("Part Number", "D38999/26WA35PN")
ctx.add_data("Material", "Aluminum")
ctx.add_data("Status", "Active")

# ❌ Bad - too much clutter
ctx.add_data("Database ID", "12345")
ctx.add_data("Last Modified", "2024-01-01 12:34:56")
ctx.add_data("Internal Code", "XYZ123")
ctx.add_data("Created By", "John Doe")
```

### 2. **Concise Button Labels**

Keep button text short and action-oriented.

```python
# ✅ Good
ctx.add_callback("Open in Lookup", ...)
ctx.add_callback("Find Alternatives", ...)
ctx.add_callback("View Details", ...)

# ❌ Bad
ctx.add_callback("Click here to open this connector in the Lookup tab", ...)
ctx.add_callback("Search", ...)  # Too vague
```

### 3. **Use Tooltips for Clarity**

Always provide tooltips explaining what the action does.

```python
ctx.add_callback(
    label="Open in Lookup",
    callback=lambda: open_connector(),
    tooltip="Jump to Connector tab and search for this part number"  # ✅
)
```

### 4. **Capture Variables in Lambda**

When using lambdas in loops, capture the variable value.

```python
# ✅ Correct - capture value
for part_number in part_numbers:
    ctx.add_callback(
        label=f"Open {part_number}",
        callback=lambda pn=part_number: open_connector(pn),  # Capture!
        tooltip=f"Open {part_number}"
    )

# ❌ Wrong - all callbacks use last value
for part_number in part_numbers:
    ctx.add_callback(
        label=f"Open {part_number}",
        callback=lambda: open_connector(part_number),  # Bug!
        tooltip=f"Open {part_number}"
    )
```

### 5. **Limit Number of Actions**

Aim for **2-4 callback buttons** per context. More than that clutters the UI.

```python
# ✅ Good - 3 focused actions
ctx.add_callback("Open in Lookup", ...)
ctx.add_callback("Find Alternatives", ...)
ctx.add_callback("Find Opposite", ...)

# ❌ Bad - too many options
ctx.add_callback("Open", ...)
ctx.add_callback("Edit", ...)
ctx.add_callback("Copy", ...)
ctx.add_callback("Export", ...)
ctx.add_callback("Download", ...)
ctx.add_callback("Share", ...)
```

### 6. **Handle Errors in Callbacks**

Always wrap callback logic in try-except to prevent crashes.

```python
def _open_in_lookup(self, part_number: str):
    try:
        self.main_window.tab_widget.setCurrentWidget(self.connector_tab)
        self.connector_tab.switch_to_subtab("Lookup")
        # ... rest of logic
    except Exception as e:
        print(f"Error opening connector: {e}")
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.warning(
            None,
            "Error",
            f"Could not open connector: {e}"
        )
```

### 7. **Test Context Collapsing**

Ensure contexts can be collapsed/expanded smoothly.

- Click header to collapse
- Arrow indicator updates (▼ → ▶)
- Content animates smoothly

---

## 🎯 Quick Reference

### Create Minimal Context

```python
context = Context(term="value", context_owner="Module")
context.add_data("Key", "Value")
context.add_callback("Action", callback_fn, "Tooltip")
return [context]
```

### Create Full Context

```python
context = Context(
    term="D38999-26WA35PN",
    context_owner="Connector",
    data_context={"Part": "D38999/26WA35PN", "Material": "Aluminum"},
    callbacks=[
        ContextCallback("Open", open_fn, "Open in Connector tab")
    ]
)
return [context]
```

---

## 🔧 Implementation Files

- **Data Classes**: `app/document_scanner/search_result.py`
- **View Rendering**: `app/document_scanner/Search/view.py`
- **Presenter Logic**: `app/document_scanner/Search/presenter.py`
- **Provider Interface**: `app/document_scanner/context_provider.py`

---

*Last Updated: October 19, 2025*
*Interactive, collapsible context system with hyperlink-style action buttons*
