# Tab & Sub-Tab Architecture Guide

**Last Updated:** October 20, 2025  
**Purpose:** Guide for adding new tabs and sub-tabs to the Engineering Toolkit application

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Tab Types & When to Use](#tab-types--when-to-use)
3. [Component Patterns](#component-patterns)
4. [Step-by-Step: Adding a Simple Tab](#step-by-step-adding-a-simple-tab)
5. [Step-by-Step: Adding a Multi-Sub-Tab Module](#step-by-step-adding-a-multi-sub-tab-module)
6. [Aesthetic & Consistency Guidelines](#aesthetic--consistency-guidelines)
7. [Common Patterns & Best Practices](#common-patterns--best-practices)
8. [Integration Checklist](#integration-checklist)

---

## Architecture Overview

### The MVP Pattern

The application follows the **Model-View-Presenter (MVP)** pattern:

```
┌─────────────────┐
│   MainWindow    │  ← QMainWindow with QTabWidget
└────────┬────────┘
         │
         ├── Tab 1 (Simple)
         │   ├── Presenter  ← Business logic
         │   ├── View       ← UI (QWidget)
         │   └── Model      ← Data & state
         │
         └── Tab 2 (Multi-Sub-Tab)
             ├── ModuleView (QWidget with QTabWidget)
             │   ├── Sub-Tab 1
             │   │   ├── Presenter
             │   │   ├── View
             │   │   └── (shares parent model)
             │   └── Sub-Tab 2
             │       ├── Presenter
             │       ├── View
             │       └── (shares parent model)
             └── Model (shared across sub-tabs)
```

### Key Principles

1. **Separation of Concerns**: View handles UI, Presenter handles logic, Model handles data
2. **Signal-based Communication**: Use Qt signals/slots for loose coupling
3. **Shared Models**: Sub-tabs within a module typically share a common model
4. **Context Provider**: AppContext provides shared resources (config, data paths, etc.)
5. **Component Library**: Use standardized UI components for consistency

---

## Tab Types & When to Use

### 1. Simple Tab (Single View)

**Use when:**
- Single focused functionality
- No need for multiple sub-views
- Relatively simple UI

**Examples in codebase:**
- **Remote Docs** - Single view for document management
- Single-purpose utilities

**File Structure:**
```
app/
└── your_module/
    ├── __init__.py
    ├── presenter.py      # YourModulePresenter
    ├── view.py          # YourModuleView (QWidget)
    └── model.py         # YourModuleModel (optional)
```

### 2. Multi-Sub-Tab Module

**Use when:**
- Multiple related functionalities
- Need to organize complex features
- Sub-tabs share data/models
- Workflows span multiple views

**Examples in codebase:**
- **EPD Tools** - Search EPD + Identify Best EPD
- **Document Scanner** - Search + Configuration + History + Compare Versions

**File Structure:**
```
app/
└── your_module/
    ├── __init__.py
    ├── your_module_tab.py      # ModuleView (QWidget with QTabWidget)
    ├── your_module_model.py    # Shared model
    ├── your_module_presenter.py # Top-level presenter (optional)
    ├── SubTab1/
    │   ├── __init__.py
    │   ├── presenter.py
    │   ├── view.py
    │   └── model.py (if needed)
    └── SubTab2/
        ├── __init__.py
        ├── presenter.py
        ├── view.py
        └── model.py (if needed)
```

---

## Component Patterns

### Standard Components (from `app.ui.components`)

Always use the standard component library for consistency:

```python
from app.ui.components import (
    StandardLabel, TextStyle,
    StandardButton, ButtonRole,
    StandardLineEdit, StandardTextEdit,
    StandardComboBox,
    StandardCheckBox,
    StandardGroupBox,
    StandardTableWidget,
)
```

#### Key Components:

| Component | Purpose | Usage |
|-----------|---------|-------|
| `StandardLabel` | Text labels with consistent styling | `StandardLabel("Text", style=TextStyle.TITLE)` |
| `StandardButton` | Action buttons | `StandardButton("Click", role=ButtonRole.PRIMARY)` |
| `StandardLineEdit` | Single-line text input | `StandardLineEdit(placeholder="Enter text...")` |
| `StandardTextEdit` | Multi-line text input | `StandardTextEdit(placeholder="Details...")` |
| `StandardGroupBox` | Grouped content sections | `StandardGroupBox("Section", collapsible=True)` |
| `StandardTableWidget` | Data tables | `StandardTableWidget()` |

#### Text Styles:

```python
TextStyle.TITLE       # Large, bold headers
TextStyle.SUBTITLE    # Section headers
TextStyle.LABEL       # Standard form labels
TextStyle.NOTES       # Smaller, muted text
TextStyle.STATUS      # Status messages
```

#### Button Roles:

```python
ButtonRole.PRIMARY    # Main actions (blue/green)
ButtonRole.SECONDARY  # Alternative actions (gray)
ButtonRole.DANGER     # Destructive actions (red)
ButtonRole.SUCCESS    # Positive actions (green)
```

### Base Tab View (`BaseTabView`)

For complex tabs, inherit from `BaseTabView` which provides:

```python
from app.ui.base_sub_tab_view import BaseTabView

class YourView(BaseTabView):
    def __init__(self):
        super().__init__()
        # Layout already includes:
        # - self.header_frame (top 10%)
        # - self.main_splitter (left/right split)
        # - self.left_content_frame (results area)
        # - self.context_box (right top)
        # - self.footer_box (right bottom)
        # - self.help_label (? Help button)
```

**Features:**
- Pre-configured 3-panel layout (Results | Context + Footer)
- Built-in help dialog system
- Consistent section banners
- Status/record count label
- Professional footer with build info

---

## Step-by-Step: Adding a Simple Tab

### Example: Adding a "Cable Calculator" Tab

#### 1. Create Module Structure

```bash
mkdir app/cable_calculator
touch app/cable_calculator/__init__.py
touch app/cable_calculator/presenter.py
touch app/cable_calculator/view.py
touch app/cable_calculator/model.py
```

#### 2. Create the Model (`model.py`)

```python
"""
Cable Calculator Model
"""
from PySide6.QtCore import QObject, Signal


class CableCalculatorModel(QObject):
    """Model for cable length calculations"""
    
    calculation_complete = Signal(dict)  # Emits result data
    error_occurred = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._results = {}
    
    def calculate_voltage_drop(self, length: float, current: float, 
                               wire_gauge: int) -> dict:
        """Calculate voltage drop for given parameters"""
        try:
            # Your calculation logic
            result = {
                'voltage_drop': 0.0,
                'percentage': 0.0,
                'acceptable': True
            }
            
            self._results = result
            self.calculation_complete.emit(result)
            return result
            
        except Exception as e:
            self.error_occurred.emit(str(e))
            return {}
```

#### 3. Create the View (`view.py`)

```python
"""
Cable Calculator View
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout
from PySide6.QtCore import Signal
from app.ui.components import (
    StandardLabel, TextStyle,
    StandardButton, ButtonRole,
    StandardLineEdit,
    StandardGroupBox
)


class CableCalculatorView(QWidget):
    """UI for cable calculations"""
    
    # Signals
    calculate_requested = Signal(dict)  # Emits input parameters
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = StandardLabel("Cable Calculator", style=TextStyle.TITLE)
        layout.addWidget(title)
        
        # Description
        description = StandardLabel(
            "Calculate voltage drop and wire sizing for cable runs.",
            style=TextStyle.NOTES
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Input Section
        input_group = StandardGroupBox("Input Parameters")
        input_layout = QFormLayout()
        
        self.length_input = StandardLineEdit(placeholder="Enter length in feet")
        self.current_input = StandardLineEdit(placeholder="Enter current in amps")
        self.gauge_input = StandardLineEdit(placeholder="Enter wire gauge (AWG)")
        
        input_layout.addRow("Cable Length:", self.length_input)
        input_layout.addRow("Current Draw:", self.current_input)
        input_layout.addRow("Wire Gauge:", self.gauge_input)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Calculate Button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.calculate_btn = StandardButton("Calculate", role=ButtonRole.PRIMARY)
        self.calculate_btn.clicked.connect(self._on_calculate)
        button_layout.addWidget(self.calculate_btn)
        
        layout.addLayout(button_layout)
        
        # Results Section
        self.results_group = StandardGroupBox("Results")
        results_layout = QVBoxLayout()
        
        self.results_label = StandardLabel("No calculation performed", 
                                          style=TextStyle.NOTES)
        results_layout.addWidget(self.results_label)
        
        self.results_group.setLayout(results_layout)
        layout.addWidget(self.results_group)
        
        layout.addStretch()
    
    def _on_calculate(self):
        """Handle calculate button click"""
        try:
            params = {
                'length': float(self.length_input.text()),
                'current': float(self.current_input.text()),
                'gauge': int(self.gauge_input.text())
            }
            self.calculate_requested.emit(params)
        except ValueError:
            self.show_error("Please enter valid numeric values")
    
    def display_results(self, results: dict):
        """Display calculation results"""
        text = f"""
        Voltage Drop: {results['voltage_drop']:.2f}V
        Percentage: {results['percentage']:.1f}%
        Status: {'✓ Acceptable' if results['acceptable'] else '✗ Too High'}
        """
        self.results_label.setText(text)
    
    def show_error(self, message: str):
        """Show error message"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Input Error", message)
```

#### 4. Create the Presenter (`presenter.py`)

```python
"""
Cable Calculator Presenter
"""
from PySide6.QtCore import QObject
from app.core.base_presenter import BasePresenter
from .view import CableCalculatorView
from .model import CableCalculatorModel


class CableCalculatorPresenter(BasePresenter):
    """Presenter for Cable Calculator"""
    
    def __init__(self, context):
        self.model = CableCalculatorModel()
        self.view = CableCalculatorView()
        super().__init__(context, self.view, self.model, title="Cable Calculator")
        
        self.bind()
    
    def bind(self):
        """Connect signals between view and model"""
        # View → Presenter → Model
        self.view.calculate_requested.connect(self.on_calculate_requested)
        
        # Model → Presenter → View
        self.model.calculation_complete.connect(self.on_calculation_complete)
        self.model.error_occurred.connect(self.on_error)
    
    def on_calculate_requested(self, params: dict):
        """Handle calculation request from view"""
        self.model.calculate_voltage_drop(
            params['length'],
            params['current'],
            params['gauge']
        )
    
    def on_calculation_complete(self, results: dict):
        """Handle completed calculation"""
        self.view.display_results(results)
    
    def on_error(self, error_message: str):
        """Handle errors"""
        self.view.show_error(error_message)
```

#### 5. Create Package Init (`__init__.py`)

```python
"""
Cable Calculator Module
"""
from .presenter import CableCalculatorPresenter

__all__ = ['CableCalculatorPresenter']
```

#### 6. Add to Main Window

Edit `app/tabs/main_window.py`:

```python
from app.cable_calculator import CableCalculatorPresenter

class MainWindow(QMainWindow):
    def __init__(self, context):
        super().__init__()
        # ... existing code ...
        
        # Add your new tab
        self.cable_calc = CableCalculatorPresenter(context)
        
        # ... existing tabs ...
        self.tabs.addTab(self.cable_calc.view, self.cable_calc.title)
```

**Done!** Your simple tab is now integrated.

---

## Step-by-Step: Adding a Multi-Sub-Tab Module

### Example: Adding a "Wire Management" Module with Sub-Tabs

This module will have:
- **Wire Sizing** sub-tab
- **Color Codes** sub-tab
- **Inventory** sub-tab

#### 1. Create Module Structure

```bash
mkdir -p app/wire_management
mkdir -p app/wire_management/WireSizing
mkdir -p app/wire_management/ColorCodes
mkdir -p app/wire_management/Inventory

touch app/wire_management/__init__.py
touch app/wire_management/wire_management_tab.py
touch app/wire_management/wire_management_model.py
touch app/wire_management/wire_management_presenter.py

touch app/wire_management/WireSizing/__init__.py
touch app/wire_management/WireSizing/presenter.py
touch app/wire_management/WireSizing/view.py

touch app/wire_management/ColorCodes/__init__.py
touch app/wire_management/ColorCodes/presenter.py
touch app/wire_management/ColorCodes/view.py

touch app/wire_management/Inventory/__init__.py
touch app/wire_management/Inventory/presenter.py
touch app/wire_management/Inventory/view.py
```

#### 2. Create Shared Model (`wire_management_model.py`)

```python
"""
Wire Management Shared Model
"""
from PySide6.QtCore import QObject, Signal


class WireManagementModel(QObject):
    """Shared model for all wire management sub-tabs"""
    
    # Signals
    wire_data_loaded = Signal(list)
    inventory_updated = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self._wire_database = []
        self._inventory = {}
    
    def load_wire_data(self):
        """Load wire specifications"""
        # Load from file/database
        self._wire_database = [
            {'gauge': 12, 'diameter': 2.05, 'resistance': 1.588},
            {'gauge': 14, 'diameter': 1.63, 'resistance': 2.525},
            # ... more data
        ]
        self.wire_data_loaded.emit(self._wire_database)
    
    def get_wire_specs(self, gauge: int) -> dict:
        """Get specifications for a wire gauge"""
        for wire in self._wire_database:
            if wire['gauge'] == gauge:
                return wire
        return {}
    
    def update_inventory(self, gauge: int, quantity: int):
        """Update inventory quantities"""
        self._inventory[gauge] = quantity
        self.inventory_updated.emit(self._inventory)
```

#### 3. Create Sub-Tab 1: Wire Sizing

**`WireSizing/view.py`:**

```python
"""
Wire Sizing View
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout
from PySide6.QtCore import Signal
from app.ui.components import (
    StandardLabel, TextStyle,
    StandardButton, ButtonRole,
    StandardLineEdit,
    StandardGroupBox
)


class WireSizingView(QWidget):
    """UI for wire sizing calculations"""
    
    size_calculation_requested = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = StandardLabel("Wire Sizing Calculator", style=TextStyle.TITLE)
        layout.addWidget(title)
        
        # Input form
        input_group = StandardGroupBox("Parameters")
        form = QFormLayout()
        
        self.current_input = StandardLineEdit(placeholder="Amps")
        self.length_input = StandardLineEdit(placeholder="Feet")
        
        form.addRow("Current:", self.current_input)
        form.addRow("Length:", self.length_input)
        
        input_group.setLayout(form)
        layout.addWidget(input_group)
        
        # Calculate button
        self.calc_btn = StandardButton("Calculate Size", role=ButtonRole.PRIMARY)
        self.calc_btn.clicked.connect(self._on_calculate)
        layout.addWidget(self.calc_btn)
        
        # Results
        self.result_label = StandardLabel("", style=TextStyle.NOTES)
        layout.addWidget(self.result_label)
        
        layout.addStretch()
    
    def _on_calculate(self):
        params = {
            'current': float(self.current_input.text()),
            'length': float(self.length_input.text())
        }
        self.size_calculation_requested.emit(params)
    
    def display_result(self, recommended_gauge: int):
        self.result_label.setText(f"Recommended: {recommended_gauge} AWG")
```

**`WireSizing/presenter.py`:**

```python
"""
Wire Sizing Presenter
"""
from PySide6.QtCore import QObject
from .view import WireSizingView


class WireSizingPresenter(QObject):
    """Presenter for Wire Sizing sub-tab"""
    
    def __init__(self, context, shared_model):
        super().__init__()
        self.context = context
        self.model = shared_model  # Use shared model
        self.view = WireSizingView()
        
        self.bind()
    
    def bind(self):
        self.view.size_calculation_requested.connect(self.on_calculate)
    
    def on_calculate(self, params: dict):
        """Calculate recommended wire size"""
        # Use shared model data
        current = params['current']
        length = params['length']
        
        # Simple calculation (you'd use model.get_wire_specs())
        if current < 15:
            gauge = 14
        elif current < 20:
            gauge = 12
        else:
            gauge = 10
        
        self.view.display_result(gauge)
```

#### 4. Create Sub-Tab 2 & 3 (Similar Pattern)

Follow the same pattern for `ColorCodes` and `Inventory` sub-tabs.

#### 5. Create Module View (`wire_management_tab.py`)

```python
"""
Wire Management Module - Main tab with sub-tabs
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from .WireSizing.presenter import WireSizingPresenter
from .ColorCodes.presenter import ColorCodesPresenter
from .Inventory.presenter import InventoryPresenter
from .wire_management_model import WireManagementModel


class WireManagementModuleView(QWidget):
    """Main Wire Management module containing sub-tabs"""
    
    def __init__(self, context):
        super().__init__()
        self.context = context
        
        # Create shared model
        self.model = WireManagementModel()
        
        # Create sub-presenters with shared model
        self.sizing_presenter = WireSizingPresenter(context, self.model)
        self.colors_presenter = ColorCodesPresenter(context, self.model)
        self.inventory_presenter = InventoryPresenter(context, self.model)
        
        # Connect model signals to presenters
        self.model.wire_data_loaded.connect(
            self.colors_presenter.on_data_loaded
        )
        self.model.inventory_updated.connect(
            self.inventory_presenter.on_inventory_changed
        )
        
        self._setup_ui()
        self.start_loading()
    
    def _setup_ui(self):
        """Setup the tabbed interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Add sub-tabs
        self.tabs.addTab(self.sizing_presenter.view, "Wire Sizing")
        self.tabs.addTab(self.colors_presenter.view, "Color Codes")
        self.tabs.addTab(self.inventory_presenter.view, "Inventory")
        
        layout.addWidget(self.tabs)
    
    def start_loading(self):
        """Load initial data"""
        self.model.load_wire_data()
```

#### 6. Create Module Presenter (`wire_management_presenter.py`)

```python
"""
Wire Management Module Presenter
"""
from PySide6.QtCore import QObject
from app.core.base_presenter import BasePresenter
from .wire_management_tab import WireManagementModuleView


class WireManagementPresenter(BasePresenter):
    """Top-level presenter for Wire Management module"""
    
    def __init__(self, context):
        self.view = WireManagementModuleView(context)
        # Model is owned by the view in this pattern
        super().__init__(context, self.view, None, title="Wire Management")
    
    def get_current_presenter(self):
        """Get the currently active sub-tab presenter"""
        current_index = self.view.tabs.currentIndex()
        
        if current_index == 0:
            return self.view.sizing_presenter
        elif current_index == 1:
            return self.view.colors_presenter
        elif current_index == 2:
            return self.view.inventory_presenter
        
        return None
```

#### 7. Create Package Init (`__init__.py`)

```python
"""
Wire Management Module
"""
from .wire_management_presenter import WireManagementPresenter

__all__ = ['WireManagementPresenter']
```

#### 8. Add to Main Window

```python
from app.wire_management import WireManagementPresenter

class MainWindow(QMainWindow):
    def __init__(self, context):
        super().__init__()
        # ... existing code ...
        
        self.wire_mgmt = WireManagementPresenter(context)
        
        # ... existing tabs ...
        self.tabs.addTab(self.wire_mgmt.view, self.wire_mgmt.title)
```

**Done!** Your multi-sub-tab module is integrated.

---

## Aesthetic & Consistency Guidelines

### Layout Principles

1. **Margins & Spacing**
   ```python
   layout.setContentsMargins(10, 10, 10, 10)  # Standard content margin
   layout.setSpacing(10)  # Standard spacing between widgets
   ```

2. **Section Grouping**
   - Always use `StandardGroupBox` for logical sections
   - Collapsible sections for optional/advanced content
   ```python
   group = StandardGroupBox("Section Title", collapsible=True)
   ```

3. **Form Layouts**
   ```python
   from PySide6.QtWidgets import QFormLayout
   
   form = QFormLayout()
   form.addRow("Label:", widget)  # Consistent label alignment
   ```

### Typography Hierarchy

```python
# Page Title
StandardLabel("Main Title", style=TextStyle.TITLE)

# Section Headers
StandardLabel("Section Header", style=TextStyle.SUBTITLE)

# Form Labels
StandardLabel("Field Label:", style=TextStyle.LABEL)

# Help Text / Descriptions
StandardLabel("Help text here...", style=TextStyle.NOTES)
label.setWordWrap(True)  # Always wrap long text

# Status Messages
StandardLabel("Status: Ready", style=TextStyle.STATUS)
```

### Button Patterns

```python
# Primary action (one per section)
StandardButton("Save", role=ButtonRole.PRIMARY)

# Secondary actions
StandardButton("Cancel", role=ButtonRole.SECONDARY)

# Destructive actions
StandardButton("Delete", role=ButtonRole.DANGER)

# Success confirmations
StandardButton("Apply", role=ButtonRole.SUCCESS)
```

### Color & Theming

**Don't hardcode colors!** Use the theme system:

```python
from app.core.config import UI_COLORS, UI_STYLES

# Access theme colors
background = UI_COLORS['section_background']
highlight = UI_COLORS['section_highlight_primary']
```

### Spacing & Alignment

```python
# Horizontal button group (right-aligned)
button_layout = QHBoxLayout()
button_layout.addStretch()  # Push buttons right
button_layout.addWidget(cancel_btn)
button_layout.addWidget(save_btn)

# Vertical spacing
layout.addStretch()  # Push content to top
```

### Table Styling

```python
from app.ui.components import StandardTableWidget

table = StandardTableWidget()
table.setColumnCount(3)
table.setHorizontalHeaderLabels(["Name", "Value", "Actions"])

# Configure column sizing
from PySide6.QtWidgets import QHeaderView
table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
```

---

## Common Patterns & Best Practices

### 1. Async Data Loading

```python
from PySide6.QtCore import QTimer

def start_loading(self):
    """Load data asynchronously"""
    # Delay loading slightly so UI renders first
    QTimer.singleShot(100, self.model.load_data)
```

### 2. Signal Naming Conventions

```python
class MyView(QWidget):
    # Past tense for completed actions
    search_completed = Signal(list)
    data_loaded = Signal()
    
    # Request/action for user-initiated events
    search_requested = Signal(str)
    save_requested = Signal(dict)
    
    # State changes
    selection_changed = Signal(object)
    filter_changed = Signal(str)
```

### 3. Error Handling in Views

```python
def show_error(self, message: str, title: str = "Error"):
    """Display error dialog"""
    from PySide6.QtWidgets import QMessageBox
    QMessageBox.critical(self, title, message)

def show_warning(self, message: str, title: str = "Warning"):
    """Display warning dialog"""
    from PySide6.QtWidgets import QMessageBox
    QMessageBox.warning(self, title, message)

def show_info(self, message: str, title: str = "Information"):
    """Display info dialog"""
    from PySide6.QtWidgets import QMessageBox
    QMessageBox.information(self, title, message)
```

### 4. Confirmation Dialogs

```python
def confirm_delete(self, item_name: str) -> bool:
    """Ask user to confirm deletion"""
    from PySide6.QtWidgets import QMessageBox
    
    reply = QMessageBox.question(
        self,
        "Confirm Deletion",
        f"Are you sure you want to delete '{item_name}'?",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No  # Default to No
    )
    
    return reply == QMessageBox.Yes
```

### 5. Context Providers (Cross-Tab Communication)

```python
# In main_window.py
connector_context = ConnectorContextProvider(self.connectors.model)
self.document_scanner.search_presenter.register_context_provider(
    connector_context
)
```

See existing example: `ConnectorContextProvider` provides connector data to Document Scanner.

### 6. Shared Configuration

```python
from app.core.config_manager import ConfigManager

# Read config
value = ConfigManager.get_setting('my_module', 'my_setting', default_value)

# Write config
ConfigManager.set_setting('my_module', 'my_setting', new_value)
```

### 7. Help Content

```python
class MyView(BaseTabView):
    def __init__(self):
        super().__init__()
        
        # Set custom help content
        self.set_help_content("""
        <h2>My Feature Help</h2>
        <p>Description of what this feature does.</p>
        
        <h3>How to Use</h3>
        <ol>
            <li>Step 1</li>
            <li>Step 2</li>
            <li>Step 3</li>
        </ol>
        
        <h3>Tips</h3>
        <ul>
            <li>Tip 1</li>
            <li>Tip 2</li>
        </ul>
        """)
```

---

## Integration Checklist

### Before Starting

- [ ] Determine if simple tab or multi-sub-tab module is needed
- [ ] Sketch out UI layout on paper
- [ ] Identify what data/models are needed
- [ ] Identify signals needed between components
- [ ] Check if existing components can be reused

### During Development

- [ ] Follow MVP pattern (separate Model, View, Presenter)
- [ ] Use standard components from `app.ui.components`
- [ ] Follow naming conventions for files and classes
- [ ] Use signals for all communication
- [ ] Add docstrings to all classes and methods
- [ ] Use type hints for function parameters
- [ ] Handle errors gracefully with user feedback

### File Structure Created

- [ ] Module directory created under `app/`
- [ ] `__init__.py` exports presenter
- [ ] Presenter file (inherits `BasePresenter`)
- [ ] View file (inherits `QWidget` or `BaseTabView`)
- [ ] Model file (inherits `QObject`)
- [ ] For sub-tabs: module tab file with `QTabWidget`

### Integration Steps

- [ ] Import presenter in `main_window.py`
- [ ] Initialize presenter with context
- [ ] Add tab to `QTabWidget`
- [ ] Test tab switching and functionality
- [ ] Verify consistent styling with other tabs

### Testing Checklist

- [ ] Tab appears in correct position
- [ ] Title/icon displays correctly
- [ ] All buttons respond to clicks
- [ ] Signals fire correctly
- [ ] Error handling works
- [ ] Help content displays (if applicable)
- [ ] Consistent with application aesthetic
- [ ] No console errors on load
- [ ] Data persists correctly (if applicable)

---

## Quick Reference: File Templates

### Simple Tab Presenter Template

```python
"""
[Module Name] Presenter
"""
from PySide6.QtCore import QObject
from app.core.base_presenter import BasePresenter
from .view import [ModuleName]View
from .model import [ModuleName]Model


class [ModuleName]Presenter(BasePresenter):
    """Presenter for [Module Name]"""
    
    def __init__(self, context):
        self.model = [ModuleName]Model()
        self.view = [ModuleName]View()
        super().__init__(context, self.view, self.model, title="[Display Title]")
        
        self.bind()
    
    def bind(self):
        """Connect signals"""
        # View → Model
        self.view.action_requested.connect(self.on_action)
        
        # Model → View
        self.model.data_changed.connect(self.on_data_changed)
    
    def on_action(self, params):
        """Handle action from view"""
        self.model.perform_action(params)
    
    def on_data_changed(self, data):
        """Handle data change from model"""
        self.view.update_display(data)
```

### Multi-Sub-Tab Module View Template

```python
"""
[Module Name] Module - Main tab with sub-tabs
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from .SubTab1.presenter import SubTab1Presenter
from .SubTab2.presenter import SubTab2Presenter
from .[module_name]_model import [ModuleName]Model


class [ModuleName]ModuleView(QWidget):
    """Main [Module Name] module containing sub-tabs"""
    
    def __init__(self, context):
        super().__init__()
        self.context = context
        
        # Create shared model
        self.model = [ModuleName]Model()
        
        # Create sub-presenters
        self.subtab1_presenter = SubTab1Presenter(context, self.model)
        self.subtab2_presenter = SubTab2Presenter(context, self.model)
        
        # Connect signals
        self.model.data_changed.connect(self.subtab1_presenter.on_data_changed)
        
        self._setup_ui()
        self.start_loading()
    
    def _setup_ui(self):
        """Setup the tabbed interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        
        self.tabs.addTab(self.subtab1_presenter.view, "Sub-Tab 1")
        self.tabs.addTab(self.subtab2_presenter.view, "Sub-Tab 2")
        
        layout.addWidget(self.tabs)
    
    def start_loading(self):
        """Initialize data"""
        self.model.load_data()
```

---

## Examples in Codebase

Study these existing implementations:

### Simple Tabs
- **Remote Docs** (`app/remote_docs/`)
  - Single view with upload/download
  - Table display
  - Simple presenter pattern

### Multi-Sub-Tab Modules
- **EPD Tools** (`app/epd/`)
  - 2 sub-tabs: Search EPD, Identify Best EPD
  - Shared EpdModel
  - Top-level coordinator (EpdPresenter)

- **Document Scanner** (`app/document_scanner/`)
  - 4 sub-tabs: Search, Configuration, History, Compare Versions
  - Shared DocumentScannerModel
  - Signal-based communication between sub-tabs

### Complex Views
- **Connector Tab** (`app/presenters/connectors_presenter.py`)
  - Table with context menu
  - Advanced filtering
  - Context provider for other tabs

---

## Summary: Decision Tree

```
Need to add functionality?
│
├─ Single focused feature?
│  └─ Create Simple Tab
│     ├─ Create model.py
│     ├─ Create view.py  
│     ├─ Create presenter.py
│     └─ Add to main_window.py
│
└─ Multiple related features?
   └─ Create Multi-Sub-Tab Module
      ├─ Create shared model
      ├─ Create module_tab.py (with QTabWidget)
      ├─ For each sub-tab:
      │  ├─ Create SubTab/view.py
      │  ├─ Create SubTab/presenter.py
      │  └─ Connect to shared model
      └─ Add to main_window.py
```

---

## Need Help?

- Check `docs/COMPONENT_LIBRARY.md` for component usage
- Check `docs/COMPONENT_QUICK_REF.md` for quick component reference
- Look at existing tabs for patterns:
  - Simple: `app/remote_docs/`
  - Complex: `app/document_scanner/`
- Follow the MVP pattern consistently
- Use signals for all cross-component communication

---

**Remember:** Consistency is key! Follow existing patterns and use the standard component library to maintain a cohesive application aesthetic.
