# Compare Versions Feature

## Overview

The **Compare Versions** tab allows users to compare different versions of documents to identify changes and differences. This is useful for:
- Tracking document evolution over time
- Identifying changes between versions
- Comparing production vs. development data
- Validating data migrations
- Auditing document updates

## Features

### Document Selection with Project Grouping
- Documents organized by project with visual separators
- Easy navigation through large document libraries
- "Custom Document" option for ad-hoc comparisons

### Flexible Version Selection
- Side-by-side version pickers for easy comparison
- Auto-selection of first and last versions
- Support for comparing any two versions

### Drag-and-Drop Custom Files
- Drop areas for each version
- Supports CSV and Excel files
- Automatically sets picker to "Custom" when file is dropped
- Visual feedback during drag-and-drop

### Configurable Comparison
- Choose key column to identify unique rows
- Select which columns to compare
- Choose which columns to display in results
- Select/Deselect all shortcuts

### Intelligent Results Display
- Side-by-side display of both versions
- Clear verdict: "Same", "Different", "Only in Version X"
- Highlights which columns changed
- Color-coded results (yellow for differences)

### Advanced Features
- **Filter Changes**: Toggle between showing all rows or only changed rows
- **Export**: Save results to CSV or Excel
- **Context Menu**: Right-click for quick actions

## User Interface

### Header Section (200px height)
1. **Document Selector**: Dropdown with project groupings
   ```
   -- Select Document --
   ─── Project 1 ───
     Connector Specifications
     Cable Assembly List
   ─── Project 2 ───
     Parts Database
   ─── Other ───
     Custom Document
   ```

2. **Version Selectors**: Two side-by-side dropdowns
   - Version 1 (left)
   - Version 2 (right)
   - Each includes "Custom" option

3. **Drag-Drop Areas**: Two side-by-side areas
   - Drop CSV or Excel files
   - Visual feedback on hover and drop
   - Shows filename when dropped

4. **Compare Button**: Large, centered button to trigger comparison

### Content Section
- **Results Table**: Full comparison results with columns:
  - Key column (user-selected)
  - Verdict (Same/Different/Only in Version X)
  - Changed Columns (comma-separated list)
  - Data columns from both versions (suffixed with _V1 and _V2)

- **Action Buttons**:
  - 🔍 Filter Changes Only / 📋 Show All Rows (toggle)
  - 📤 Export Results

- **Status Label**: Shows comparison statistics

## Workflow

### Basic Comparison

1. **Select Document**
   - Choose from dropdown
   - Versions automatically populate

2. **Select Versions**
   - Pick Version 1 and Version 2 from dropdowns
   - Or drag-drop custom files

3. **Click Compare**
   - Configuration dialog appears

4. **Configure Comparison**
   - Select key column (required)
   - Choose columns to compare
   - Choose columns to show
   - Click OK

5. **View Results**
   - Table shows all rows with verdict
   - Yellow highlight for differences
   - Statistics in status bar

6. **Filter/Export** (optional)
   - Filter to show only changes
   - Export to CSV or Excel

### Custom Document Comparison

1. Select "Custom Document" from dropdown
2. Drag-drop two files (CSV or Excel)
3. Click Compare
4. Follow configuration steps above

### Comparing Custom vs. Versioned

1. Select a versioned document
2. Choose a version for Version 1
3. Drag-drop custom file for Version 2
   - Automatically sets to "Custom"
4. Click Compare

## Configuration Dialog

### Key Column
**Required**: Column that uniquely identifies each row
- Must be present in both versions
- Used to match rows between versions

Example: Part Number, ID, Serial Number

### Columns to Compare
**Required**: At least one column
- Only these columns will be checked for differences
- Select relevant columns to focus comparison

Example: Price, Description, Status

### Columns to Show
**Required**: At least one column
- Controls which columns appear in results
- Helps reduce clutter in large documents

Example: Part Number, Description, Price

### Tips
- Use "Select All" / "Deselect All" for quick setup
- Key column is automatically included in results
- Can compare and show different column sets

## Results Interpretation

### Verdict Values

**Same**: Row exists in both versions with identical values
- All compared columns match
- Gray background

**Different**: Row exists in both versions but has differences
- At least one compared column changed
- Yellow background
- "Changed Columns" shows which columns differ

**Only in Version 1**: Row only exists in first version
- Row was deleted or not yet added

**Only in Version 2**: Row only exists in second version
- Row was added or removed from Version 1

### Results Table Columns

**Key Column**: Unique identifier (e.g., "Part_Number")

**Verdict**: Same / Different / Only in Version X

**Changed_Columns**: Comma-separated list (only for "Different" rows)
- Example: "Price, Description"

**Data Columns**: Suffixed with _V1 and _V2
- `Description_V1`: Value from Version 1
- `Description_V2`: Value from Version 2
- Side-by-side for easy comparison

### Example

```
Part_Number | Verdict   | Changed_Columns      | Description_V1 | Description_V2 | Price_V1 | Price_V2
------------|-----------|---------------------|----------------|----------------|----------|----------
ABC-123     | Same      |                      | Widget         | Widget         | $10.00   | $10.00
XYZ-456     | Different | Price, Description   | Old Widget     | New Widget     | $15.00   | $12.00
DEF-789     | Only in Version 1 |              | Legacy Part    |                | $20.00   |
GHI-012     | Only in Version 2 |              |                | New Part       |          | $25.00
```

## Filtering and Export

### Filter Changes Only
**Button**: 🔍 Filter Changes Only / 📋 Show All Rows (toggle)

- **Off** (default): Shows all rows
- **On**: Shows only rows with verdict "Different"

Use case: Focus on what actually changed

### Export Results
**Button**: 📤 Export Results

- Exports currently displayed data
  - If filtered: Exports only changes
  - If unfiltered: Exports all rows

- Supported formats:
  - CSV: compatibility with Excel, databases
  - Excel: Preserves formatting, multi-sheet support

- File naming: `comparison_results.csv` (default)

## Document Store Integration

### DocumentStore Interface

The Compare Versions feature integrates with the `DocumentStore` module to access document metadata.

**Required Method**: `get_all_documents()`

Returns documents organized by project:
```python
{
    "Project 1": [
        {
            "name": "Connector Spec",
            "id": "conn_spec_p1",
            "versions": ["v1.0", "v1.1", "v2.0"],
            "metadata": {"type": "csv", "path": "/path/to/file"}
        }
    ],
    "Project 2": [...]
}
```

**Required Method**: `get_document_data(document_id, version)`

Returns document data as pandas DataFrame for specific version.

**Required Method**: `get_custom_document_data(file_path)`

Loads custom file (CSV or Excel) and returns as DataFrame.

### Implementing Your Document Store

To integrate with your actual data source:

1. **Modify** `app/document_scanner/document_store.py`
2. **Implement** `get_all_documents()` to query your database/file system
3. **Implement** `get_document_data()` to load specific versions
4. **Keep** `get_custom_document_data()` as-is (handles file loading)

Example implementation:
```python
class DocumentStore:
    @staticmethod
    def get_all_documents():
        # Query your database or file system
        connection = get_database_connection()
        projects = connection.query("SELECT * FROM projects")
        
        result = {}
        for project in projects:
            documents = get_documents_for_project(project.id)
            result[project.name] = [
                {
                    "name": doc.name,
                    "id": doc.id,
                    "versions": get_versions_for_document(doc.id),
                    "metadata": doc.metadata
                }
                for doc in documents
            ]
        return result
        
    @staticmethod
    def get_document_data(document_id, version):
        # Load specific version from storage
        file_path = get_file_path(document_id, version)
        return pd.read_csv(file_path)  # or load from database
```

## Technical Details

### File Structure
```
app/document_scanner/
├── CompareVersions/
│   ├── __init__.py
│   ├── view.py              # UI components
│   ├── presenter.py         # Business logic
│   └── config_dialog.py     # Comparison configuration dialog
├── document_store.py        # Data access layer
└── document_scanner_tab.py  # Integration (adds 4th tab)
```

### Class Hierarchy

**CompareVersionsView** (extends BaseTabView)
- Header: Document/version selectors, drag-drop areas
- Content: Results table, action buttons
- Signals: document_selected, version1_selected, compare_requested, etc.

**CompareVersionsPresenter** (extends QObject)
- Manages state: current document, versions, custom files
- Loads data from DocumentStore
- Performs comparison logic
- Handles filtering and export

**ComparisonConfigDialog** (extends QDialog)
- Modal dialog for configuration
- Returns: key_column, compare_columns, show_columns

**DocumentStore** (static class)
- Interface to document repository
- get_all_documents(), get_document_data(), get_custom_document_data()

### Signal Flow

```
User Action → View Signal → Presenter Handler → Update View

1. Document Selected
   view.document_selected → presenter.on_document_selected → view.populate_versions()

2. Compare Clicked
   view.compare_requested → presenter.on_compare_requested → 
   show config dialog → perform comparison → view.display_comparison_results()

3. Filter Clicked
   view.filter_changes_requested → presenter.on_filter_changes → 
   toggle filter → view.display_comparison_results()
```

### Comparison Algorithm

**Input**: Two DataFrames, configuration

**Process**:
1. Set key column as index
2. Find union of all keys (all rows from both versions)
3. For each key:
   - Check if in Version 1 only → "Only in Version 1"
   - Check if in Version 2 only → "Only in Version 2"
   - If in both → Compare selected columns
     - If any differ → "Different" + list changed columns
     - If all same → "Same"
4. Build results DataFrame with _V1 and _V2 suffixed columns
5. Order columns: Key, Verdict, Changed_Columns, data columns

**Output**: DataFrame with comparison results

## Error Handling

### User Errors

**No Document Selected**
- Message: "Please select a document first"
- Solution: Choose from dropdown

**No Custom File**
- Message: "Please drop a custom file or select a version"
- Solution: Drag-drop file or choose version

**No Common Columns**
- Message: "The two versions have no columns in common"
- Solution: Ensure files have at least one matching column

**No Key Column Selected**
- Message: "Please select a key column"
- Solution: Choose key column in config dialog

**No Columns Selected**
- Message: "Please select at least one column to compare/show"
- Solution: Check at least one checkbox

### Technical Errors

**File Loading Error**
- Message: "Failed to load [Version X]: [error details]"
- Logged to console with traceback

**Comparison Error**
- Message: "Error comparing versions: [error details]"
- Logged to console with traceback

**Export Error**
- Message: "Error exporting results: [error details]"
- User-friendly error dialog

## Best Practices

### Performance
- Limit columns to compare (faster comparison)
- Filter results before export (smaller files)
- Use appropriate file formats (CSV for large data)

### Workflow
- Always select key column carefully (must be unique)
- Compare relevant columns only (reduces noise)
- Export before filtering (preserves all data)

### Data Quality
- Ensure consistent key column values
- Handle missing data gracefully (shown as empty)
- Verify column names match between versions

## Future Enhancements

Potential improvements:
- **Diff View**: Inline diff for text changes
- **Statistics Panel**: Summary of changes by type
- **History**: Track comparison history
- **Scheduled Comparisons**: Automatic periodic comparisons
- **Merge Tool**: Apply changes from one version to another
- **Three-way Comparison**: Compare three versions
- **Change Visualization**: Charts/graphs of changes over time
- **Audit Trail**: Who made changes and when
- **Batch Comparison**: Compare multiple documents at once

## Troubleshooting

### Issue: Drag-drop not working
- **Solution**: Ensure file is CSV or Excel (.csv, .xlsx, .xls)
- **Solution**: Check file permissions

### Issue: Comparison very slow
- **Solution**: Reduce number of columns to compare
- **Solution**: Use CSV instead of Excel for large files
- **Solution**: Filter data before comparison

### Issue: Export fails
- **Solution**: Check write permissions for target folder
- **Solution**: Close file if already open in Excel
- **Solution**: Choose different file format

### Issue: Wrong results
- **Solution**: Verify key column is truly unique
- **Solution**: Check column selection in config dialog
- **Solution**: Ensure data types match between versions

## Example Use Cases

### Use Case 1: Product Catalog Update
**Scenario**: Compare old product catalog with updated version

1. Select "Product Catalog" document
2. Choose v1.0 (old) and v2.0 (new)
3. Click Compare
4. Key: ProductID
5. Compare: Price, Description, Status
6. Show: ProductID, Name, Price, Description
7. Filter to see only price changes
8. Export for review

### Use Case 2: Data Migration Validation
**Scenario**: Verify data migrated correctly from old system

1. Select "Custom Document"
2. Drop old system export (Version 1)
3. Drop new system export (Version 2)
4. Click Compare
5. Key: RecordID
6. Compare: All columns
7. Show: All columns
8. Export all rows for audit trail

### Use Case 3: Configuration Drift Detection
**Scenario**: Find differences between dev and prod configurations

1. Select "Configuration File" document
2. Choose "dev" (Version 1) and "prod" (Version 2)
3. Click Compare
4. Key: ConfigKey
5. Compare: Value
6. Show: ConfigKey, Description, Value
7. Filter changes only
8. Review differences before deploying

## API Reference

### CompareVersionsPresenter

```python
def start_loading()
    # Initialize and load documents from store
    
def on_document_selected(document_id: str)
    # Handle document selection, populate versions
    
def on_compare_requested()
    # Load data, show config dialog, perform comparison
    
def on_filter_changes()
    # Toggle between all rows and changes only
    
def on_export_results()
    # Export results to file (CSV or Excel)
```

### CompareVersionsView

```python
def populate_documents(documents_by_project: Dict)
    # Populate document dropdown with groupings
    
def populate_versions(versions: List[str])
    # Populate version dropdowns
    
def display_comparison_results(results_df: DataFrame)
    # Show comparison results in table
    
# Signals:
document_selected(str)          # document_id
version1_selected(str)          # version
version2_selected(str)          # version
custom_file1_dropped(str)       # file_path
custom_file2_dropped(str)       # file_path
compare_requested()
filter_changes_requested()
export_requested()
```

### ComparisonConfigDialog

```python
def __init__(columns: List[str])
    # Create dialog with column checkboxes
    
def get_config() -> Dict
    # Returns: {'key_column', 'compare_columns', 'show_columns'}
```

## Summary

The Compare Versions feature provides a powerful, user-friendly way to:
- ✅ Compare document versions side-by-side
- ✅ Identify what changed between versions
- ✅ Support both versioned and custom documents
- ✅ Flexible configuration for different use cases
- ✅ Export results for further analysis
- ✅ Filter to focus on changes only

Perfect for data validation, audit trails, configuration management, and tracking document evolution over time.
