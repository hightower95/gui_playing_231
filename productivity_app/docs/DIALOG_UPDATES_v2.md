# Add Document Dialog - Updates v2

## Changes Made

### 1. Drag and Drop Implementation (Step 1)
- **Created `DropZoneWidget` class**:
  - Custom QFrame that accepts drag and drop
  - Visual feedback on hover (green border)
  - Styled drop zone with dashed border
  - Emits `file_dropped` signal when file is dropped
  - Includes integrated "Browse for File" button
  
- **Drag Events Handled**:
  - `dragEnterEvent`: Accepts URLs, changes style to green
  - `dragLeaveEvent`: Resets style to default
  - `dropEvent`: Extracts file path and emits signal
  
- **User Flow**:
  1. Drag file from file explorer over drop zone (turns green)
  2. Drop file → automatically loads
  3. OR click "Browse for File" button
  4. File name displays below drop zone
  5. "✓ Confirm File" button becomes enabled

### 2. Combined Steps 3 & 4
- **Old Design**:
  - Step 3: Preview Document (just view)
  - Step 4: Configure Header & Search Columns
  
- **New Design (Step 3)**:
  - Title: "Configure Document Structure"
  - Instructions: "Set the header row so column names appear at the top of the preview"
  - Header row spinner with tooltip
  - Live preview table (updates when header row changes)
  - Search columns multi-select list
  - Single confirmation button

- **Benefits**:
  - Immediate visual feedback when adjusting header row
  - See column names update in preview
  - Select search columns right after seeing the data
  - Fewer steps, more efficient workflow

### 3. File Type Handling
- **Assumption**: All files are CSV-separated unless they are .xlsx/.xls
- **Logic**:
  ```python
  if path.suffix.lower() in ['.xlsx', '.xls']:
      df = pd.read_excel(file_path, header=None)
  else:
      # Try CSV first
      try:
          df = pd.read_csv(file_path, header=None)
      except:
          # Fall back to tab-separated
          df = pd.read_csv(file_path, sep='\t', header=None)
  ```
- **Supported Files**: .csv, .txt, .xlsx, .xls, and any text file with delimiters

### 4. Updated Step Numbers
- **Step 1**: Add Document (drag & drop or browse)
- **Step 2**: Pick Document Type
- **Step 3**: Configure Document Structure (preview + header + search columns)
- **Step 4**: Specify Columns of Interest (return columns)
- **Step 5**: Specify Precondition (optional)

### 5. Step Completion Logic
- **Required Steps**: 1, 2, 3, 4 (Step 5 is optional)
- **Validation**:
  - Step 1: File must be loaded
  - Step 2: Document type selected (always valid)
  - Step 3: At least one search column selected
  - Step 4: At least one return column selected
  - Step 5: Optional (can skip)

## Visual Improvements

### Drop Zone Styling
```css
Default:
- Border: 2px dashed #cccccc
- Background: #f9f9f9
- Padding: 20px

Hover/Drag Over:
- Border: 2px dashed #4CAF50 (green)
- Background: #f0f8f0 (light green)
```

### File Selected Indicator
- ✅ Green text with file name
- ❌ Red text if error loading
- Hidden until file selected

### Step 3 Layout
- Bold instructions at top
- Header row spinner with explanation "(0 = first row)"
- Preview table with alternating row colors
- Search columns list below preview
- Confirmation button at bottom

## User Experience Flow

### Typical Workflow
1. **Step 1**: Drag CSV file into drop zone → file loads → confirm
2. **Step 2**: Select/enter document type → confirm
3. **Step 3**: 
   - Adjust header row spinner
   - Watch preview update in real-time
   - Select which columns to search in
   - Confirm
4. **Step 4**: Select columns to return in results → confirm
5. **Step 5**: (Optional) Add precondition filter → confirm
6. Click "Finish & Add Document"

### Key Features
- **Live Preview**: Header row changes immediately update the table
- **Visual Feedback**: Completed steps turn green
- **Progressive Disclosure**: Only see what's needed at each stage
- **Flexibility**: Can reopen any step to make changes
- **Clear Instructions**: Each step tells you exactly what to do

## Technical Details

### DropZoneWidget Class
- **Inherits**: QFrame
- **Properties**:
  - `setAcceptDrops(True)`: Enables drag and drop
  - `file_dropped = Signal(str)`: Emits file path
- **Methods**:
  - `dragEnterEvent()`: Accept file drops
  - `dragLeaveEvent()`: Reset styling
  - `dropEvent()`: Extract file path from MIME data
  - `_browse_file()`: Traditional file browser dialog

### State Management
```python
self.step_completed = {
    1: False,  # File selected
    2: False,  # Document type picked
    3: False,  # Preview + header + search columns configured
    4: False,  # Return columns configured
    5: False,  # Precondition (optional)
}
```

### Signals Flow
1. User drops file → `DropZoneWidget.file_dropped` → `_on_file_selected()`
2. `_on_file_selected()` → loads DataFrame, enables confirm button
3. User clicks "✓ Confirm File" → `_complete_step(1)`
4. Step 1 turns green, collapses, Step 2 expands
5. Continue through steps...
6. All required steps complete → "Finish" button enabled
7. Click Finish → `_accept()` → emit `add_document_requested` signal

## Future Enhancements

### Smart Header Detection
- Analyze first few rows
- Detect likely header row automatically
- Pre-select common column names for searching

### Preview Enhancements
- Syntax highlighting for different data types
- Show data type per column (string, number, date)
- Column statistics (unique values, nulls, etc.)

### Drag & Drop Polish
- Show file type icon in drop zone
- Preview file contents on hover
- Support multiple file drops (batch add)

### Accessibility
- Keyboard shortcuts for drag and drop alternative
- Screen reader announcements for step completion
- High contrast mode for drop zone
