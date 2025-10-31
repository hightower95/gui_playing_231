# Search Context Component Integration

**Date**: October 19, 2025  
**Status**: ✅ Complete - Using Standard Components

---

## 📋 Changes Summary

Updated the Search context display to use **standardized components** from the component library and removed hardcoded white backgrounds in favor of default/transparent backgrounds.

---

## 🔧 Component Updates

### Before (Custom Styling)

```python
# Custom QFrame with white background
frame = QFrame()
frame.setStyleSheet(f"""
    QFrame {{
        background-color: white;
        border: 1px solid {UI_COLORS['frame_border']};
        border-radius: 3px;
        padding: 2px;
    }}
""")

# Custom header button
header = QPushButton()
header.setStyleSheet(f"""
    QPushButton {{
        background: qlineargradient(...);
        color: white;
        border: none;
        padding: 4px 8px;
        ...
    }}
""")
```

### After (Standard Components)

```python
# Using StandardGroupBox from component library
group = StandardGroupBox("Matched Data")
layout = QVBoxLayout()
# Add content...
group.setLayout(layout)

# Context sections also use StandardGroupBox
group = StandardGroupBox(f"{context.context_owner} • '{context.term}'")
```

---

## ✅ Benefits

### 1. **Consistency**
- All context sections use the same StandardGroupBox styling
- Matches the rest of the application's design language
- Consistent borders, padding, and typography

### 2. **Default Backgrounds**
- Removed hardcoded `background-color: white`
- Using `background-color: transparent` in component
- Respects parent widget's background color
- Better integration with overall app theme

### 3. **Maintainability**
- Changes to StandardGroupBox styling automatically apply
- No duplicate style definitions
- Follows component library patterns

### 4. **Simplified Code**
- Fewer lines of custom styling code
- More readable and maintainable
- Easier to understand intent

---

## 🎨 Visual Changes

### Matched Data Section

**Before**: White background QFrame with custom border
```
┌─────────────────────────────┐
│ Matched Data    [white bg]  │
│ ────────────────────────────│
│ Part Number: D38999         │
└─────────────────────────────┘
```

**After**: StandardGroupBox with transparent background
```
┌─────────────────────────────┐
│ Matched Data    [inherit]   │
│ ────────────────────────────│
│ Part Number: D38999         │
└─────────────────────────────┘
```

### Context Sections

**Before**: Custom collapsible with blue gradient header
```
┌─────────────────────────────┐
│ ▼ Connector [blue gradient] │ ← Custom header
├─────────────────────────────┤
│ Content [white bg]          │
└─────────────────────────────┘
```

**After**: StandardGroupBox (native collapsible)
```
┌─────────────────────────────┐
│ Connector • 'D38999'         │ ← StandardGroupBox title
│ ────────────────────────────│
│ Content [transparent]        │
└─────────────────────────────┘
```

---

## 📝 Implementation Details

### Imports Added

```python
from app.ui.components import (
    StandardLabel,
    TextStyle,
    StandardButton,      # Available for future use
    ButtonRole,          # Available for future use
    StandardGroupBox     # Used for context sections
)
```

### Component Usage

#### Matched Data Section
```python
def _create_matched_data_section(self, result: SearchResult):
    """Create matched data display section using StandardGroupBox"""
    group = StandardGroupBox("Matched Data")
    
    layout = QVBoxLayout()
    layout.setContentsMargins(8, 5, 8, 5)
    layout.setSpacing(3)

    # Add data rows with StandardLabel
    for key, value in result.matched_row_data.items():
        row_layout = QHBoxLayout()
        
        key_label = StandardLabel(f"{key}:", style=TextStyle.LABEL)
        key_label.setStyleSheet("font-weight: bold;")
        
        value_label = StandardLabel(str(value), style=TextStyle.LABEL)
        value_label.setWordWrap(True)
        
        row_layout.addWidget(key_label)
        row_layout.addWidget(value_label, 1)
        layout.addLayout(row_layout)

    group.setLayout(layout)
    self.context_layout.addWidget(group)
```

#### Context Sections
```python
def _create_collapsible_context(self, context: Context):
    """Create a collapsible context section using StandardGroupBox"""
    title_text = context.context_owner
    if context.term:
        title_text += f" • '{context.term}'"
    
    group = StandardGroupBox(title_text)
    
    content_layout = QVBoxLayout()
    content_layout.setContentsMargins(8, 5, 8, 5)
    content_layout.setSpacing(3)

    # Add data fields
    if context.has_data():
        for key, value in context.data_context.items():
            row = QHBoxLayout()
            
            key_label = StandardLabel(f"{key}:", style=TextStyle.LABEL)
            key_label.setStyleSheet("font-weight: bold;")
            
            value_label = StandardLabel(str(value), style=TextStyle.LABEL)
            value_label.setWordWrap(True)
            
            row.addWidget(key_label)
            row.addWidget(value_label, 1)
            content_layout.addLayout(row)

    # Add hyperlink buttons
    if context.has_callbacks():
        buttons_layout = QHBoxLayout()
        for callback_info in context.callbacks:
            btn = QPushButton(callback_info.label)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setFlat(True)
            btn.setStyleSheet("""
                QPushButton {
                    color: #4a90e2;
                    border: none;
                    text-decoration: underline;
                    padding: 2px 4px;
                    font-size: 9pt;
                    background: transparent;
                }
                QPushButton:hover {
                    color: #357abd;
                    font-weight: bold;
                }
            """)
            btn.setToolTip(callback_info.tooltip)
            btn.clicked.connect(callback_info.callback)
            buttons_layout.addWidget(btn)
        
        buttons_layout.addStretch()
        content_layout.addLayout(buttons_layout)

    group.setLayout(content_layout)
    self.context_layout.addWidget(group)
```

---

## 🔮 Future Improvements

### Potential Enhancements:

1. **StandardButton for Hyperlinks**
   - Create a new ButtonRole.LINK for hyperlink-style buttons
   - Replace custom QPushButton styling with StandardButton
   - Example: `StandardButton("Open", role=ButtonRole.LINK)`

2. **Collapsible StandardGroupBox**
   - Add native collapse/expand functionality to StandardGroupBox
   - Arrow indicators in title (▼/▶)
   - Animate collapse/expand transitions
   - This would restore the collapsible feature removed in this update

3. **Context-Specific Icons**
   - Add icons to context section titles
   - Example: "📎 Connector • 'D38999'"
   - Use emoji or icon font

4. **Hover Effects on GroupBox**
   - Subtle highlight on hover
   - Indicates interactivity (if collapsible)

---

## 📂 Files Modified

1. **`app/document_scanner/Search/view.py`**
   - Added StandardGroupBox to imports
   - Updated `_create_matched_data_section()` to use StandardGroupBox
   - Updated `_create_collapsible_context()` to use StandardGroupBox
   - Removed custom QFrame styling
   - Removed white background colors
   - Added `background: transparent` to hyperlink buttons

---

## ✅ Testing Results

- ✅ Application starts without errors
- ✅ StandardGroupBox renders correctly
- ✅ Context sections display with proper styling
- ✅ No white backgrounds (uses default/transparent)
- ✅ Hyperlink buttons maintain styling
- ✅ Tooltips work correctly
- ✅ Callback connections functional

---

## 📝 Notes

### Trade-offs

**Lost Feature**: Custom collapsible headers with blue gradient
- Previous implementation had clickable headers to expand/collapse
- StandardGroupBox doesn't have built-in collapse functionality
- Could be added to StandardGroupBox in future enhancement

**Gained Benefits**:
- ✅ Consistent with component library
- ✅ Transparent/default backgrounds
- ✅ Simpler code
- ✅ Better maintainability
- ✅ Follows app design patterns

### Styling Preserved

Items that still use custom styling (justified):
- **Hyperlink buttons**: Unique appearance not covered by StandardButton roles
- **Key labels**: Bold weight for visual hierarchy
- **Layout spacing**: Context-specific spacing for dense display

---

*Component Integration Complete - Following Best Practices*
