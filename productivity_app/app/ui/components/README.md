# UI Components Library

**Location:** `app/ui/components/`

Standardized, reusable UI components with consistent styling and behavior. Each component is in its own file for better organization and maintainability.

---

## 📁 File Structure

```
app/ui/components/
├── __init__.py          # Package exports
├── README.md           # This file - complete documentation
├── enums.py            # ButtonRole, ButtonSize, ComboSize, TextStyle, DialogResult, SelectionMode
├── constants.py        # COMPONENT_SIZES, BUTTON_COLORS
├── button.py           # StandardButton component
├── label.py            # StandardLabel component
├── combobox.py         # StandardComboBox component
├── input.py            # StandardInput component
├── drop_area.py        # StandardDropArea component
├── checkbox.py         # StandardCheckBox component
├── progress_bar.py     # StandardProgressBar component
├── radio_button.py     # StandardRadioButton component + create_radio_group()
├── text_area.py        # StandardTextArea component
├── spin_box.py         # StandardSpinBox component
├── group_box.py        # StandardGroupBox component
├── form_layout.py      # StandardFormLayout component
├── warning_dialog.py   # StandardWarningDialog component
└── helpers.py          # create_button_row(), create_form_row()
```

---

## 🚀 Quick Start

```python
from app.ui.components import (
    # Core components
    StandardButton, ButtonRole, ButtonSize,
    StandardLabel, TextStyle,
    StandardComboBox, ComboSize,
    StandardInput,
    StandardDropArea,
    # Interactive components
    StandardCheckBox,
    StandardProgressBar,
    StandardRadioButton, create_radio_group,
    StandardTextArea,
    StandardSpinBox,
    StandardGroupBox,
    # Layout components
    StandardFormLayout,
    StandardWarningDialog, DialogResult,
    # Helpers
    create_button_row,
    create_form_row
)

# Create components with role-based styling
btn = StandardButton("Save", role=ButtonRole.PRIMARY)
label = StandardLabel("Title", style=TextStyle.TITLE)
combo = StandardComboBox(size=ComboSize.SINGLE)
checkbox = StandardCheckBox("Enable feature")
progress = StandardProgressBar()
```

---

## 📚 Components Reference

### 1. StandardButton (`button.py`)

**Purpose:** Standardized buttons with role-based coloring and size variants

**Import:**
```python
from app.ui.components import StandardButton, ButtonRole, ButtonSize
```

**Constructor:**
```python
StandardButton(
    text: str,
    role: ButtonRole = ButtonRole.PRIMARY,
    size: ButtonSize = ButtonSize.FULL,
    icon: Optional[str] = None,
    parent: Optional[QWidget] = None
)
```

**Tuning Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | str | Required | Button text |
| `role` | ButtonRole | PRIMARY | Color scheme (see roles below) |
| `size` | ButtonSize | FULL | Size variant (see sizes below) |
| `icon` | str | None | Optional icon/emoji prefix |
| `parent` | QWidget | None | Parent widget |

**Button Roles (role parameter):**

| Role | Color | Hex | Use Case |
|------|-------|-----|----------|
| `PRIMARY` | Blue | #0078d4 | Main actions (Save, Submit, Compare) |
| `SECONDARY` | Gray | #6c757d | Secondary actions (Cancel, Close) |
| `SUCCESS` | Green | #28a745 | Positive actions (Apply, Confirm) |
| `DANGER` | Red | #dc3545 | Destructive actions (Delete, Remove) |
| `WARNING` | Orange | #ffc107 | Warning actions (Reset, Revert) |
| `INFO` | Light Blue | #17a2b8 | Informational (Export, Help) |

**Button Sizes (size parameter):**

| Size | Width | Height | Use Case |
|------|-------|--------|----------|
| `FULL` | Auto | 36px | Default, stretches to fill |
| `HALF_WIDTH` | 150px | 36px | Fixed width buttons |
| `HALF_HEIGHT` | Auto | 24px | Compact height |
| `COMPACT` | 100px | 24px | Small buttons (toolbar) |

**Examples:**

```python
# Primary action button (default)
save_btn = StandardButton("Save", role=ButtonRole.PRIMARY)

# Danger button with custom size
delete_btn = StandardButton("Delete", role=ButtonRole.DANGER, size=ButtonSize.HALF_WIDTH)

# Button with icon
search_btn = StandardButton("Search", icon="🔍", role=ButtonRole.PRIMARY)

# Compact secondary button
close_btn = StandardButton("X", role=ButtonRole.SECONDARY, size=ButtonSize.COMPACT)

# Connect to slot
save_btn.clicked.connect(self.on_save)
```

---

### 2. StandardLabel (`label.py`)

**Purpose:** Standardized text labels with consistent typography

**Import:**
```python
from app.ui.components import StandardLabel, TextStyle
```

**Constructor:**
```python
StandardLabel(
    text: str,
    style: TextStyle = TextStyle.LABEL,
    color: Optional[str] = None,
    parent: Optional[QWidget] = None
)
```

**Tuning Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | str | Required | Label text |
| `style` | TextStyle | LABEL | Typography style (see styles below) |
| `color` | str | None | Custom color override (hex or name) |
| `parent` | QWidget | None | Parent widget |

**Text Styles (style parameter):**

| Style | Font Size | Weight | Color | Use Case |
|-------|-----------|--------|-------|----------|
| `TITLE` | 14pt | Bold | Black | Page titles |
| `SECTION` | 12pt | Bold | Black | Section headers |
| `SUBSECTION` | 11pt | Bold | Dark Gray | Subsection headers |
| `LABEL` | 10pt | Normal | Black | Form labels, standard text |
| `NOTES` | 9pt | Normal Italic | Light Gray | Helper text, hints |
| `STATUS` | 10pt | Normal | Gray | Status messages |

**Methods:**

```python
set_color(color: str) -> None
```
Update label color dynamically (use this instead of setStyleSheet)

**Examples:**

```python
# Title label
title = StandardLabel("Document Scanner", style=TextStyle.TITLE)

# Section header
section = StandardLabel("Configuration", style=TextStyle.SECTION)

# Helper notes
notes = StandardLabel("This field is optional", style=TextStyle.NOTES)

# Status with dynamic color
status = StandardLabel("Ready", style=TextStyle.STATUS)
status.set_color("green")  # Change to green
status.setText("Processing...")
status.set_color("#ff9800")  # Change to orange

# Custom color override
error = StandardLabel("Error", style=TextStyle.LABEL, color="#ff0000")
```

**Typography Hierarchy:**
```
TITLE (14pt bold)
└── SECTION (12pt bold)
    └── SUBSECTION (11pt bold)
        └── LABEL (10pt)
            └── NOTES (9pt italic)
```

---

### 3. StandardComboBox (`combobox.py`)

**Purpose:** Standardized dropdown with consistent sizing

**Import:**
```python
from app.ui.components import StandardComboBox, ComboSize
```

**Constructor:**
```python
StandardComboBox(
    size: ComboSize = ComboSize.SINGLE,
    items: Optional[list] = None,
    parent: Optional[QWidget] = None
)
```

**Tuning Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `size` | ComboSize | SINGLE | Size variant (see sizes below) |
| `items` | list | None | Initial items to populate |
| `parent` | QWidget | None | Parent widget |

**Combo Sizes (size parameter):**

| Size | Width | Height | Use Case |
|------|-------|--------|----------|
| `SINGLE` | 200px | 30px | Version selectors, short names |
| `DOUBLE` | 400px | 30px | Document names, file paths |
| `FULL` | Auto | 30px | Main selectors (stretches to fill) |

**Examples:**

```python
# Single width dropdown
version_combo = StandardComboBox(size=ComboSize.SINGLE)

# With initial items
document_combo = StandardComboBox(
    size=ComboSize.DOUBLE,
    items=["Document A", "Document B", "Document C"]
)

# Full width
main_combo = StandardComboBox(size=ComboSize.FULL)

# Add items after creation
version_combo.addItems(["v1.0", "v2.0", "v3.0"])

# Connect to signal
version_combo.currentTextChanged.connect(self.on_version_changed)

# Get current selection
selected = version_combo.currentText()
```

---

### 4. StandardInput (`input.py`)

**Purpose:** Standardized text input box

**Import:**
```python
from app.ui.components import StandardInput
```

**Constructor:**
```python
StandardInput(
    placeholder: str = "",
    width: Optional[int] = None,
    parent: Optional[QWidget] = None
)
```

**Tuning Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `placeholder` | str | "" | Placeholder text |
| `width` | int | None | Custom width in pixels (None = 200px min) |
| `parent` | QWidget | None | Parent widget |

**Size:**
- Height: 30px (fixed)
- Width: 200px minimum (default) or custom

**Examples:**

```python
# Standard input with placeholder
search_input = StandardInput(placeholder="Enter search term...")

# Custom width
path_input = StandardInput(placeholder="File path...", width=400)

# No placeholder
name_input = StandardInput()

# Connect to signals
search_input.textChanged.connect(self.on_text_changed)
search_input.returnPressed.connect(self.on_return_pressed)

# Get/set text
search_input.setText("query")
text = search_input.text()
```

---

### 5. StandardDropArea (`drop_area.py`)

**Purpose:** Standardized drag-and-drop area for file uploads

**Import:**
```python
from app.ui.components import StandardDropArea
```

**Constructor:**
```python
StandardDropArea(
    label_text: str = "Drag & Drop file here",
    allowed_extensions: tuple = ('.csv', '.xlsx', '.xls'),
    parent: Optional[QWidget] = None
)
```

**Tuning Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `label_text` | str | "Drag & Drop file here" | Text displayed in drop area |
| `allowed_extensions` | tuple | ('.csv', '.xlsx', '.xls') | Allowed file extensions |
| `parent` | QWidget | None | Parent widget |

**Signals:**
```python
file_dropped = Signal(str)  # Emitted with file path when valid file dropped
```

**Methods:**

```python
clear() -> None                    # Clear drop area, reset to default
get_file_path() -> Optional[str]   # Get currently dropped file path
```

**Examples:**

```python
# CSV files only
csv_drop = StandardDropArea(
    label_text="Drag & Drop CSV file here",
    allowed_extensions=('.csv',)  # Note: tuple requires comma!
)
csv_drop.file_dropped.connect(self.on_csv_file)

# Multiple extensions
data_drop = StandardDropArea(
    label_text="Drag & Drop data file",
    allowed_extensions=('.csv', '.xlsx', '.xls', '.json')
)
data_drop.file_dropped.connect(self.on_data_file)

# Get file path
def on_csv_file(self, file_path: str):
    print(f"CSV file: {file_path}")
    # Process file...

# Programmatic access
file_path = csv_drop.get_file_path()
if file_path:
    print(f"Current file: {file_path}")

# Clear drop area
csv_drop.clear()
```

**Size:**
- Min Height: 80px
- Width: Stretches to fill available space

**File Validation:**
- Shows error dialog if wrong file type
- Only emits signal for valid files

---

### 6. Helper Functions (`helpers.py`)

#### create_button_row()

**Purpose:** Create horizontal row of buttons with optional stretch

**Import:**
```python
from app.ui.components import create_button_row
```

**Signature:**
```python
create_button_row(
    *buttons,
    stretch_after: int = -1
) -> QWidget
```

**Tuning Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*buttons` | QPushButton | Required | Variable number of button widgets |
| `stretch_after` | int | -1 | Index after which to add stretch (-1 = right-align) |

**Stretch Behavior:**

| Value | Result | Visual |
|-------|--------|--------|
| `-1` | Stretch before buttons | `[stretch] [Btn1] [Btn2]` (right-aligned) |
| `0` | Stretch after first button | `[Btn1] [stretch] [Btn2] [Btn3]` |
| `1` | Stretch after second | `[Btn1] [Btn2] [stretch] [Btn3]` |
| `n` | Stretch after nth button | Buttons space accordingly |

**Examples:**

```python
# Right-aligned buttons (most common)
button_row = create_button_row(
    StandardButton("Save", role=ButtonRole.PRIMARY),
    StandardButton("Cancel", role=ButtonRole.SECONDARY),
    stretch_after=-1  # or just omit (default)
)
layout.addWidget(button_row)

# Left-aligned buttons
button_row = create_button_row(
    StandardButton("Apply", role=ButtonRole.SUCCESS),
    StandardButton("Reset", role=ButtonRole.WARNING),
    stretch_after=1  # Stretch after last button
)

# Split positioning
button_row = create_button_row(
    StandardButton("Help", role=ButtonRole.INFO),      # Left
    StandardButton("Save", role=ButtonRole.PRIMARY),   # Right
    StandardButton("Cancel", role=ButtonRole.SECONDARY), # Right
    stretch_after=0  # Stretch after first button
)
```

#### create_form_row()

**Purpose:** Create form row with aligned label and input widget

**Import:**
```python
from app.ui.components import create_form_row
```

**Signature:**
```python
create_form_row(
    label_text: str,
    widget: QWidget,
    label_width: int = 100
) -> QWidget
```

**Tuning Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `label_text` | str | Required | Label text (auto-styled as LABEL) |
| `widget` | QWidget | Required | Input widget (Input, ComboBox, etc.) |
| `label_width` | int | 100 | Fixed label width for alignment |

**Label Width Guide:**

| Label Length | Suggested Width | Example |
|--------------|-----------------|---------|
| Short (1-5 chars) | 50-80px | "ID:", "Name:" |
| Medium (6-10 chars) | 100-120px | "Version:", "Document:" |
| Long (11-15 chars) | 130-150px | "Document Name:", "Configuration:" |
| Very Long (16+ chars) | 150-200px | "Output Directory:", "Advanced Settings:" |

**Examples:**

```python
# Basic form row
name_row = create_form_row(
    "Name:",
    StandardInput(placeholder="Enter name")
)
layout.addWidget(name_row)

# With combo box
version_row = create_form_row(
    "Version:",
    StandardComboBox(size=ComboSize.SINGLE, items=["v1.0", "v2.0"])
)
layout.addWidget(version_row)

# Custom label width for alignment
rows = [
    create_form_row("ID:", StandardInput(), label_width=120),
    create_form_row("Document:", StandardComboBox(size=ComboSize.DOUBLE), label_width=120),
    create_form_row("Version:", StandardComboBox(size=ComboSize.SINGLE), label_width=120),
]
for row in rows:
    layout.addWidget(row)

# With helper text below
name_row = create_form_row("Name:", StandardInput(placeholder="Enter name"))
layout.addWidget(name_row)
helper = StandardLabel("Must be unique", style=TextStyle.NOTES)
layout.addWidget(helper)
```

---

### 7. StandardCheckBox (`checkbox.py`)

**Purpose:** Consistent checkbox with tristate support

**Import:**
```python
from app.ui.components import StandardCheckBox
```

**Constructor:**
```python
StandardCheckBox(
    text: str = "",
    checked: bool = False,
    tristate: bool = False,
    parent: Optional[QWidget] = None
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | str | "" | Checkbox label text |
| `checked` | bool | False | Initial checked state |
| `tristate` | bool | False | Enable three-state checkbox |
| `parent` | QWidget | None | Parent widget |

**Methods:**
- `is_checked() -> bool` - Returns True if checked
- `set_checked(checked: bool)` - Sets checked state
- `get_state() -> Qt.CheckState` - Returns check state (Unchecked, PartiallyChecked, Checked)
- `set_state(state: Qt.CheckState)` - Sets specific check state
- `set_tristate(enable: bool)` - Enable/disable tristate

**Signals:**
- `state_changed(int)` - Emitted when state changes (0=Unchecked, 1=Partial, 2=Checked)
- `toggled(bool)` - Emitted when toggled (True=checked, False=unchecked)

**Examples:**
```python
# Basic checkbox
checkbox = StandardCheckBox("Enable feature")
checkbox.toggled.connect(lambda checked: print(f"Enabled: {checked}"))

# Pre-checked
checkbox = StandardCheckBox("Auto-save", checked=True)

# Tristate (for "select all" scenarios)
select_all = StandardCheckBox("Select All", tristate=True)
select_all.state_changed.connect(lambda state: handle_select_all(state))

# Check programmatically
if checkbox.is_checked():
    save_preference()
```

---

### 8. StandardProgressBar (`progress_bar.py`)

**Purpose:** Consistent progress indicator for long operations

**Import:**
```python
from app.ui.components import StandardProgressBar
```

**Constructor:**
```python
StandardProgressBar(
    show_percentage: bool = True,
    minimum: int = 0,
    maximum: int = 100,
    parent: Optional[QWidget] = None
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `show_percentage` | bool | True | Display percentage text |
| `minimum` | int | 0 | Minimum value |
| `maximum` | int | 100 | Maximum value |
| `parent` | QWidget | None | Parent widget |

**Methods:**
- `set_value(value: int)` - Sets progress value
- `get_value() -> int` - Returns current value
- `set_range(min: int, max: int)` - Sets min/max range
- `reset()` - Resets to minimum
- `set_text_visible(visible: bool)` - Show/hide percentage

**Signals:**
- `value_changed(int)` - Emitted when value changes

**Examples:**
```python
# Basic progress bar
progress = StandardProgressBar()
layout.addWidget(progress)

# Without percentage text
progress = StandardProgressBar(show_percentage=False)

# Update progress
for i in range(101):
    progress.set_value(i)
    QApplication.processEvents()  # Keep UI responsive

# Custom range (e.g., file rows)
progress = StandardProgressBar()
progress.set_range(0, total_rows)
progress.value_changed.connect(lambda v: print(f"Processing row {v}..."))
```

---

### 9. StandardRadioButton (`radio_button.py`)

**Purpose:** Consistent radio buttons with group helper

**Import:**
```python
from app.ui.components import StandardRadioButton, create_radio_group
```

**Constructor:**
```python
StandardRadioButton(
    text: str = "",
    checked: bool = False,
    parent: Optional[QWidget] = None
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | str | "" | Radio button label |
| `checked` | bool | False | Initial checked state |
| `parent` | QWidget | None | Parent widget |

**Methods:**
- `is_checked() -> bool` - Returns True if checked
- `set_checked(checked: bool)` - Sets checked state

**Signals:**
- `toggled(bool)` - Emitted when toggled

**Helper Function:**
```python
create_radio_group(
    *buttons: StandardRadioButton,
    default_index: int = 0
) -> QButtonGroup
```

**Examples:**
```python
# Create radio buttons
radio1 = StandardRadioButton("Use E3 Connect", checked=True)
radio2 = StandardRadioButton("Use E3 Cache")
radio3 = StandardRadioButton("Manual Mode")

# Group them (ensures only one is checked)
group = create_radio_group(radio1, radio2, radio3, default_index=0)

# Connect signals
radio1.toggled.connect(lambda checked: self.use_e3_connect() if checked else None)
radio2.toggled.connect(lambda checked: self.use_e3_cache() if checked else None)

# Check which is selected
if radio1.is_checked():
    mode = "connect"
elif radio2.is_checked():
    mode = "cache"
```

---

### 10. StandardTextArea (`text_area.py`)

**Purpose:** Multi-line text input/display with consistent styling

**Import:**
```python
from app.ui.components import StandardTextArea
```

**Constructor:**
```python
StandardTextArea(
    text: str = "",
    read_only: bool = False,
    placeholder: str = "",
    height: Optional[int] = None,
    parent: Optional[QWidget] = None
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | str | "" | Initial text content |
| `read_only` | bool | False | Read-only mode |
| `placeholder` | str | "" | Placeholder text |
| `height` | int | 120 | Fixed height (None = 60-120px) |
| `parent` | QWidget | None | Parent widget |

**Methods:**
- `get_text() -> str` - Returns current text
- `set_text(text: str)` - Sets text content
- `append_text(text: str)` - Appends text
- `clear()` - Clears all text
- `set_read_only(read_only: bool)` - Sets read-only mode
- `is_read_only() -> bool` - Returns True if read-only

**Signals:**
- `text_changed()` - Emitted when text changes

**Examples:**
```python
# Editable text area
notes = StandardTextArea(placeholder="Enter notes...")
notes.text_changed.connect(lambda: self.save_draft())
layout.addWidget(notes)

# Read-only display (for logs, results)
results = StandardTextArea(read_only=True, height=200)
results.set_text("Operation completed successfully!\nProcessed 150 rows.")
layout.addWidget(results)

# Append logs
log_area = StandardTextArea(read_only=True)
log_area.append_text("Starting process...\n")
log_area.append_text("Step 1 complete\n")
log_area.append_text("Step 2 complete\n")

# Get content
notes_text = notes.get_text()
save_to_file(notes_text)
```

---

### 11. StandardSpinBox (`spin_box.py`)

**Purpose:** Numeric input with up/down buttons

**Import:**
```python
from app.ui.components import StandardSpinBox
```

**Constructor:**
```python
StandardSpinBox(
    min_value: int = 0,
    max_value: int = 100,
    default_value: int = 0,
    suffix: str = "",
    width: Optional[int] = None,
    parent: Optional[QWidget] = None
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_value` | int | 0 | Minimum value |
| `max_value` | int | 100 | Maximum value |
| `default_value` | int | 0 | Initial value |
| `suffix` | str | "" | Text suffix (e.g., " px", " %") |
| `width` | int | 100 | Fixed width in pixels |
| `parent` | QWidget | None | Parent widget |

**Methods:**
- `get_value() -> int` - Returns current value
- `set_value(value: int)` - Sets value
- `set_range(min: int, max: int)` - Sets range
- `set_suffix(suffix: str)` - Sets suffix text

**Signals:**
- `value_changed(int)` - Emitted when value changes

**Examples:**
```python
# Basic spin box
row_spin = StandardSpinBox(min_value=1, max_value=100, default_value=1)
row_spin.value_changed.connect(lambda v: self.update_row_number(v))

# With suffix
font_size = StandardSpinBox(min_value=8, max_value=72, default_value=12, suffix=" pt")
width_spin = StandardSpinBox(min_value=50, max_value=500, default_value=200, suffix=" px")
percentage = StandardSpinBox(min_value=0, max_value=100, default_value=50, suffix=" %")

# Custom width
wide_spin = StandardSpinBox(min_value=0, max_value=9999, width=120)

# Get value
header_row = row_spin.get_value()
process_from_row(header_row)
```

---

### 12. StandardGroupBox (`group_box.py`)

**Purpose:** Container for grouping related controls

**Import:**
```python
from app.ui.components import StandardGroupBox
```

**Constructor:**
```python
StandardGroupBox(
    title: str = "",
    parent: Optional[QWidget] = None
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `title` | str | "" | Group box title |
| `parent` | QWidget | None | Parent widget |

**Methods:**
- `set_title(title: str)` - Sets title
- `get_title() -> str` - Returns title

**Examples:**
```python
# Basic group box
group = StandardGroupBox("Advanced Options")
layout = QVBoxLayout()
layout.addWidget(StandardCheckBox("Option 1"))
layout.addWidget(StandardCheckBox("Option 2"))
layout.addWidget(StandardCheckBox("Option 3"))
group.setLayout(layout)

# Form within group
settings_group = StandardGroupBox("Connection Settings")
form_layout = QVBoxLayout()
form_layout.addWidget(create_form_row("Host:", StandardInput()))
form_layout.addWidget(create_form_row("Port:", StandardSpinBox(min_value=1, max_value=65535)))
settings_group.setLayout(form_layout)

# Multiple groups
main_layout = QVBoxLayout()
main_layout.addWidget(StandardGroupBox("Basic Settings"))
main_layout.addWidget(StandardGroupBox("Advanced Settings"))
main_layout.addWidget(StandardGroupBox("Output Options"))
```

---

### 13. StandardFormLayout (`form_layout.py`)

**Purpose:** Easy form creation with aligned labels and sections

**Import:**
```python
from app.ui.components import StandardFormLayout
```

**Constructor:**
```python
StandardFormLayout(
    label_width: Optional[int] = None,
    parent: Optional[QWidget] = None
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `label_width` | int | 120 | Fixed label width for alignment |
| `parent` | QWidget | None | Parent widget |

**Methods:**
- `add_row(label: str, field: QWidget)` - Adds labeled field row
- `add_widget(widget: QWidget)` - Adds widget spanning both columns
- `add_section(title: str)` - Adds section header
- `add_spacing(height: int)` - Adds vertical spacing
- `clear()` - Removes all rows

**Examples:**
```python
# Basic form
form = StandardFormLayout()

# Add labeled rows
form.add_row("Name:", StandardInput(placeholder="Enter name..."))
form.add_row("Version:", StandardComboBox(size=ComboSize.SINGLE))
form.add_row("Output:", StandardInput(placeholder="Output path..."))

# Add sections
form.add_section("Basic Settings")
form.add_row("Document:", StandardInput())
form.add_row("Format:", StandardComboBox(size=ComboSize.SINGLE))

form.add_section("Advanced Options")
form.add_widget(StandardCheckBox("Enable advanced mode"))
form.add_widget(StandardCheckBox("Use cache"))
form.add_spacing(10)
form.add_row("Timeout:", StandardSpinBox(min_value=1, max_value=300, suffix=" sec"))

# Use in layout
container = QWidget()
container.setLayout(form)
main_layout.addWidget(container)

# Custom label width
wide_form = StandardFormLayout(label_width=150)
wide_form.add_row("Document Directory:", StandardInput())
wide_form.add_row("Output Directory:", StandardInput())
```

---

### 14. StandardWarningDialog (`warning_dialog.py`)

**Purpose:** Standard dialogs for confirmations, warnings, and messages (similar to C# MessageBox)

**Import:**
```python
from app.ui.components import StandardWarningDialog, DialogResult
```

**Static Methods:**

**show_ok(parent, title, message) -> DialogResult**
- Shows dialog with OK button only
- Returns: DialogResult.OK or DialogResult.CANCEL (if closed)

**show_yes_no(parent, title, message) -> DialogResult**
- Shows dialog with Yes and No buttons
- Returns: DialogResult.YES, DialogResult.NO, or DialogResult.CANCEL

**show_yes_no_cancel(parent, title, message) -> DialogResult**
- Shows dialog with Yes, No, and Cancel buttons
- Returns: DialogResult.YES, DialogResult.NO, or DialogResult.CANCEL

**show_info(parent, title, message) -> DialogResult**
- Shows informational dialog with OK button (blue icon)
- Returns: DialogResult.OK

**show_warning(parent, title, message) -> DialogResult**
- Shows warning dialog with OK button (orange icon)
- Returns: DialogResult.OK

**show_error(parent, title, message) -> DialogResult**
- Shows error dialog with OK button (red icon)
- Returns: DialogResult.OK

**Examples:**
```python
from app.ui.components import StandardWarningDialog, DialogResult

# Simple information message
StandardWarningDialog.show_info(
    self, 
    "Success", 
    "Operation completed successfully!"
)

# Warning message
StandardWarningDialog.show_warning(
    self,
    "Warning",
    "This action cannot be undone. Proceed with caution."
)

# Error message
StandardWarningDialog.show_error(
    self,
    "Error",
    "Failed to load document. Please check the file path."
)

# Yes/No confirmation
result = StandardWarningDialog.show_yes_no(
    self,
    "Confirm Delete",
    "Are you sure you want to delete this item?"
)
if result == DialogResult.YES:
    delete_item()
elif result == DialogResult.NO:
    print("Delete cancelled")

# Yes/No/Cancel (for "Save changes?" scenarios)
result = StandardWarningDialog.show_yes_no_cancel(
    self,
    "Save Changes",
    "Do you want to save your changes before closing?"
)
if result == DialogResult.YES:
    save_changes()
    close_window()
elif result == DialogResult.NO:
    discard_changes()
    close_window()
else:  # CANCEL
    # Stay on current page, don't close
    return

# Check result
if result == DialogResult.OK:
    proceed()
elif result == DialogResult.CANCEL:
    abort()
```

---

## 🎨 Design System

### Color Palette

**Button Colors:**
- PRIMARY: #0078d4 (Blue)
- SECONDARY: #6c757d (Gray)
- SUCCESS: #28a745 (Green)
- DANGER: #dc3545 (Red)
- WARNING: #ffc107 (Orange)
- INFO: #17a2b8 (Light Blue)

**Text Colors:**
- Black: #000000 (TITLE, SECTION, LABEL)
- Dark Gray: #333333 (SUBSECTION)
- Gray: #666666 (STATUS)
- Light Gray: #888888 (NOTES)

**Border Colors:**
- Default: #cccccc
- Focus/Hover: #0078d4
- Inactive: #999999

### Typography Scale

| Style | Size | Weight | Color | Line Height |
|-------|------|--------|-------|-------------|
| TITLE | 14pt | Bold | Black | Auto |
| SECTION | 12pt | Bold | Black | Auto |
| SUBSECTION | 11pt | Bold | Dark Gray | Auto |
| LABEL | 10pt | Normal | Black | Auto |
| NOTES | 9pt | Normal Italic | Light Gray | Auto |
| STATUS | 10pt | Normal | Gray | Auto |

### Spacing Standards

**Component Heights:**
- Button Full: 36px
- Button Compact: 24px
- Input: 30px
- ComboBox: 30px
- Drop Area: 80px minimum

**Component Widths:**
- Button Half: 150px
- Button Compact: 100px
- Input Standard: 200px min
- ComboBox Single: 200px
- ComboBox Double: 400px

**Padding:**
- Button: 6px 16px
- Input: 4px 8px
- ComboBox: 4px 8px

---

## 🔧 Configuration

### Modifying Constants

Edit `constants.py` to adjust global sizes:

```python
COMPONENT_SIZES = {
    "button_full_height": 36,      # Change to 40 for taller buttons
    "button_half_width": 150,      # Change to 180 for wider buttons
    "combo_single_width": 200,     # Change to 220 for wider combos
    # ... etc
}
```

### Modifying Colors

Edit `constants.py` to adjust button colors:

```python
BUTTON_COLORS = {
    ButtonRole.PRIMARY: {
        "background": "#0078d4",   # Change to your brand color
        "hover": "#106ebe",        # Darker shade
        "pressed": "#005a9e",      # Even darker
        # ... etc
    }
}
```

### Modifying Typography

Edit `label.py` STYLE_CONFIG to adjust text styles:

```python
STYLE_CONFIG = {
    TextStyle.TITLE: {
        "font_size": "14pt",       # Change to "16pt" for larger titles
        "font_weight": "bold",
        "color": "#000000",
    }
}
```

---

## 📖 Usage Guidelines

### When to Use Each Component

**StandardButton:**
- ✅ Any clickable action
- ✅ Form submissions
- ✅ Toolbar actions
- ❌ Links (use QLabel with link styling)
- ❌ Tabs (use QTabWidget)

**StandardLabel:**
- ✅ Form labels
- ✅ Section headers
- ✅ Status messages
- ✅ Helper text
- ❌ Clickable text (use QPushButton)
- ❌ Editable text (use StandardInput)

**StandardComboBox:**
- ✅ Selection from list
- ✅ Version selectors
- ✅ Document pickers
- ❌ Multi-select (use QListWidget)
- ❌ Very long lists (consider search)

**StandardInput:**
- ✅ Text entry
- ✅ Search boxes
- ✅ File paths
- ✅ IDs/codes
- ❌ Large text (use QTextEdit)
- ❌ Numbers only (consider QSpinBox)

**StandardDropArea:**
- ✅ File uploads
- ✅ Document imports
- ✅ Data loading
- ❌ Text drag-drop
- ❌ Non-file content

### Role Selection Guide

**Choose button role based on action purpose:**

| Action Type | Role | Examples |
|-------------|------|----------|
| Main action | PRIMARY | Save, Submit, Compare, Search |
| Alternative action | SECONDARY | Cancel, Close, Back |
| Positive change | SUCCESS | Apply, Confirm, Accept |
| Destructive | DANGER | Delete, Remove, Clear |
| Reversible change | WARNING | Reset, Revert, Undo |
| Non-critical | INFO | Export, Help, Learn More |

**Don't choose based on color preference!**
- ❌ Bad: "I like blue, use PRIMARY"
- ✅ Good: "This is the main action, use PRIMARY"

---

## ⚠️ Common Mistakes

### 1. Forgetting Tuple Comma

```python
# ❌ Wrong - not a tuple!
drop = StandardDropArea(allowed_extensions=('.csv'))

# ✅ Correct - tuple requires comma
drop = StandardDropArea(allowed_extensions=('.csv',))
```

### 2. Using setStyleSheet After Creation

```python
# ❌ Wrong - breaks component styling
btn = StandardButton("Save", role=ButtonRole.PRIMARY)
btn.setStyleSheet("background: red;")

# ✅ Correct - use appropriate role
btn = StandardButton("Save", role=ButtonRole.DANGER)
```

### 3. Manual Resizing

```python
# ❌ Wrong - defeats the purpose
btn = StandardButton("Save")
btn.setFixedSize(200, 50)

# ✅ Correct - use size variant
btn = StandardButton("Save", size=ButtonSize.HALF_WIDTH)
```

### 4. Wrong Label Color Method

```python
# ❌ Wrong - overrides all styling
label = StandardLabel("Status", style=TextStyle.STATUS)
label.setStyleSheet("color: green;")

# ✅ Correct - use set_color()
label = StandardLabel("Status", style=TextStyle.STATUS)
label.set_color("green")
```

### 5. Inconsistent Sizing

```python
# ❌ Wrong - manual width defeats consistency
combo1 = QComboBox()
combo1.setFixedWidth(205)  # Close but not standard

# ✅ Correct - use standard size
combo1 = StandardComboBox(size=ComboSize.SINGLE)  # Always 200px
```

---

## 🔍 Troubleshooting

### Button too wide/narrow
**Problem:** Button stretches to fill space
**Solution:** Use `ButtonSize.HALF_WIDTH` or `COMPACT`

### Label color not changing
**Problem:** `setStyleSheet()` doesn't work
**Solution:** Use `label.set_color("green")` method

### ComboBox cuts off text
**Problem:** Dropdown too narrow
**Solution:** Use `ComboSize.DOUBLE` or `FULL`

### Drop area accepts all files
**Problem:** File validation not working
**Solution:** Ensure tuple: `('.csv',)` not `('.csv')`

### Import error
**Problem:** Can't find component
**Solution:** Import from package: `from app.ui.components import StandardButton`

---

## 📚 Additional Resources

**Related Documentation:**
- `/docs/COMPONENT_LIBRARY.md` - Detailed guide for developers
- `/docs/COMPONENT_QUICK_REF.md` - Quick syntax reference
- `/docs/MIGRATION_CHECKLIST.md` - Migration from old code

**Example Implementation:**
- `app/document_scanner/CompareVersions/view.py` - Real usage example

**Source Files:**
- `app/ui/components/*.py` - Component implementations

---

## 🎯 Summary

**What This Library Provides:**
- ✅ Consistent styling across entire application
- ✅ Role-based semantic coloring
- ✅ Standard sizes (no guessing)
- ✅ Type-safe enums (IDE autocomplete)
- ✅ Minimal code (1 line vs 15+ lines)
- ✅ Easy maintenance (change once, apply everywhere)

**What You Should Do:**
- ✅ Use these components for all new UI
- ✅ Choose roles based on action purpose
- ✅ Use standard sizes when possible
- ✅ Follow the guidelines in this document
- ✅ Ask questions if unsure

**What You Should NOT Do:**
- ❌ Use `setStyleSheet()` on components
- ❌ Manually size standard components
- ❌ Choose roles based on color preference
- ❌ Mix old and new patterns in same view
- ❌ Create custom versions "just because"

---

**Questions?** Check the docs or ask the team!
