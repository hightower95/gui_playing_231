# Expandable Steps Dialog - Add Document Redesign

## Overview
Redesigned the "Add Document" dialog to use an expandable step-by-step workflow. Each step expands automatically when the previous step is completed, or users can manually expand/collapse steps at any time.

## Design Philosophy
- **Progressive Disclosure**: Show only what's needed at each stage
- **Visual Feedback**: Completed steps turn green
- **Flexibility**: Users can reopen any previous step to make changes
- **Clear Progress**: See all 6 steps at a glance, understand where you are

## Step-by-Step Workflow

### Step 1: Add Document
- **Purpose**: Select the source document file
- **Actions**: 
  - Drag & drop (placeholder for future implementation)
  - Browse button to select file
  - File path displays when selected
- **Completion**: Click "✓ Confirm File" button (enabled after file selection)
- **Auto-advance**: Automatically expands Step 2 on completion

### Step 2: Pick Document Type
- **Purpose**: Categorize the document for future smart handling
- **Actions**:
  - Select from dropdown: default, part_numbers, specifications, custom
  - Editable combo box allows custom types
- **Completion**: Click "✓ Confirm Type"
- **Auto-advance**: Expands Step 3 on completion
- **Future Enhancement**: Type will determine preview format and search behavior

### Step 3: Preview Document
- **Purpose**: Verify the document loaded correctly
- **Display**:
  - Table showing first 20 rows
  - Info message: "Preview shows first 20 rows. Configure header in next step."
- **Completion**: Click "✓ Preview Looks Good"
- **Auto-advance**: Expands Step 4 on completion

### Step 4: Configure Header & Search Columns
- **Purpose**: Define data structure and which columns to search
- **Actions**:
  - **Header Row**: Spinner to select 0-based row index for headers
  - **Search Columns**: Multi-select list (QListWidget)
    - Shows column names from header row
    - Updates dynamically when header row changes
    - Must select at least one
- **Completion**: 
  - Button enabled only when search columns are selected
  - Click "✓ Confirm Search Configuration"
- **Auto-advance**: Expands Step 5 on completion
- **Live Preview**: Changing header row updates the preview table immediately

### Step 5: Specify Columns of Interest
- **Purpose**: Define which columns to return in search results
- **Actions**:
  - Multi-select list showing all available columns
  - Must select at least one column
- **Completion**:
  - Button enabled only when return columns are selected
  - Click "✓ Confirm Return Columns"
- **Auto-advance**: Expands Step 6 on completion

### Step 6: Specify Precondition (Optional)
- **Purpose**: Add filtering logic to determine when this document is searched
- **Actions**:
  - Checkbox to enable/disable precondition
  - Text input for Python expression
  - Example shown: `search_term.startswith("B") or len(search_term) > 5`
  - Uses `search_term` variable in expression
- **Completion**: Click "✓ Precondition Configured"
- **Note**: This step is always considered "complete" (optional)

## Visual Design

### Step Appearance

**Default State** (not completed):
- Gray border
- Black text
- Collapsible checkbox

**Completed State**:
- Green border (#4CAF50)
- Green title text
- Still collapsible for editing

**Expanded State**:
- Content visible
- Larger dialog height (auto-adjusts)

**Collapsed State**:
- Only title bar visible
- Dialog shrinks

### Layout Features
- Indented content (20px left margin) for visual hierarchy
- Consistent spacing between steps (5px)
- Each step has internal padding for breathing room
- Buttons aligned consistently within each step

## User Experience Flow

### Happy Path
1. User clicks "➕ Add Document"
2. Dialog opens with Step 1 expanded
3. User browses and selects file
4. Click "✓ Confirm File" → Step 1 collapses (turns green), Step 2 expands
5. User selects document type
6. Click "✓ Confirm Type" → Step 2 collapses (turns green), Step 3 expands
7. User sees preview, verifies data
8. Click "✓ Preview Looks Good" → Step 3 collapses (turns green), Step 4 expands
9. User adjusts header row, sees preview update
10. User selects search columns
11. Click "✓ Confirm Search Configuration" → Step 4 collapses (turns green), Step 5 expands
12. User selects return columns
13. Click "✓ Confirm Return Columns" → Step 5 collapses (turns green), Step 6 expands
14. User optionally adds precondition
15. "Finish & Add Document" button becomes enabled (bold styling)
16. Click to complete

### Editing Previous Steps
- Click on any completed step's checkbox to re-expand
- Make changes
- Step remains green (completed status preserved)
- Can collapse again without re-confirming

### Validation
- "Finish & Add Document" button only enabled when steps 1-5 complete
- Step 6 is optional, doesn't block finishing
- Individual step buttons validate their own requirements
- Final validation on "Finish" checks all required fields

## Technical Implementation

### State Tracking
```python
self.step_completed = {
    1: False,  # File selected
    2: False,  # Document type picked
    3: False,  # Preview loaded
    4: False,  # Header and search columns configured
    5: False,  # Return columns configured
    6: False,  # Precondition (always considered complete)
}
```

### Key Methods

**`_create_step_group(title, expanded)`**
- Creates QGroupBox with checkable title bar
- Custom stylesheet for borders and colors
- Returns group for content addition

**`_on_group_toggled(group, checked)`**
- Handles expand/collapse of step content
- Auto-adjusts dialog size

**`_complete_step(step_num)`**
- Marks step as complete
- Updates styling to green
- Collapses current step
- Expands next step
- Checks if all requirements met

**`_check_can_finish()`**
- Validates steps 1-5 are complete
- Enables/disables "Finish" button

**Live Update Handlers**
- `_check_step4_complete()`: Enables button when search columns selected
- `_check_step5_complete()`: Enables button when return columns selected
- `_reload_preview()`: Updates preview and column lists when header row changes

### Signals Flow
1. User completes all steps
2. Click "Finish & Add Document"
3. `_accept()` validates and builds config dict
4. `self.accept()` closes dialog with QDialog.Accepted
5. ConfigurationView receives result
6. Emits `add_document_requested.emit(dialog.config)`
7. ConfigurationPresenter handles caching and persistence

## Improvements Over Previous Design

### Before (Single Page)
- ❌ All options visible at once (overwhelming)
- ❌ No clear workflow or sequence
- ❌ Hard to know what to do next
- ❌ No visual feedback on progress
- ❌ Large scrolling dialog

### After (Expandable Steps)
- ✅ Progressive disclosure (see only what matters now)
- ✅ Clear numbered sequence
- ✅ Visual feedback on completion (green)
- ✅ Can review/edit any previous step
- ✅ Compact when steps collapsed
- ✅ Clear "next action" at each stage
- ✅ Finish button only enabled when ready

## Future Enhancements

### Drag & Drop
- Add drop zone in Step 1
- Handle file drops with QDragEnterEvent/QDropEvent
- Validate file types on drop

### Document Type Intelligence
- When type selected in Step 2, auto-configure common settings
- Example: "part_numbers" → auto-select "Part Number" as search column
- Load type-specific templates

### Preview Enhancements (Step 3)
- Link to document type (different formats for different types)
- Highlight potential header rows
- Show statistics (row count, column count, data types)
- Smart header detection algorithm

### Validation Indicators
- Show checkmarks next to each step title when complete
- Progress bar showing X/6 steps complete
- Estimated time remaining

### Keyboard Navigation
- Tab through steps
- Enter to confirm each step
- Escape to cancel
- Arrow keys to expand/collapse

### Accessibility
- Screen reader support for step status
- High contrast mode
- Keyboard shortcuts for all actions

## Configuration Result

The final configuration object contains:
```python
{
    'file_path': str,              # Full path to source file
    'file_name': str,              # Display name
    'doc_type': str,               # Document type category
    'header_row': int,             # 0-based header row index
    'search_columns': List[str],   # Column names to search in
    'return_columns': List[str],   # Column names to return
    'precondition_enabled': bool,  # Whether precondition is active
    'precondition': str            # Python expression (if enabled)
}
```

This config is then cached locally as CSV and stored in `documents_config.json` for cross-document search functionality.
