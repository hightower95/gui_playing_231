# Component Library Migration Checklist

## Overview

This checklist helps migrate existing views to use the standardized UI component library. Follow this process systematically to ensure consistent refactoring.

## Migration Status

### ✅ Completed

- **CompareVersions/view.py** - First view refactored as reference example
  - Removed 90+ lines of custom DropArea class
  - Replaced inline button styling (15 lines → 1 line)
  - Standardized all labels (5 different styles → TextStyle enum)
  - Consistent sizing for ComboBoxes
  - Used role-based button coloring

### 🔄 In Progress

- (None currently)

### ❌ Pending

- CheckMultiple/view.py
- Lookup/view.py  
- Document Scanner main tab
- E3 views
- EPD views
- Connector views
- Configuration views
- All other custom views

---

## Step-by-Step Migration Process

### Phase 1: Preparation

- [ ] **1.1** Read the view file to understand current UI structure
- [ ] **1.2** Identify all UI components:
  - [ ] QPushButtons
  - [ ] QLabels with custom styling
  - [ ] QComboBoxes
  - [ ] QLineEdits
  - [ ] Custom drag-drop areas
  - [ ] Any inline setStyleSheet() calls
- [ ] **1.3** Take note of any custom behaviors or special requirements
- [ ] **1.4** Check if view has any tests that need updating

### Phase 2: Update Imports

- [ ] **2.1** Add component library imports:
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
  ```
- [ ] **2.2** Remove unused imports:
  - [ ] QPushButton (if all replaced)
  - [ ] QLabel (if all replaced)
  - [ ] QComboBox (if all replaced)
  - [ ] QLineEdit (if all replaced)
  - [ ] Any drag-drop related imports (QDragEnterEvent, etc.)

### Phase 3: Replace Components (Priority Order)

#### 3.1 Replace Custom Drag-Drop Areas

**Before:**
```python
class CustomDropArea(QFrame):
    file_dropped = Signal(str)
    # ... 50-100 lines of custom implementation
```

**After:**
```python
self.drop_area = StandardDropArea(
    label_text="Drag & Drop CSV file",
    allowed_extensions=('.csv',)
)
self.drop_area.file_dropped.connect(self.on_file_selected)
```

- [ ] Find custom drag-drop class definition
- [ ] Note the label text and file extensions
- [ ] Replace with StandardDropArea
- [ ] Remove custom class (save 50-100 lines!)
- [ ] Test drag-drop functionality

#### 3.2 Replace Buttons

**Before:**
```python
self.save_btn = QPushButton("Save")
self.save_btn.setStyleSheet("""
    QPushButton {
        background-color: #0078d4;
        color: white;
        padding: 6px 16px;
        ...
    }
""")
```

**After:**
```python
self.save_btn = StandardButton("Save", role=ButtonRole.PRIMARY)
```

**Button Replacement Guide:**

| Current Style | New Role | Notes |
|--------------|----------|-------|
| Blue (#0078d4) | PRIMARY | Main actions |
| Gray | SECONDARY | Cancel, Close |
| Green | SUCCESS | Apply, Confirm |
| Red | DANGER | Delete, Remove |
| Orange | WARNING | Reset, Revert |
| Light Blue | INFO | Help, Export |

- [ ] Identify all QPushButtons
- [ ] For each button:
  - [ ] Determine appropriate role based on action
  - [ ] Choose size variant if needed
  - [ ] Replace with StandardButton
  - [ ] Remove setStyleSheet() calls
- [ ] Test all button functionality

#### 3.3 Replace Labels

**Text Style Mapping:**

| Current | New Style | Use Case |
|---------|-----------|----------|
| font-size: 14pt; font-weight: bold | TextStyle.TITLE | Page titles |
| font-size: 12pt; font-weight: bold | TextStyle.SECTION | Section headers |
| font-size: 11pt; font-weight: bold | TextStyle.SUBSECTION | Subsections |
| font-size: 10pt | TextStyle.LABEL | Form labels |
| font-size: 9pt; color: gray; font-style: italic | TextStyle.NOTES | Helper text |
| color: gray/green/orange | TextStyle.STATUS | Status messages |

**Before:**
```python
title = QLabel("Configuration")
title.setStyleSheet("font-size: 14pt; font-weight: bold;")

notes = QLabel("This is optional")
notes.setStyleSheet("font-size: 9pt; color: gray; font-style: italic;")
```

**After:**
```python
title = StandardLabel("Configuration", style=TextStyle.TITLE)
notes = StandardLabel("This is optional", style=TextStyle.NOTES)
```

- [ ] Identify all QLabels with custom styling
- [ ] For each label:
  - [ ] Determine appropriate TextStyle
  - [ ] Replace with StandardLabel
  - [ ] Remove setStyleSheet() calls
- [ ] For dynamic color labels:
  - [ ] Use `set_color()` method instead of setStyleSheet

#### 3.4 Replace ComboBoxes

**Before:**
```python
self.version_combo = QComboBox()
self.version_combo.setFixedWidth(200)
self.version_combo.setStyleSheet("""
    QComboBox {
        padding: 4px 8px;
        border: 1px solid #ccc;
        ...
    }
""")
```

**After:**
```python
self.version_combo = StandardComboBox(
    size=ComboSize.SINGLE,  # 200px
    items=["v1.0", "v2.0"]
)
```

**Size Selection Guide:**

| Width Needed | ComboSize | Typical Use |
|-------------|-----------|-------------|
| ~200px | SINGLE | Versions, short names |
| ~400px | DOUBLE | Document names, paths |
| Fill available | FULL | Main selectors |

- [ ] Identify all QComboBoxes
- [ ] For each combo:
  - [ ] Determine appropriate size
  - [ ] Replace with StandardComboBox
  - [ ] Remove sizing and styling code
- [ ] Test dropdown functionality

#### 3.5 Replace Input Fields

**Before:**
```python
self.search_input = QLineEdit()
self.search_input.setPlaceholderText("Enter search...")
self.search_input.setFixedHeight(30)
self.search_input.setStyleSheet("...")
```

**After:**
```python
self.search_input = StandardInput(placeholder="Enter search...")
```

- [ ] Identify all QLineEdits
- [ ] For each input:
  - [ ] Note placeholder text
  - [ ] Note any custom width requirements
  - [ ] Replace with StandardInput
  - [ ] Remove styling code
- [ ] Test input functionality

### Phase 4: Refactor Layouts

#### 4.1 Button Rows

**Before:**
```python
button_container = QWidget()
button_layout = QHBoxLayout(button_container)
button_layout.addStretch()
button_layout.addWidget(save_btn)
button_layout.addWidget(cancel_btn)
layout.addWidget(button_container)
```

**After:**
```python
button_row = create_button_row(save_btn, cancel_btn, stretch_after=1)
layout.addWidget(button_row)
```

- [ ] Find button layout patterns
- [ ] Replace with `create_button_row()`
- [ ] Test button alignment

#### 4.2 Form Rows

**Before:**
```python
row = QWidget()
row_layout = QHBoxLayout(row)
label = QLabel("Name:")
label.setFixedWidth(100)
row_layout.addWidget(label)
row_layout.addWidget(name_input)
layout.addWidget(row)
```

**After:**
```python
row = create_form_row("Name:", name_input)
layout.addWidget(row)
```

- [ ] Find form label-input patterns
- [ ] Replace with `create_form_row()`
- [ ] Test form alignment

### Phase 5: Testing

- [ ] **5.1** Visual inspection:
  - [ ] Check all buttons render correctly
  - [ ] Verify label styling is appropriate
  - [ ] Ensure consistent spacing
  - [ ] Test hover states
  - [ ] Verify disabled states
  
- [ ] **5.2** Functional testing:
  - [ ] Test all button clicks
  - [ ] Test dropdown selections
  - [ ] Test input field entry
  - [ ] Test drag-drop if applicable
  - [ ] Test dynamic color changes
  
- [ ] **5.3** Regression testing:
  - [ ] Verify no broken functionality
  - [ ] Check signal connections
  - [ ] Test integration with presenters
  - [ ] Validate data flow

### Phase 6: Cleanup

- [ ] **6.1** Remove unused code:
  - [ ] Custom classes (DropArea, etc.)
  - [ ] Style constants
  - [ ] Helper methods for styling
  
- [ ] **6.2** Update docstrings:
  - [ ] Add note about using standardized components
  - [ ] Reference COMPONENT_LIBRARY.md
  
- [ ] **6.3** Code formatting:
  - [ ] Run formatter
  - [ ] Check for consistent indentation
  - [ ] Remove extra blank lines

### Phase 7: Documentation

- [ ] **7.1** Update view's docstring:
  ```python
  """
  View Name - Description
  
  REFACTORED: Now uses standardized UI components from app.ui.components
  See docs/COMPONENT_LIBRARY.md for component documentation
  """
  ```

- [ ] **7.2** Update migration status in this document

- [ ] **7.3** Note any special cases or lessons learned

---

## Common Patterns

### Pattern 1: Title with Button

```python
# Standardized pattern for header with action button
title_row = QHBoxLayout()
title_row.addWidget(StandardLabel("Page Title", style=TextStyle.TITLE))
title_row.addStretch()
title_row.addWidget(StandardButton("Action", role=ButtonRole.PRIMARY))
layout.addLayout(title_row)
```

### Pattern 2: Section with Status

```python
# Section header with dynamic status
section_row = QHBoxLayout()
section_row.addWidget(StandardLabel("Results", style=TextStyle.SECTION))
section_row.addStretch()
self.status_label = StandardLabel("Ready", style=TextStyle.STATUS)
section_row.addWidget(self.status_label)
layout.addLayout(section_row)

# Later, update status color:
self.status_label.setText("Processing...")
self.status_label.set_color("orange")
```

### Pattern 3: Form with Validation

```python
# Form row with label and input
name_row = create_form_row(
    "Name:",
    StandardInput(placeholder="Enter name")
)
layout.addWidget(name_row)

# Add helper text below
helper = StandardLabel("Must be unique", style=TextStyle.NOTES)
layout.addWidget(helper)
```

### Pattern 4: Action Button Group

```python
# Right-aligned action buttons
button_row = create_button_row(
    StandardButton("Save", role=ButtonRole.PRIMARY),
    StandardButton("Cancel", role=ButtonRole.SECONDARY),
    stretch_after=0  # Stretch before buttons (right-align)
)
layout.addWidget(button_row)
```

---

## Troubleshooting

### Issue: Button too wide

**Symptom:** Button stretches to fill available space

**Solution:** Use size variant
```python
btn = StandardButton("OK", size=ButtonSize.HALF_WIDTH)  # Fixed 150px
```

### Issue: Label color won't change

**Symptom:** `setStyleSheet()` doesn't work after migration

**Solution:** Use `set_color()` method
```python
label = StandardLabel("Status", style=TextStyle.STATUS)
label.set_color("green")  # ✅ Correct
# label.setStyleSheet("color: green;")  # ❌ Wrong
```

### Issue: ComboBox too narrow

**Symptom:** Dropdown cuts off text

**Solution:** Use larger size variant
```python
combo = StandardComboBox(size=ComboSize.DOUBLE)  # 400px instead of 200px
```

### Issue: Drag-drop validation not working

**Symptom:** All files accepted

**Solution:** Check allowed_extensions tuple
```python
drop = StandardDropArea(
    label_text="Drop CSV",
    allowed_extensions=('.csv',)  # Note the comma!
)
```

### Issue: Dynamic colors not showing

**Symptom:** Status label stays same color

**Solution:** Use set_color() not setText()
```python
self.status_label.setText("Error occurred")
self.status_label.set_color("#ff0000")  # Must call both!
```

---

## Code Reduction Examples

### Example 1: CompareVersions/view.py

**Before Migration:**
- Total lines: 486
- Custom DropArea class: 93 lines
- Button styling: 15 lines per button × 3 = 45 lines
- Label styling: ~30 lines
- ComboBox styling: ~20 lines
- **Total styling code: ~188 lines**

**After Migration:**
- Total lines: 398
- DropArea removed: -93 lines
- Buttons: 1 line each × 3 = 3 lines
- Labels: 1 line each
- ComboBoxes: 1 line each
- **Total styling code: ~10 lines**

**Reduction: 88 lines removed (18% smaller file)**

---

## Migration Priority

### High Priority (Do First)
1. ✅ **CompareVersions/view.py** - COMPLETED (reference example)
2. **Document Scanner main tab** - Most visible
3. **Connector tab** - Frequently used
4. **Configuration views** - Good practice ground

### Medium Priority
5. **CheckMultiple/view.py** - Active feature
6. **Lookup/view.py** - Active feature
7. **E3 main views** - Core functionality
8. **EPD main views** - Core functionality

### Low Priority (Gradual)
9. **Dialog classes** - Less visible
10. **Helper views** - Internal use
11. **Legacy views** - Rarely used

---

## Review Checklist

Before marking a view as "migrated", verify:

- [ ] No more `setStyleSheet()` calls on standard widgets
- [ ] No more inline color/size definitions
- [ ] All buttons use ButtonRole
- [ ] All labels use TextStyle
- [ ] Custom DropArea classes removed
- [ ] Helper functions used where appropriate
- [ ] Docstring updated with "REFACTORED" note
- [ ] Visual testing completed
- [ ] Functional testing completed
- [ ] No regression issues
- [ ] Code is cleaner and shorter
- [ ] Migration status updated in this document

---

## Team Guidelines

### When to Migrate

- ✅ **DO migrate** when:
  - Making other changes to a view
  - Fixing UI bugs
  - Adding new UI elements
  - Refactoring code

- ❌ **DON'T migrate** when:
  - View works perfectly and isn't being touched
  - Under tight deadline (do it properly later)
  - Uncertain about component behavior

### How to Migrate

1. **One view at a time** - Don't try to migrate everything at once
2. **Test thoroughly** - Visual and functional testing required
3. **Commit separately** - Each view migration is a separate commit
4. **Document issues** - Note any problems in this document
5. **Ask for help** - If uncertain, check CompareVersions example or ask

### Best Practices

- **Follow the checklist** - Don't skip steps
- **Use appropriate roles** - Think about button meaning
- **Consider size variants** - Don't force standard sizes
- **Preserve functionality** - UI should work exactly the same
- **Keep it simple** - Don't over-engineer

---

## Metrics

Track migration progress:

| Metric | Target | Current |
|--------|--------|---------|
| Views migrated | 30+ | 1 |
| Lines removed | 2000+ | 88 |
| setStyleSheet() calls | 0 | ~50 |
| Custom styling classes | 0 | ~5 |
| Consistency score | 100% | 10% |

---

## Reference

- **Component Documentation:** `docs/COMPONENT_LIBRARY.md`
- **Component Source:** `app/ui/components.py`
- **Example Migration:** `app/document_scanner/CompareVersions/view.py`
- **Config Reference:** `app/core/config.py` (UI_COLORS, UI_STYLES)

---

## Update Log

| Date | View | Migrator | Notes |
|------|------|----------|-------|
| 2024-01-XX | CompareVersions/view.py | GitHub Copilot | First migration, reference example |

---

**Remember:** The goal is consistency and maintainability, not perfection. Migrate gradually and test thoroughly!
