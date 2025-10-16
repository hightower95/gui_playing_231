# Column Filtering Fix

## Issues Fixed

### 1. Unselected Columns Appearing in Results
**Problem**: All columns from imported file were appearing in results, even if not selected during import.

**Solution**: Updated `_merge_context_columns()` to only merge selected columns:
- Search column (always included)
- Context columns (user-selected during import)
- No other input columns from original file

### 2. All Operations Showing Same Columns
**Problem**: Every batch operation (Lookup, Get Material, Check Status) showed all connector properties.

**Solution**: Created operation-specific column configuration in `config.py`:

```python
OPERATION_RESULT_COLUMNS = {
    'find_opposites': 'all',  # Show all properties
    'find_alternatives': 'all',  # Show all properties
    'lookup': 'all',  # Show all properties
    'get_material': [  # Only material-related
        'Part Number',
        'Part Code',
        'Minified Part Code',
        'Material'
    ],
    'check_status': [  # Only status-related
        'Part Number',
        'Part Code',
        'Minified Part Code',
        'Database Status'
    ]
}
```

## Implementation Details

### New Method: `_filter_result_columns()`
```python
def _filter_result_columns(self, results_df: pd.DataFrame, operation_type: str) -> pd.DataFrame:
    """Filter result columns based on operation configuration"""
    - Reads configuration from OPERATION_RESULT_COLUMNS
    - If 'all': returns all columns
    - If list: keeps only specified columns + Search Term + Status
    - Always preserves Search Term and Status columns
```

### Updated Method: `_merge_context_columns()`
**Before**:
```python
input_df = self.imported_df.copy()  # ALL columns
```

**After**:
```python
columns_to_merge = [self.search_column] + self.context_columns
columns_to_merge = [col for col in columns_to_merge if col in self.imported_df.columns]
input_df = self.imported_df[columns_to_merge].copy()  # ONLY selected columns
```

### Updated Flow in `on_operation_requested()`
1. Run batch operation → get results with all connector fields
2. **NEW**: Filter result columns based on operation type
3. Merge with selected input columns only
4. Reorder columns (Input columns first, Status, then result columns)
5. Display

## Configuration

To customize which columns an operation shows, edit `app/connector/CheckMultiple/config.py`:

```python
OPERATION_RESULT_COLUMNS = {
    'operation_name': 'all',  # Show everything
    # OR
    'operation_name': [  # Show only specific columns
        'Column 1',
        'Column 2',
        ...
    ]
}
```

## Example Results

### Lookup Operation (all columns)
```
Part Numbers | Context1  | Status | Part Number         | Part Code            | Minified Part Code   | Material  | Database Status | Family | Shell Type | ...
D38999/...   | Project A | Found  | D38999/26WA35PN    | D38999-26WA35PN     | D3899926WA35PN      | Aluminum  | Active          | D38999 | 26 - Plug  | ...
```

### Get Material Operation (filtered)
```
Part Numbers | Context1  | Status | Part Number         | Part Code            | Minified Part Code   | Material
D38999/...   | Project A | Found  | D38999/26WA35PN    | D38999-26WA35PN     | D3899926WA35PN      | Aluminum
```

### Check Status Operation (filtered)
```
Part Numbers | Context1  | Status | Part Number         | Part Code            | Minified Part Code   | Database Status
D38999/...   | Project A | Found  | D38999/26WA35PN    | D38999-26WA35PN     | D3899926WA35PN      | Active
```

## Benefits

✅ **Clean Results**: Only see relevant columns for each operation  
✅ **User Control**: Only selected input columns appear in results  
✅ **Configurable**: Easy to customize column sets per operation  
✅ **Consistent**: Search Term and Status always included  
✅ **Exportable**: Filtered columns are preserved in exports  

## Testing

1. Import `test_connectors.csv`
2. Select "Part Numbers" as search column
3. Select "Context1" as context column (DO NOT select Context2)
4. Run "Lookup" → Should see all connector fields + Part Numbers + Context1 (NO Context2)
5. Run "Get Material" → Should see only Material + Part Numbers + Context1
6. Run "Check Status" → Should see only Database Status + Part Numbers + Context1
