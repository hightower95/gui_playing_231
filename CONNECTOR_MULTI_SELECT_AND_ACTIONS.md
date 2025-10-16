# Connector Lookup - Multi-Select and Enhanced Actions

## Overview
Enhanced the Connector Lookup module with multi-row selection, context-aware actions, image display area, and action buttons.

## Features Implemented

### 1. Multi-Row Selection with Shift/Ctrl
**Table Selection Mode:**
```python
self.table.setSelectionMode(QTableView.ExtendedSelection)
```

**Behavior:**
- **Single click**: Select one row
- **Ctrl + click**: Add/remove individual rows from selection
- **Shift + click**: Select range from first selected to clicked row
- Standard keyboard navigation (Up/Down arrows with Shift/Ctrl)

### 2. Context Menu with Conditional Actions

**Conditional Enabling:**
- **"Find Alternative"**: Only enabled when exactly 1 row selected
- **"Find Opposite"**: Only enabled when exactly 1 row selected
- **"View Details"**: Available for any selection
- **"Copy Row"**: Available for any selection
- **"Export Selection"**: Available for any selection

**Implementation in `table_context_menu_mixin.py`:**
```python
# Disable "Find Alternative" and "Find Opposite" if multiple rows selected
if action_name in ["Find Alternative", "Find Opposite"] and num_selected != 1:
    action.setEnabled(False)
    action.setToolTip("Select exactly one row to use this action")
```

### 3. Enhanced Context Area with Image and Buttons

**Layout Structure:**
```
┌─────────────────────────────────────┐
│ Context Banner                      │
├──────────────────┬──────────────────┤
│                  │                  │
│  Context Text    │  Pinout Image    │
│  (QTextEdit)     │  (QLabel)        │
│                  │  200x200px       │
│                  │                  │
├──────────────────┴──────────────────┤
│ [Find Alternative] [Find Opposite]  │
└─────────────────────────────────────┘
```

**Image Area:**
- **Size**: 200x200px fixed
- **Border**: 2px dashed border
- **Placeholder**: "No Image" text when no image loaded
- **Purpose**: Display connector pinout diagrams
- **Future**: Will load actual connector images

**Button Row:**
- **Find Alternative**: Searches for alternative connectors with similar specs
- **Find Opposite**: Finds mating connector (plug ↔ receptacle)
- **State**: Disabled when 0 or 2+ rows selected, enabled when exactly 1 row selected

### 4. Tooltips on Multiselect Filter Options

**Implementation:**
```python
for item in left_items:
    list_item = QListWidgetItem(item)
    # Add tooltip with the same text
    list_item.setToolTip(item)
    left_list.addItem(list_item)
```

**Purpose:**
- Shows full text on hover
- Helpful when filter values are long and might be truncated
- Provides accessibility improvement

### 5. Part Code Propagation to Model

**Signal Flow:**
```
User Action (Button or Context Menu)
    ↓
View: Emit find_alternative_requested(part_code)
    ↓
Presenter: on_find_alternative(part_code)
    ↓
Model: find_alternative(part_code) → Returns List[Dict]
```

**View Methods:**
```python
def _get_part_code_from_row(self, row: int) -> str:
    """Extract Part Code from selected row"""
    # Handles sorting/filtering via proxy model
    # Returns actual Part Code value from DataFrame
```

**Presenter Methods:**
```python
def on_find_alternative(self, part_code: str):
    """Handle find alternative request with part_code parameter"""
    alternatives = self.model.find_alternative(part_code)

def on_find_opposite(self, part_code: str):
    """Handle find opposite request with part_code parameter"""
    opposite = self.model.find_opposite(part_code)
```

**Model Methods (Dummy Implementation):**
```python
def find_alternative(self, part_code: str) -> List[Dict[str, Any]]:
    """Returns list of alternative connectors"""
    # Currently returns dummy data
    # TODO: Implement actual alternative search logic

def find_opposite(self, part_code: str) -> Optional[Dict[str, Any]]:
    """Returns opposite/mating connector"""
    # Currently returns dummy data
    # TODO: Implement actual opposite search logic (plug ↔ receptacle)
```

## New Signals

**View Signals:**
```python
find_alternative_requested = Signal(str)  # part_code
find_opposite_requested = Signal(str)    # part_code
```

**Connection in Presenter:**
```python
self.view.find_alternative_requested.connect(self.on_find_alternative)
self.view.find_opposite_requested.connect(self.on_find_opposite)
```

## Button State Management

**Update Logic:**
```python
def update_context_buttons_state(self):
    """Enable/disable buttons based on selection"""
    selected_rows = self.table.selectionModel().selectedRows()
    exactly_one_selected = len(selected_rows) == 1
    
    self.find_alternative_btn.setEnabled(exactly_one_selected)
    self.find_opposite_btn.setEnabled(exactly_one_selected)
```

**Triggered On:**
- Table selection change
- After search completes
- After data refresh

**Connected in Presenter:**
```python
self.view.table.selectionModel().selectionChanged.connect(
    self.on_selection_changed
)

def on_selection_changed(self, selected, deselected):
    self.view.update_context_buttons_state()
```

## User Experience Flow

### Scenario 1: Find Alternative via Button
```
1. User searches for "D38999"
2. Results displayed in table
3. User clicks one row → Buttons enabled
4. Context shows connector details
5. User clicks "Find Alternative" button
6. part_code extracted from selected row
7. Signal emitted: find_alternative_requested("D38999-26WA35PN")
8. Presenter calls model.find_alternative("D38999-26WA35PN")
9. Model returns list of alternatives (currently dummy data)
10. TODO: Display alternatives in table or dialog
```

### Scenario 2: Find Opposite via Context Menu
```
1. User selects one connector row
2. Right-click on row
3. Context menu appears
4. "Find Opposite" option enabled (only 1 row selected)
5. User clicks "Find Opposite"
6. part_code extracted
7. Signal emitted: find_opposite_requested("D38999-26WA35PN")
8. Model finds mating connector (plug → receptacle or vice versa)
9. TODO: Display opposite connector
```

### Scenario 3: Multiple Selection
```
1. User selects row 1
2. Shift+click row 5 → Rows 1-5 selected
3. Buttons DISABLED (not exactly one row)
4. Right-click → Context menu
5. "Find Alternative" option GRAYED OUT with tooltip
6. "Find Opposite" option GRAYED OUT with tooltip
7. "View Details" and "Copy Row" still available
```

## Code Locations

### View (`app/connector/Lookup/view.py`)
- `_setup_results()` - Changed to `ExtendedSelection`
- `_setup_context_area()` - NEW: Creates enhanced layout with image and buttons
- `_get_part_code_from_row(row)` - NEW: Extracts Part Code from table
- `update_context_buttons_state()` - NEW: Manages button enable/disable
- `_on_find_alternative_button_clicked()` - NEW: Button handler
- `_on_find_opposite_button_clicked()` - NEW: Button handler
- `_on_find_alternative_context()` - NEW: Context menu handler
- `_on_find_opposite_context()` - NEW: Context menu handler
- `_create_dual_column_multiselect()` - UPDATED: Added tooltips to items

### Presenter (`app/connector/Lookup/presenter.py`)
- `__init__()` - Connected new signals
- `_on_data_ready()` - Connected selection change signal
- `on_selection_changed()` - NEW: Updates button states
- `on_find_alternative(part_code)` - NEW: Handles alternative search
- `on_find_opposite(part_code)` - NEW: Handles opposite search

### Model (`app/connector/connector_model.py`)
- `find_alternative(part_code)` - NEW: Returns alternatives (dummy data)
- `find_opposite(part_code)` - NEW: Returns opposite connector (dummy data)

### Mixin (`app/ui/table_context_menu_mixin.py`)
- `_show_context_menu()` - UPDATED: Conditional action enabling based on selection count

## Styling

**Button Styling:**
```css
QPushButton {
    background-color: #007ACC;  /* Primary blue */
    color: white;
    border: none;
    border-radius: 3px;
    padding: 5px 15px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #005A9E;  /* Darker blue */
}

QPushButton:disabled {
    background-color: #2D2D30;  /* Dark gray */
    color: #656565;              /* Muted text */
}
```

**Image Placeholder:**
```css
QLabel {
    border: 2px dashed #3F3F46;     /* Dashed border */
    background-color: #1E1E1E;      /* Dark background */
    color: #656565;                  /* Muted text */
    border-radius: 5px;
}
```

## Future Enhancements

### 1. Image Loading
```python
def load_pinout_image(self, part_code: str):
    """Load connector pinout diagram"""
    image_path = f"images/connectors/{part_code}.png"
    if os.path.exists(image_path):
        pixmap = QPixmap(image_path)
        self.pinout_image_label.setPixmap(pixmap)
    else:
        self.pinout_image_label.setText("No Image")
```

### 2. Alternative Display
```python
def show_alternatives_dialog(self, alternatives: List[Dict]):
    """Show alternatives in a dialog or sub-table"""
    # Create dialog with table of alternatives
    # Allow user to select and view details
    # Provide "Replace" button to switch to alternative
```

### 3. Opposite Auto-Search
```python
def auto_find_opposite(self, part_code: str):
    """Automatically determine opposite based on shell type"""
    # Parse shell type (26 - Plug → 24 - Receptacle)
    # Match shell size, insert arrangement, keying
    # Return exact mating connector
```

### 4. Bulk Operations
```python
def find_alternatives_bulk(self, part_codes: List[str]):
    """Find alternatives for multiple connectors"""
    # When 2+ rows selected, allow bulk alternative search
    # Display results in separate view
    # Compare alternatives side-by-side
```

## Testing Recommendations

### Multi-Selection
1. **Single Selection**: Click row → Verify buttons enabled
2. **Shift Range**: Select row 1, Shift+click row 5 → Verify 5 rows selected, buttons disabled
3. **Ctrl Toggle**: Select row 1, Ctrl+click row 3, Ctrl+click row 1 → Verify row 3 selected, buttons enabled
4. **Keyboard Nav**: Arrow keys, Shift+arrows, Ctrl+A → Verify all selection modes work

### Context Menu
1. **One Row**: Right-click → Verify "Find Alternative" and "Find Opposite" enabled
2. **Multiple Rows**: Select 2+ rows, right-click → Verify actions grayed out with tooltip
3. **No Selection**: Click empty area → Verify no context menu appears

### Button Actions
1. **Find Alternative**: Click button → Verify part_code logged to console
2. **Find Opposite**: Click button → Verify part_code logged to console
3. **Model Response**: Check console for dummy data returned from model

### Tooltips
1. **Hover Filter**: Hover over multiselect items → Verify tooltip appears
2. **Long Values**: Check that long filter values show full text in tooltip
3. **Empty Padding**: Hover over empty padding items → Verify no tooltip

## Known Limitations

1. **Dummy Data**: Model returns hardcoded alternatives/opposites
2. **No Image Loading**: Pinout image always shows "No Image" placeholder
3. **No Alternative Display**: Alternatives printed to console, not shown in UI
4. **Single Opposite**: Model assumes one opposite per connector (might have multiple)
5. **No Validation**: Part Code extraction doesn't validate connector exists

## Next Steps

1. Implement actual alternative search logic in model
2. Implement opposite/mating connector logic
3. Create dialog/view for displaying alternatives
4. Add image loading from file system or database
5. Add bulk operations for multiple selection
6. Add validation and error handling
7. Add loading indicators for model operations
8. Consider caching alternatives for performance
