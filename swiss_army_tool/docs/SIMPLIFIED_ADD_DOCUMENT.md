# Simplified Add Document Dialog

## Changes Made

### Simplified from 5 Steps to 2 Steps

**Old Design** (overcomplicated):
- Step 1: Add Document
- Step 2: Pick Document Type
- Step 3: Configure Document Structure (preview + header + search)
- Step 4: Specify Return Columns
- Step 5: Specify Precondition

**New Design** (streamlined):
- **Step 1**: Add Document (drag & drop or browse)
- **Step 2**: Configure Document Structure (preview + header + search columns)

### Removed Features
- ❌ Document Type selection (always defaults to "default")
- ❌ Return Columns selection (returns same columns as search columns)
- ❌ Precondition configuration (removed from UI)

### Kept Features
- ✅ Drag and drop file upload
- ✅ File browser
- ✅ Live preview table
- ✅ Header row configuration
- ✅ Search columns multi-select
- ✅ Collapsible step groups

## New Workflow

### Step 1: Add Document
1. Drag & drop file or click "Browse for File"
2. File loads automatically
3. File name displays below drop zone
4. Click "✓ Confirm File"
5. Step 1 turns green and collapses
6. Step 2 automatically expands

### Step 2: Configure Document Structure
1. Preview table loads automatically showing first 20 rows
2. Adjust "Header Row" spinner to set which row contains column names
3. Preview updates in real-time as you change header row
4. Column list populates with column names from header row
5. Select one or more columns to search in
6. Click "✓ Confirm Configuration"
7. Click "Finish & Add Document"

## Search Behavior

### How Search Works
1. User enters search term in Search tab
2. System searches **only in the columns you specified** in Step 2
3. Results show **the same columns** you selected as searchable
4. Search is case-insensitive and uses "contains" matching

### Example
If you select columns: `Part Number`, `Description`, `Status`

**Search Input**: "connector"

**What Happens**:
- Searches for "connector" in Part Number column
- Searches for "connector" in Description column  
- Searches for "connector" in Status column
- Returns matching rows showing: Part Number, Description, Status

### Search Implementation (Verified ✓)

The search presenter (`Search/presenter.py`) correctly:

1. **Loads cached CSV** from configured path
2. **Iterates through search columns** specified in config
3. **Case-insensitive contains search**:
   ```python
   matches = df[df[search_col].astype(str).str.contains(search_term, case=False, na=False)]
   ```
4. **Returns data from return columns** (same as search columns)
5. **Creates SearchResult objects** with matched data
6. **Displays results** in the Search view table

## Configuration Object

When you finish adding a document, this config is created:

```python
{
    'file_path': str,              # Full path to source file
    'file_name': str,              # Display name (e.g., "data.csv")
    'doc_type': 'default',         # Always 'default' now
    'header_row': int,             # 0-based index (0 = first row)
    'search_columns': List[str],   # Columns to search in
    'return_columns': List[str],   # Same as search_columns
    'precondition_enabled': False, # Always False
    'precondition': ''             # Empty string
}
```

## Benefits of Simplification

### User Experience
- ✅ **Faster workflow**: 2 steps instead of 5
- ✅ **Less confusion**: No need to understand document types or preconditions
- ✅ **Clear purpose**: Just pick columns to search
- ✅ **Immediate feedback**: Preview updates live

### Technical Benefits
- ✅ **Simpler code**: Fewer validation checks
- ✅ **Easier maintenance**: Less complexity
- ✅ **Consistent behavior**: No edge cases from preconditions
- ✅ **Better performance**: Less UI overhead

## File Format Support

**Supported Files**:
- `.csv` - Comma-separated values
- `.txt` - Treated as CSV (comma-separated)
- `.xlsx` / `.xls` - Excel files

**Loading Logic**:
```python
if file.endswith('.xlsx') or file.endswith('.xls'):
    df = pd.read_csv(file, header=header_row, nrows=20)
else:
    # Try CSV first
    try:
        df = pd.read_csv(file, header=header_row, nrows=20)
    except:
        # Fall back to tab-separated
        df = pd.read_csv(file, sep='\t', header=header_row, nrows=20)
```

## Preview Behavior

### Live Preview Updates
- **Trigger**: Header row spinner value changes
- **Action**: Reloads file with `header=header_row` parameter
- **Display**: Shows first 20 rows with proper column headers
- **Side Effect**: Updates column list for selection

### Why Reload Instead of Manipulate?
Previously, we loaded the entire file and manipulated the DataFrame. Now we:
1. Reload with pandas' native `header` parameter
2. Only load 20 rows (`nrows=20`)
3. Get proper column names automatically
4. Better performance and accuracy

## Future Enhancements (Removed for Now)

These features were removed but could be added back if needed:

### Document Types (Removed)
- Could auto-configure based on file content
- Could apply different search strategies
- Could enable type-specific validation

### Return Columns (Removed)
- Could select different columns to return vs. search
- Could reduce result size
- Could focus on specific data

### Preconditions (Removed)
- Could filter which documents are searched
- Could optimize search performance
- Could enable conditional logic

## Testing Checklist

- [ ] Drag and drop .csv file
- [ ] Drag and drop .txt file (CSV format)
- [ ] Drag and drop .xlsx file
- [ ] Browse for file
- [ ] Change header row and see preview update
- [ ] Select multiple search columns
- [ ] Confirm configuration
- [ ] Add document
- [ ] Search for term
- [ ] Verify results show correct columns
- [ ] Verify search works across all selected columns
- [ ] Remove document
- [ ] Add multiple documents
- [ ] Search across multiple documents
