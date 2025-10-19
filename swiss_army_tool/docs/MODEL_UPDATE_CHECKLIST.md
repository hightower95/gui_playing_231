# Model Update Checklist

This document provides step-by-step instructions for updating models in the **EPD** and **Connector** modules when data structures, columns, or headings change.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [When to Use This Guide](#when-to-use-this-guide)
3. [EPD Model Update Checklist](#epd-model-update-checklist)
4. [Connector Model Update Checklist](#connector-model-update-checklist)
5. [Testing Your Changes](#testing-your-changes)
6. [Common Issues & Solutions](#common-issues--solutions)

---

## Overview

**Models** are responsible for:
- Loading data from files/databases
- Managing data structure in memory
- Providing filtered/processed data to presenters
- Thread-safe data access using `QMutex`

**Key Principle**: Models should be updated **first** when data structures change, then views/presenters are updated to match.

---

## When to Use This Guide

Update the model when:
- ✅ Column names change in source data (Excel, CSV, Database)
- ✅ New columns are added to source data
- ✅ Data types or structures change
- ✅ New filter options are needed
- ✅ New methods are needed to query/process data
- ✅ Statistics or aggregations need updating

---

## EPD Model Update Checklist

### 📂 File: `app/epd/epd_model.py`

### Step 1: Update Sample Data Structure
**Location**: `EpdDataWorker._load_sample_data()` method (around line 50)

- [ ] **1.1** Open `app/epd/epd_model.py`
- [ ] **1.2** Locate the `_load_sample_data()` method in `EpdDataWorker` class
- [ ] **1.3** Update the `sample_data` list of dictionaries with new column names:
  ```python
  sample_data = [
      {
          "EPD": "EPD-001",           # Keep or rename
          "Description": "...",        # Keep or rename
          "Cable": "Cable 100",        # Keep or rename
          "AWG": 20,                   # Keep or rename
          "NEW_COLUMN": "New Value",   # Add new columns
          # Remove old columns
      },
      # ... more rows
  ]
  ```

### Step 2: Update Data Loading Logic (If Loading from Real Source)
**Location**: `EpdDataWorker.run()` method (around line 30)

- [ ] **2.1** If loading from Excel/CSV, update file path and sheet name
- [ ] **2.2** If loading from database, update SQL query with new column names
- [ ] **2.3** Verify column name mappings match new structure
- [ ] **2.4** Add any data transformations needed (e.g., type conversions)

### Step 3: Update Filter Methods
**Location**: `EpdModel` class methods

- [ ] **3.1** Update `filter()` method if new columns need different filtering logic
- [ ] **3.2** Update column-specific methods like `get_records_by_cable()`:
  ```python
  def get_records_by_cable(self, cable_type: str) -> pd.DataFrame:
      # Update column name if "Cable" column was renamed
      return self.data[self.data['NEW_CABLE_COLUMN'] == cable_type].copy()
  ```
- [ ] **3.3** Add new filter methods for new columns:
  ```python
  def get_records_by_new_field(self, value: str) -> pd.DataFrame:
      """Get records filtered by new field"""
      with QMutexLocker(self._data_mutex):
          if self.data is None:
              return pd.DataFrame()
          return self.data[self.data['NEW_FIELD'] == value].copy()
  ```

### Step 4: Update Statistics Methods
**Location**: `EpdModel.get_statistics()` method (around line 200)

- [ ] **4.1** Update column references in statistics calculations:
  ```python
  stats = {
      'total_records': len(self.data),
      'unique_cables': self.data['NEW_CABLE_COLUMN'].nunique(),  # Update column name
      'new_stat': self.data['NEW_COLUMN'].mean(),                # Add new stats
      'loaded': True
  }
  ```
- [ ] **4.2** Add new statistical calculations for new columns
- [ ] **4.3** Remove statistics for removed columns

### Step 5: Update Export Methods
**Location**: `EpdModel.export_data()` method (around line 220)

- [ ] **5.1** Verify export includes all new columns automatically (DataFrame export handles this)
- [ ] **5.2** Add column filtering if only specific columns should be exported:
  ```python
  columns_to_export = ['EPD', 'Description', 'NEW_COLUMN']
  self.data[columns_to_export].to_csv(file_path, index=False)
  ```

### Step 6: Update Type Hints and Documentation
- [ ] **6.1** Update method docstrings to reflect new columns
- [ ] **6.2** Update return type hints if data structure changed
- [ ] **6.3** Add comments explaining new data fields

---

## Connector Model Update Checklist

### 📂 File: `app/connector/connector_model.py`

### Step 1: Update Sample Data Structure
**Location**: `ConnectorDataWorker._load_connector_data()` method (around line 60)

- [ ] **1.1** Open `app/connector/connector_model.py`
- [ ] **1.2** Locate the `_load_connector_data()` method in `ConnectorDataWorker` class
- [ ] **1.3** Update the connector dictionaries with new keys:
  ```python
  'connectors': [
      {
          'Part Number': 'D38999/26WA35PN',      # Keep or rename
          'Part Code': 'D38999-26WA35PN',        # Keep or rename
          'Material': 'Aluminum',                # Keep or rename
          'NEW_FIELD': 'New Value',              # Add new fields
          # Remove old fields
      },
      # ... more connectors
  ]
  ```

### Step 2: Update Filter Options
**Location**: Dictionary keys in `_load_connector_data()` and metadata lists

- [ ] **2.1** Update filter option lists (families, shell_types, etc.):
  ```python
  return {
      'connectors': [...],
      'families': ['D38999', 'VG', 'MS', 'NEW_FAMILY'],     # Add new families
      'shell_types': [...],                                 # Update as needed
      'new_filter_options': ['Option1', 'Option2'],        # Add new filter lists
  }
  ```

### Step 3: Update Getter Methods
**Location**: Various `get_*()` methods in `ConnectorModel` class

- [ ] **3.1** Add new getter methods for new filter options:
  ```python
  def get_new_filter_options(self) -> List[str]:
      """Get list of available new filter options (thread-safe)"""
      with QMutexLocker(self._data_mutex):
          if self.data:
              return self.data.get('new_filter_options', [])
          return []
  ```

### Step 4: Update Available Filter Options Method
**Location**: `ConnectorModel.get_available_filter_options()` method (around line 300)

- [ ] **4.1** Add new filter categories to the return dictionary:
  ```python
  return {
      'shell_types': shell_types,
      'materials': materials,
      'shell_sizes': shell_sizes,
      'insert_arrangements': insert_arrangements,
      'socket_types': socket_types,
      'keyings': keyings,
      'new_filter_field': new_filter_values,  # Add new filter
  }
  ```
- [ ] **4.2** Add logic to extract unique values for new filter:
  ```python
  new_filter_values = sorted(set(
      conn.get('NEW_FIELD') for conn in filtered_connectors
      if conn.get('NEW_FIELD')
  ))
  ```

### Step 5: Update Filter Connectors Method
**Location**: `ConnectorModel.filter_connectors()` method (around line 400)

- [ ] **5.1** Add filter logic for new fields:
  ```python
  # Apply new filter
  if filters.get('new_field') and filters['new_field'] != 'Any':
      if conn_data.get('NEW_FIELD') != filters['new_field']:
          match = False
  ```
- [ ] **5.2** Remove filter logic for removed fields
- [ ] **5.3** Update field names in existing filters if renamed

### Step 6: Update Alternative/Opposite Methods
**Location**: `find_alternative()` and `find_opposite()` methods (around line 370)

- [ ] **6.1** Update field references in alternative/opposite logic
- [ ] **6.2** Add new fields to results if needed:
  ```python
  dummy_alternatives = [
      {
          'Part Number': 'ALT-001',
          'Part Code': 'ALT-D38999-001',
          'Material': 'Aluminum',
          'NEW_FIELD': 'New Value',     # Add new fields
          'Reason': 'Same characteristics'
      }
  ]
  ```

### Step 7: Update Type Hints and Documentation
- [ ] **7.1** Update method docstrings to reflect new fields
- [ ] **7.2** Update return type hints if dictionary structure changed
- [ ] **7.3** Add comments explaining new filter options

---

## Testing Your Changes

### Test Checklist

After updating a model, verify:

#### Data Loading
- [ ] **T1** Run the application and navigate to the module
- [ ] **T2** Verify data loads without errors (check console for errors)
- [ ] **T3** Verify all new columns appear in the data
- [ ] **T4** Check loading progress messages display correctly

#### Data Display
- [ ] **T5** Verify new columns appear in table views
- [ ] **T6** Verify renamed columns display with correct headers
- [ ] **T7** Check that sorting works on all columns
- [ ] **T8** Verify data types display correctly (numbers, text, dates)

#### Filtering
- [ ] **T9** Test existing filters still work
- [ ] **T10** Test new filters return correct results
- [ ] **T11** Test filter combinations work together
- [ ] **T12** Verify "No results" displays when no matches

#### Statistics/Aggregations
- [ ] **T13** Check statistics display correct values
- [ ] **T14** Verify calculations use correct columns
- [ ] **T15** Test with empty data (should not crash)

#### Export
- [ ] **T16** Export data and verify all columns are present
- [ ] **T17** Check exported file format (CSV/Excel) is correct
- [ ] **T18** Verify column headers match new structure

#### Thread Safety
- [ ] **T19** Test rapid filter changes (should not crash)
- [ ] **T20** Test data loading cancellation (close while loading)
- [ ] **T21** Verify UI remains responsive during data loading

---

## Common Issues & Solutions

### Issue 1: KeyError when accessing column
**Symptom**: `KeyError: 'OLD_COLUMN_NAME'`

**Solution**:
1. Search for all references to old column name in model file
2. Replace with new column name: `Ctrl+F` → Find `'OLD_COLUMN_NAME'` → Replace with `'NEW_COLUMN_NAME'`
3. Check both string literals `'OLD_COLUMN'` and f-strings `f"{row['OLD_COLUMN']}"`

### Issue 2: Empty filter options
**Symptom**: Filter dropdowns are empty or show "No options"

**Solution**:
1. Verify column name in `get_available_filter_options()` matches data structure
2. Check that data is loaded before calling filter options
3. Add debug print to see what's in `filtered_connectors`:
   ```python
   print(f"DEBUG: Filtered connectors = {len(filtered_connectors)}")
   print(f"DEBUG: Sample data = {filtered_connectors[0] if filtered_connectors else 'None'}")
   ```

### Issue 3: Statistics showing wrong values
**Symptom**: Statistics display 0, NaN, or incorrect values

**Solution**:
1. Check column names in `get_statistics()` method
2. Verify column data type (string vs. number)
3. Add error handling:
   ```python
   'avg_value': self.data['COLUMN'].mean() if 'COLUMN' in self.data.columns else 0
   ```

### Issue 4: Export missing columns
**Symptom**: Exported file doesn't have all columns

**Solution**:
1. If using column selection in export, update the column list
2. Verify DataFrame has columns before export:
   ```python
   print(f"DEBUG: DataFrame columns = {self.data.columns.tolist()}")
   ```

### Issue 5: Thread safety errors
**Symptom**: Random crashes, "QObject::killTimer" warnings, or data corruption

**Solution**:
1. Ensure all data access uses `QMutexLocker`:
   ```python
   with QMutexLocker(self._data_mutex):
       # All data access here
       result = self.data[...]
   # Process result outside mutex lock
   ```
2. Never emit signals while holding mutex lock (emit after `with` block)

---

## Quick Reference: File Locations

### EPD Module
- **Model**: `app/epd/epd_model.py`
- **Presenter**: `app/epd/epd_presenter.py`
- **View (Search)**: `app/epd/SearchEpd/view.py`
- **View (Identify Best)**: `app/epd/IdentifyBestEpd/view.py`
- **Config**: `app/epd/epd_config.py`

### Connector Module
- **Model**: `app/connector/connector_model.py`
- **Presenter**: `app/connector/connector_presenter.py`
- **View (Lookup)**: `app/connector/Lookup/view.py`
- **View (Check Multiple)**: `app/connector/CheckMultiple/view.py`
- **Config**: `app/connector/Lookup/config.py`

---

## Update Order

When changing data structure, update in this order:

1. ✅ **Model** (this checklist)
2. ✅ **Config** (if filter options changed)
3. ✅ **View** (table columns, filters)
4. ✅ **Presenter** (data formatting, business logic)
5. ✅ **Tests** (verify all changes)

---

## Additional Resources

- **Base Model**: `app/core/base_model.py` - Parent class for all models
- **Threading Guide**: See `QThread` and `QMutex` documentation in Qt docs
- **Pandas Reference**: For DataFrame operations - https://pandas.pydata.org/docs/

---

*Last Updated: October 19, 2025*
*For questions or issues, consult the development team.*
