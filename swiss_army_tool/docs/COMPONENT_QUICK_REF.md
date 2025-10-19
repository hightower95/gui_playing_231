# Component Library Quick Reference

## 🚀 Quick Start

```python
from app.ui.components import (
    StandardButton, ButtonRole, ButtonSize,
    StandardLabel, TextStyle,
    StandardComboBox, ComboSize,
    StandardInput,
    StandardDropArea
)
```

---

## 📋 Buttons

```python
# Primary action (blue)
StandardButton("Save", role=ButtonRole.PRIMARY)

# Secondary action (gray)
StandardButton("Cancel", role=ButtonRole.SECONDARY)

# Success action (green)
StandardButton("Apply", role=ButtonRole.SUCCESS)

# Danger action (red)
StandardButton("Delete", role=ButtonRole.DANGER)

# Warning action (orange)
StandardButton("Reset", role=ButtonRole.WARNING)

# Info action (light blue)
StandardButton("Export", role=ButtonRole.INFO)

# Size variants
StandardButton("OK", size=ButtonSize.HALF_WIDTH)      # 150px wide
StandardButton("OK", size=ButtonSize.HALF_HEIGHT)     # 24px tall
StandardButton("OK", size=ButtonSize.COMPACT)         # 100×24px
```

---

## 📝 Labels

```python
# Title (14pt bold) - Page titles
StandardLabel("Document Scanner", style=TextStyle.TITLE)

# Section (12pt bold) - Section headers
StandardLabel("Configuration", style=TextStyle.SECTION)

# Subsection (11pt bold) - Subsections
StandardLabel("Advanced Settings", style=TextStyle.SUBSECTION)

# Label (10pt) - Form labels
StandardLabel("Name:", style=TextStyle.LABEL)

# Notes (9pt gray italic) - Helper text
StandardLabel("This is optional", style=TextStyle.NOTES)

# Status (10pt gray) - Status messages
status = StandardLabel("Ready", style=TextStyle.STATUS)
status.set_color("green")  # Change color dynamically
```

---

## 📦 Dropdowns

```python
# Single width (200px)
StandardComboBox(size=ComboSize.SINGLE)

# Double width (400px)
StandardComboBox(size=ComboSize.DOUBLE)

# Full width (stretches)
StandardComboBox(size=ComboSize.FULL)

# With items
StandardComboBox(
    size=ComboSize.SINGLE,
    items=["Option 1", "Option 2", "Option 3"]
)
```

---

## ✏️ Inputs

```python
# Standard input
StandardInput(placeholder="Enter text...")

# Custom width
StandardInput(placeholder="File path...", width=400)

# No placeholder
StandardInput()
```

---

## 📥 Drag & Drop

```python
# CSV files only
drop = StandardDropArea(
    label_text="Drag & Drop CSV file",
    allowed_extensions=('.csv',)
)
drop.file_dropped.connect(on_file_selected)

# Multiple extensions
drop = StandardDropArea(
    label_text="Drag & Drop data file",
    allowed_extensions=('.csv', '.xlsx', '.xls')
)

# Get file path
file_path = drop.get_file_path()

# Clear drop area
drop.clear()
```

---

## 🎨 Color Reference

### Button Colors

| Role | Background | Use For |
|------|------------|---------|
| PRIMARY | #0078d4 (Blue) | Main actions |
| SECONDARY | #6c757d (Gray) | Cancel, Close |
| SUCCESS | #28a745 (Green) | Apply, Confirm |
| DANGER | #dc3545 (Red) | Delete, Remove |
| WARNING | #ffc107 (Orange) | Reset, Revert |
| INFO | #17a2b8 (Light Blue) | Help, Export |

### Text Colors

- Black `#000000` - Primary text (TITLE, SECTION, LABEL)
- Dark Gray `#333333` - Secondary text (SUBSECTION)
- Gray `#666666` - Tertiary text (STATUS)
- Light Gray `#888888` - Helper text (NOTES)

---

## 📐 Size Reference

### Buttons
- **Full:** Auto width × 36px height
- **Half Width:** 150px × 36px
- **Half Height:** Auto width × 24px
- **Compact:** 100px × 24px

### Inputs & Combos
- **Height:** 30px (standard)
- **ComboBox Single:** 200px width
- **ComboBox Double:** 400px width
- **Input Standard:** 200px min width

### Drop Area
- **Min Height:** 80px
- **Width:** Stretches to fill

---

## 🔄 Before & After

### Button
```python
# ❌ Before
btn = QPushButton("Save")
btn.setStyleSheet("""
    QPushButton {
        background-color: #0078d4;
        color: white;
        padding: 6px 16px;
        font-size: 11pt;
        font-weight: bold;
        border: none;
        border-radius: 4px;
    }
""")

# ✅ After
btn = StandardButton("Save", role=ButtonRole.PRIMARY)
```

### Label
```python
# ❌ Before
title = QLabel("Configuration")
title.setStyleSheet("font-size: 14pt; font-weight: bold;")

# ✅ After
title = StandardLabel("Configuration", style=TextStyle.TITLE)
```

### ComboBox
```python
# ❌ Before
combo = QComboBox()
combo.setFixedWidth(200)
combo.setStyleSheet("padding: 4px 8px; border: 1px solid #ccc; ...")

# ✅ After
combo = StandardComboBox(size=ComboSize.SINGLE)
```

### Drag-Drop
```python
# ❌ Before
class CustomDropArea(QFrame):
    file_dropped = Signal(str)
    # ... 50+ lines of code ...

# ✅ After  
drop = StandardDropArea(
    label_text="Drag & Drop CSV",
    allowed_extensions=('.csv',)
)
```

---

## 🎯 Common Patterns

### Page Header with Action
```python
header = QHBoxLayout()
header.addWidget(StandardLabel("Page Title", style=TextStyle.TITLE))
header.addStretch()
header.addWidget(StandardButton("Action", role=ButtonRole.PRIMARY))
```

### Section with Status
```python
section = QHBoxLayout()
section.addWidget(StandardLabel("Results", style=TextStyle.SECTION))
section.addStretch()
status = StandardLabel("Ready", style=TextStyle.STATUS)
section.addWidget(status)

# Update status later
status.setText("Processing...")
status.set_color("orange")
```

### Form Row
```python
from app.ui.components import create_form_row

row = create_form_row(
    "Name:",
    StandardInput(placeholder="Enter name")
)
layout.addWidget(row)
```

### Button Row (Right-Aligned)
```python
from app.ui.components import create_button_row

buttons = create_button_row(
    StandardButton("Save", role=ButtonRole.PRIMARY),
    StandardButton("Cancel", role=ButtonRole.SECONDARY),
    stretch_after=0  # Stretch before buttons
)
layout.addWidget(buttons)
```

---

## ⚠️ Common Mistakes

### ❌ Don't use setStyleSheet after creation
```python
btn = StandardButton("Save", role=ButtonRole.PRIMARY)
btn.setStyleSheet("background: red;")  # BREAKS STYLING!
```

### ❌ Don't manually resize standard components
```python
btn = StandardButton("Save")
btn.setFixedSize(100, 50)  # Use ButtonSize instead!
```

### ❌ Don't forget the tuple comma
```python
# Wrong - not a tuple!
drop = StandardDropArea(allowed_extensions=('.csv'))

# Correct - tuple with comma
drop = StandardDropArea(allowed_extensions=('.csv',))
```

### ✅ Do use set_color() for dynamic colors
```python
label = StandardLabel("Status", style=TextStyle.STATUS)
label.set_color("green")  # CORRECT
```

---

## 📚 Full Documentation

- **Complete Guide:** `docs/COMPONENT_LIBRARY.md`
- **Migration Guide:** `docs/MIGRATION_CHECKLIST.md`
- **Source Code:** `app/ui/components.py`
- **Example View:** `app/document_scanner/CompareVersions/view.py`

---

## 🆘 Need Help?

1. Check `docs/COMPONENT_LIBRARY.md` for detailed examples
2. Look at `CompareVersions/view.py` for real usage
3. Search for similar patterns in components.py
4. Ask the team!

---

**🎉 Pro Tip:** Use role-based button coloring instead of thinking about colors. Ask "What is this button's purpose?" not "What color should it be?"
