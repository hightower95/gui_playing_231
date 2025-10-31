# UI Component Library

## Overview

The standardized UI component library provides consistent, reusable components with unified styling across the entire application. All components follow the application's design system and eliminate the need for inline `setStyleSheet()` calls.

## Quick Start

```python
from app.ui.components import (
    StandardButton, ButtonRole, ButtonSize,
    StandardLabel, TextStyle,
    StandardComboBox, ComboSize,
    StandardInput,
    StandardDropArea,
    create_button_row,
    create_form_row
)

# Before (old way)
btn = QPushButton("Save")
btn.setStyleSheet("background-color: #0078d4; color: white; padding: 6px 16px; ...")
btn.clicked.connect(self.save)

# After (new way)
btn = StandardButton("Save", role=ButtonRole.PRIMARY)
btn.clicked.connect(self.save)
```

## Component Reference

### StandardButton

Standardized buttons with role-based coloring and size variants.

**Roles:**
- `ButtonRole.PRIMARY` - Main actions (blue)
- `ButtonRole.SECONDARY` - Secondary actions (gray)
- `ButtonRole.SUCCESS` - Positive actions (green)
- `ButtonRole.DANGER` - Destructive actions (red)
- `ButtonRole.WARNING` - Warning actions (orange)
- `ButtonRole.INFO` - Informational (light blue)

**Sizes:**
- `ButtonSize.FULL` - Full width/height (default)
- `ButtonSize.HALF_WIDTH` - 150px width
- `ButtonSize.HALF_HEIGHT` - 24px height (compact)
- `ButtonSize.COMPACT` - Both half (100px × 24px)

**Examples:**

```python
# Primary button (full size)
save_btn = StandardButton("Save", role=ButtonRole.PRIMARY)

# Danger button (half width)
delete_btn = StandardButton("Delete", role=ButtonRole.DANGER, size=ButtonSize.HALF_WIDTH)

# Button with icon
search_btn = StandardButton("Search", icon="🔍", role=ButtonRole.PRIMARY)

# Compact secondary button
close_btn = StandardButton("Close", role=ButtonRole.SECONDARY, size=ButtonSize.COMPACT)

# Connect to slot as usual
save_btn.clicked.connect(self.on_save)
```

**Visual Guide:**
```
PRIMARY    [   Save Document   ]    Blue background, white text
SECONDARY  [      Cancel       ]    Gray background, white text  
SUCCESS    [      Apply        ]    Green background, white text
DANGER     [      Delete       ]    Red background, white text
WARNING    [      Revert       ]    Orange background, dark text
INFO       [       Help        ]    Light blue background, white text
```

---

### StandardLabel

Standardized text labels with consistent styling.

**Styles:**
- `TextStyle.TITLE` - 14pt bold - Main page titles
- `TextStyle.SECTION` - 12pt bold - Section headers
- `TextStyle.SUBSECTION` - 11pt bold - Subsection headers
- `TextStyle.LABEL` - 10pt normal - Standard labels
- `TextStyle.NOTES` - 9pt italic gray - Helper text
- `TextStyle.STATUS` - 10pt normal gray - Status messages

**Examples:**

```python
# Title label
title = StandardLabel("Compare Versions", style=TextStyle.TITLE)

# Section header
section = StandardLabel("Configuration Options", style=TextStyle.SECTION)

# Helper notes
notes = StandardLabel("This field is optional", style=TextStyle.NOTES)

# Status label with dynamic color
status = StandardLabel("Ready", style=TextStyle.STATUS)
status.set_color("green")  # Change to green
status.setText("Processing...")
status.set_color("#ff9800")  # Change to orange

# Custom color override
error_label = StandardLabel("Error occurred", style=TextStyle.LABEL, color="#ff0000")
```

**Visual Guide:**
```
TITLE       Compare Versions              (14pt bold, black)
SECTION     Configuration Options         (12pt bold, black)
SUBSECTION  Advanced Settings             (11pt bold, dark gray)
LABEL       Document Name:                (10pt normal, black)
NOTES       This field is optional        (9pt italic, light gray)
STATUS      Processing: 45%               (10pt normal, gray)
```

---

### StandardComboBox

Standardized dropdown with consistent sizing.

**Sizes:**
- `ComboSize.SINGLE` - 200px width (standard dropdown)
- `ComboSize.DOUBLE` - 400px width (wide dropdown)
- `ComboSize.FULL` - Full available width

**Examples:**

```python
# Single width combo
version_combo = StandardComboBox(size=ComboSize.SINGLE)

# With items
document_combo = StandardComboBox(
    size=ComboSize.DOUBLE,
    items=["Document A", "Document B", "Document C"]
)

# Full width
full_combo = StandardComboBox(size=ComboSize.FULL)

# Add items after creation
version_combo.addItems(["v1.0", "v2.0", "v3.0"])

# Connect to signal
version_combo.currentTextChanged.connect(self.on_version_changed)

# Get current selection
selected = version_combo.currentText()
```

**Visual Guide:**
```
SINGLE:  [Select Version ▼]                    (200px)
DOUBLE:  [Select Document Name ▼]              (400px)  
FULL:    [Select Configuration Option ▼]       (stretches to fill)
```

---

### StandardInput

Standardized text input box.

**Examples:**

```python
# Standard input with placeholder
search_input = StandardInput(placeholder="Enter search term...")

# Custom width
path_input = StandardInput(placeholder="File path...", width=400)

# No placeholder
name_input = StandardInput()

# Connect to signals
search_input.textChanged.connect(self.on_search_text_changed)
search_input.returnPressed.connect(self.perform_search)

# Get/set text
search_input.setText("query text")
text = search_input.text()
```

**Visual Guide:**
```
Standard:  [Enter search term...          ]    (200px min, 30px height)
Wide:      [Enter file path...                      ]    (400px, 30px height)
```

---

### StandardDropArea

Standardized drag-and-drop area for file uploads.

**Features:**
- Visual feedback on hover/drag
- File extension validation
- Clear/reset functionality
- Automatic filename display

**Examples:**

```python
# CSV drop area
csv_drop = StandardDropArea(
    label_text="Drag & Drop CSV file here",
    allowed_extensions=('.csv',)
)

# Multiple extensions
data_drop = StandardDropArea(
    label_text="Drag & Drop data file",
    allowed_extensions=('.csv', '.xlsx', '.xls')
)

# Connect to signal
csv_drop.file_dropped.connect(self.on_file_selected)

# Get dropped file path
file_path = csv_drop.get_file_path()

# Clear the drop area
csv_drop.clear()

def on_file_selected(self, file_path: str):
    print(f"File selected: {file_path}")
    # Process file...
```

**Visual States:**
```
Default:   ┌─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┐
           │  Drag & Drop CSV file here  │    (Gray dashed border)
           └─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┘

Hover:     ┌─────────────────────────────┐
           │  Drag & Drop CSV file here  │    (Darker, solid hover)
           └─────────────────────────────┘

Active:    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
           ┃  Drag & Drop CSV file here  ┃    (Blue border, blue background)
           ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

File Set:  ┌─────────────────────────────┐
           │    ✓ File Selected:         │    (Shows filename)
           │       data_export.csv       │
           └─────────────────────────────┘
```

---

## Helper Functions

### create_button_row

Creates a horizontal row of buttons with optional stretch.

```python
# Buttons with stretch after (left-aligned)
button_row = create_button_row(
    StandardButton("Save", role=ButtonRole.PRIMARY),
    StandardButton("Cancel", role=ButtonRole.SECONDARY),
    stretch_after=1  # Stretch after second button
)

# Buttons with no stretch (fills available space)
button_row = create_button_row(
    StandardButton("Apply", role=ButtonRole.SUCCESS),
    StandardButton("Reset", role=ButtonRole.WARNING),
    StandardButton("Close", role=ButtonRole.SECONDARY),
    stretch_after=-1  # No stretch (buttons space evenly)
)

layout.addWidget(button_row)
```

**Visual Guide:**
```
stretch_after=1:
[Save] [Cancel]                                (left-aligned)

stretch_after=-1:
                              [Apply] [Reset] [Close]  (right-aligned)
```

---

### create_form_row

Creates a form row with aligned label and input widget.

```python
# With input
name_row = create_form_row(
    "Name:",
    StandardInput(placeholder="Enter name")
)

# With combo box
version_row = create_form_row(
    "Version:",
    StandardComboBox(size=ComboSize.SINGLE, items=["v1.0", "v2.0"])
)

# Custom label width for alignment
document_row = create_form_row(
    "Document Name:",
    StandardComboBox(size=ComboSize.DOUBLE),
    label_width=150  # Wider label for longer text
)

layout.addWidget(name_row)
layout.addWidget(version_row)
layout.addWidget(document_row)
```

**Visual Guide:**
```
Name:          [Enter name...              ]
Version:       [v1.0           ▼]
Document Name: [Select Document ▼]
```

---

## Migration Guide

### Pattern 1: Simple Button

**Before:**
```python
self.save_button = QPushButton("Save")
self.save_button.setStyleSheet("""
    QPushButton {
        background-color: #0078d4;
        color: white;
        padding: 6px 16px;
        font-size: 11pt;
        font-weight: bold;
        border: none;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #106ebe;
    }
""")
self.save_button.clicked.connect(self.save)
layout.addWidget(self.save_button)
```

**After:**
```python
self.save_button = StandardButton("Save", role=ButtonRole.PRIMARY)
self.save_button.clicked.connect(self.save)
layout.addWidget(self.save_button)
```

---

### Pattern 2: Labels and Text

**Before:**
```python
title = QLabel("Configuration")
title.setStyleSheet("font-size: 14pt; font-weight: bold;")

notes = QLabel("This is optional")
notes.setStyleSheet("font-size: 9pt; color: gray; font-style: italic;")

layout.addWidget(title)
layout.addWidget(notes)
```

**After:**
```python
title = StandardLabel("Configuration", style=TextStyle.TITLE)
notes = StandardLabel("This is optional", style=TextStyle.NOTES)

layout.addWidget(title)
layout.addWidget(notes)
```

---

### Pattern 3: ComboBox

**Before:**
```python
self.version_combo = QComboBox()
self.version_combo.setFixedWidth(200)
self.version_combo.setStyleSheet("""
    QComboBox {
        padding: 4px 8px;
        border: 1px solid #ccc;
        border-radius: 3px;
    }
""")
self.version_combo.addItems(["v1.0", "v2.0"])
layout.addWidget(self.version_combo)
```

**After:**
```python
self.version_combo = StandardComboBox(
    size=ComboSize.SINGLE,
    items=["v1.0", "v2.0"]
)
layout.addWidget(self.version_combo)
```

---

### Pattern 4: Drag-Drop Area

**Before:**
```python
class DropArea(QFrame):
    file_dropped = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setMinimumHeight(80)
        self.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border: 2px dashed #999;
                border-radius: 5px;
            }
        """)
        # ... 50 more lines of drag/drop logic ...
```

**After:**
```python
self.drop_area = StandardDropArea(
    label_text="Drag & Drop CSV file",
    allowed_extensions=('.csv',)
)
self.drop_area.file_dropped.connect(self.on_file_selected)
layout.addWidget(self.drop_area)
```

---

### Pattern 5: Button Row

**Before:**
```python
button_container = QWidget()
button_layout = QHBoxLayout(button_container)
button_layout.addStretch()

save_btn = QPushButton("Save")
save_btn.setStyleSheet("background-color: #0078d4; color: white; ...")

cancel_btn = QPushButton("Cancel")
cancel_btn.setStyleSheet("background-color: #6c757d; color: white; ...")

button_layout.addWidget(save_btn)
button_layout.addWidget(cancel_btn)

layout.addWidget(button_container)
```

**After:**
```python
button_row = create_button_row(
    StandardButton("Save", role=ButtonRole.PRIMARY),
    StandardButton("Cancel", role=ButtonRole.SECONDARY),
    stretch_after=1
)
layout.addWidget(button_row)
```

---

## Complete Example

Here's a complete example showing how to build a configuration dialog using the component library:

```python
from PySide6.QtWidgets import QDialog, QVBoxLayout, QWidget
from app.ui.components import (
    StandardButton, ButtonRole, ButtonSize,
    StandardLabel, TextStyle,
    StandardComboBox, ComboSize,
    StandardInput,
    StandardDropArea,
    create_button_row,
    create_form_row
)

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration")
        self.setMinimumWidth(600)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = StandardLabel("Document Configuration", style=TextStyle.TITLE)
        layout.addWidget(title)
        
        # Section header
        section = StandardLabel("Basic Settings", style=TextStyle.SECTION)
        layout.addWidget(section)
        
        # Form rows
        name_row = create_form_row(
            "Name:",
            StandardInput(placeholder="Enter document name")
        )
        layout.addWidget(name_row)
        
        version_row = create_form_row(
            "Version:",
            StandardComboBox(size=ComboSize.SINGLE, items=["v1.0", "v2.0", "v3.0"])
        )
        layout.addWidget(version_row)
        
        # Notes
        notes = StandardLabel(
            "Select the version to compare against",
            style=TextStyle.NOTES
        )
        layout.addWidget(notes)
        
        # Section
        section2 = StandardLabel("File Upload", style=TextStyle.SECTION)
        layout.addWidget(section2)
        
        # Drop area
        self.drop_area = StandardDropArea(
            label_text="Drag & Drop CSV file",
            allowed_extensions=('.csv',)
        )
        self.drop_area.file_dropped.connect(self.on_file_selected)
        layout.addWidget(self.drop_area)
        
        # Status label
        self.status_label = StandardLabel("Ready", style=TextStyle.STATUS)
        layout.addWidget(self.status_label)
        
        # Buttons
        button_row = create_button_row(
            StandardButton("Save", role=ButtonRole.PRIMARY),
            StandardButton("Reset", role=ButtonRole.WARNING, size=ButtonSize.HALF_WIDTH),
            StandardButton("Cancel", role=ButtonRole.SECONDARY),
            stretch_after=0
        )
        layout.addWidget(button_row)
        
    def on_file_selected(self, file_path: str):
        self.status_label.setText(f"File selected: {file_path}")
        self.status_label.set_color("green")
```

---

## Design System Reference

### Color Palette

**Primary Actions:**
- `#0078d4` - Primary button background
- `#106ebe` - Primary button hover
- `#005a9e` - Primary button pressed

**Secondary Actions:**
- `#6c757d` - Secondary button background
- `#5a6268` - Secondary button hover

**Status Colors:**
- `#28a745` - Success (green)
- `#dc3545` - Danger (red)
- `#ffc107` - Warning (orange)
- `#17a2b8` - Info (light blue)

**Text Colors:**
- `#000000` - Primary text
- `#333333` - Secondary text
- `#666666` - Tertiary text
- `#888888` - Helper text

**Border Colors:**
- `#cccccc` - Standard borders
- `#0078d4` - Focus/hover borders
- `#999999` - Inactive borders

---

### Typography Scale

| Style       | Size | Weight | Use Case              |
|-------------|------|--------|-----------------------|
| TITLE       | 14pt | Bold   | Page titles           |
| SECTION     | 12pt | Bold   | Section headers       |
| SUBSECTION  | 11pt | Bold   | Subsection headers    |
| LABEL       | 10pt | Normal | Form labels           |
| NOTES       | 9pt  | Normal | Helper text           |
| STATUS      | 10pt | Normal | Status messages       |

---

### Spacing Standards

| Element          | Height | Width  | Padding    |
|------------------|--------|--------|------------|
| Button (full)    | 36px   | Auto   | 6px 16px   |
| Button (compact) | 24px   | 100px  | 4px 12px   |
| Input            | 30px   | 200px+ | 4px 8px    |
| ComboBox         | 30px   | Varies | 4px 8px    |
| Drop Area        | 80px+  | Auto   | 10px       |

---

## Best Practices

### 1. Use Role-Based Button Styling

```python
# ✅ Good - Clear intent
save_btn = StandardButton("Save", role=ButtonRole.PRIMARY)
delete_btn = StandardButton("Delete", role=ButtonRole.DANGER)

# ❌ Bad - Custom colors defeat the purpose
btn = StandardButton("Save")
btn.setStyleSheet("background-color: #ff0000;")  # Don't do this!
```

### 2. Consistent Sizing

```python
# ✅ Good - Use size variants
compact_btn = StandardButton("X", role=ButtonRole.SECONDARY, size=ButtonSize.COMPACT)

# ❌ Bad - Manual sizing
btn = StandardButton("X")
btn.setFixedSize(50, 20)  # Don't do this!
```

### 3. Semantic Text Styles

```python
# ✅ Good - Semantic styles
title = StandardLabel("Configuration", style=TextStyle.TITLE)
helper = StandardLabel("Optional field", style=TextStyle.NOTES)

# ❌ Bad - Manual styling
label = QLabel("Configuration")
label.setStyleSheet("font-size: 14pt; font-weight: bold;")  # Don't do this!
```

### 4. Use Helper Functions

```python
# ✅ Good - Use helpers for common patterns
button_row = create_button_row(save_btn, cancel_btn, stretch_after=1)
form_row = create_form_row("Name:", name_input)

# ❌ Bad - Manual layout every time
container = QWidget()
layout = QHBoxLayout(container)
layout.addStretch()
layout.addWidget(save_btn)
layout.addWidget(cancel_btn)
```

---

## Troubleshooting

### Issue: Button too wide/narrow

**Solution:** Use size variants or let it stretch in layout
```python
# Compact button
btn = StandardButton("OK", size=ButtonSize.COMPACT)

# Or let layout control width
btn = StandardButton("OK")  # Will stretch to fill space
```

### Issue: Label color not changing

**Solution:** Use `set_color()` method for dynamic colors
```python
status = StandardLabel("Status", style=TextStyle.STATUS)
status.set_color("green")  # ✅ Correct
status.setStyleSheet("color: green;")  # ❌ Wrong - overrides all styling
```

### Issue: ComboBox too wide

**Solution:** Use appropriate size variant
```python
combo = StandardComboBox(size=ComboSize.SINGLE)  # 200px
# Not: combo = StandardComboBox(size=ComboSize.DOUBLE)  # 400px
```

### Issue: Drop area not validating files

**Solution:** Check allowed_extensions parameter
```python
drop = StandardDropArea(
    label_text="Drop CSV",
    allowed_extensions=('.csv',)  # Note the comma! Tuple required
)
```

---

## Migration Checklist

When refactoring existing views to use the component library:

- [ ] Replace `QPushButton` with `StandardButton` + role
- [ ] Replace `QLabel` styling with `StandardLabel` + style
- [ ] Replace `QComboBox` sizing with `StandardComboBox` + size
- [ ] Replace `QLineEdit` with `StandardInput`
- [ ] Replace custom drag-drop with `StandardDropArea`
- [ ] Use `create_button_row()` for button layouts
- [ ] Use `create_form_row()` for form layouts
- [ ] Remove all `setStyleSheet()` calls
- [ ] Test visual consistency across views
- [ ] Update any custom color logic to use `set_color()`

---

## Support

For questions or issues with the component library:
1. Check this documentation first
2. Review the examples in `app/ui/components.py`
3. Look at migrated views (e.g., `CompareVersions/view.py`)
4. Ask the team for help

**Remember:** The goal is consistency, not perfection. Migrate gradually and test thoroughly!
