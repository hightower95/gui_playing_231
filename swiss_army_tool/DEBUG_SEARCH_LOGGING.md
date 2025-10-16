# Enhanced Debug Logging for Document Scanner

## Debug Output Added

### Configuration Presenter

#### Adding Document
```
============================================================
ADDING DOCUMENT
============================================================
File Name: parts.csv
File Path: C:/data/parts.csv
Header Row: 0
Search Columns: ['Part Number', 'Description']
Return Columns: ['Part Number', 'Description']

✓ Added to documents list (total: 1)
✓ Added to view
✓ Configuration saved to: document_scanner_cache/documents_config.json
  Saved 1 document(s)
✓ Emitted update signal
============================================================
DOCUMENT ADDED SUCCESSFULLY
============================================================
```

#### Loading Configuration
```
============================================================
LOADING CONFIGURATION
============================================================
Config file: document_scanner_cache/documents_config.json
Documents found: 2

[1] parts.csv
    Path: C:/data/parts.csv
    Search columns: ['Part Number', 'Description']

[2] inventory.xlsx
    Path: C:/data/inventory.xlsx
    Search columns: ['SKU', 'Name']
============================================================
```

### Search Presenter

#### Receiving Documents
```
============================================================
SEARCH: Documents Updated
============================================================
Total documents: 2

[1] parts.csv
    File path: C:/data/parts.csv
    Header row: 0
    Search columns: ['Part Number', 'Description']
    Return columns: ['Part Number', 'Description']

[2] inventory.xlsx
    File path: C:/data/inventory.xlsx
    Header row: 1
    Search columns: ['SKU', 'Name']
    Return columns: ['SKU', 'Name']
============================================================
```

#### Searching
```
============================================================
SEARCH STARTED: 'connector'
============================================================
📚 Total documents to search: 2
  [1] parts.csv - Path: C:/data/parts.csv
  [2] inventory.xlsx - Path: C:/data/inventory.xlsx

📄 Searching document [1/2]: parts.csv
  📂 File path: C:\data\parts.csv
  ✓ File exists
  📊 Header row: 0
  📖 Loading file (type: .csv)...
  ✓ Loaded 150 rows, 3 columns
  📋 Columns: ['Part Number', 'Description', 'Status']
  🔍 Search columns: ['Part Number', 'Description']
  📤 Return columns: ['Part Number', 'Description']
  🔎 Searching in column 'Part Number'...
     Found 0 match(es)
  🔎 Searching in column 'Description'...
     Found 3 match(es)
     Sample values in 'Description': ['Cable assembly', 'Connector kit', ...]
  ✅ Found 3 result(s)

📄 Searching document [2/2]: inventory.xlsx
  📂 File path: C:\data\inventory.xlsx
  ✓ File exists
  📊 Header row: 1
  📖 Loading file (type: .xlsx)...
  ✓ Loaded 200 rows, 4 columns
  📋 Columns: ['SKU', 'Name', 'Quantity', 'Location']
  🔍 Search columns: ['SKU', 'Name']
  📤 Return columns: ['SKU', 'Name']
  🔎 Searching in column 'SKU'...
     Found 0 match(es)
  🔎 Searching in column 'Name'...
     Found 2 match(es)
  ✅ Found 2 result(s)

============================================================
SEARCH RESULTS: 5 total match(es)
============================================================
  • parts.csv: Part Number: P123, Description: Connector kit
  • parts.csv: Part Number: P456, Description: Cable connector
  • parts.csv: Part Number: P789, Description: Connector housing
  • inventory.xlsx: SKU: INV-001, Name: D-Sub connector
  • inventory.xlsx: SKU: INV-002, Name: USB connector

============================================================
SEARCH COMPLETE
============================================================
```

## Troubleshooting Guide

### Common Issues and What to Look For

#### Issue: "No documents configured"
**Debug Output Shows:**
```
❌ No documents configured
```
**Solution:** Add documents via Configuration tab

---

#### Issue: "File not found"
**Debug Output Shows:**
```
📄 Searching document [1/1]: parts.csv
  📂 File path: C:\data\parts.csv
  ❌ ERROR: File not found!
```
**Solutions:**
- Check if file was moved or deleted
- Verify path is correct in Configuration tab
- Remove and re-add the document

---

#### Issue: "Search column not found"
**Debug Output Shows:**
```
  📋 Columns: ['PartNum', 'Desc', 'Status']
  🔍 Search columns: ['Part Number', 'Description']
  ❌ Search column 'Part Number' NOT FOUND in file!
```
**Solutions:**
- Column names don't match (e.g., 'PartNum' vs 'Part Number')
- Check header row setting - may be incorrect
- Re-configure document with correct column names

---

#### Issue: "No matches found"
**Debug Output Shows:**
```
  🔎 Searching in column 'Description'...
     Found 0 match(es)
     Sample values in 'Description': ['Cable', 'Wire', 'Terminal']
```
**Analysis:**
- Search term doesn't appear in the data
- Try different search term
- Check case sensitivity (should be case-insensitive)
- Verify you're searching in the right columns

---

#### Issue: "CSV load failed"
**Debug Output Shows:**
```
  📖 Loading file (type: .csv)...
  ⚠️  CSV load failed, trying tab-separated: Error tokenizing data...
```
**Solutions:**
- File may have inconsistent delimiters
- File may be corrupted
- Try opening in Excel and re-saving as CSV

---

#### Issue: "Wrong header row"
**Debug Output Shows:**
```
  📊 Header row: 0
  📋 Columns: ['Data', '123', '456']  ← These are data values, not column names!
```
**Solution:**
- Header row is set incorrectly
- Re-configure document with correct header row
- If headers are on row 3, set header_row to 3

---

## Debug Symbol Legend

| Symbol | Meaning |
|--------|---------|
| ✓ | Success |
| ✅ | Found results |
| ❌ | Error |
| ⚠️ | Warning |
| ℹ️ | Information |
| ⏭️ | Skipped |
| 📚 | Total documents |
| 📄 | Current document |
| 📂 | File path |
| 📊 | Header row |
| 📖 | Loading file |
| 📋 | Column names |
| 🔍 | Search configuration |
| 🔎 | Searching column |
| 📤 | Return columns |

## What to Check When Getting No Results

### Step 1: Verify Documents Are Loaded
Look for:
```
LOADING CONFIGURATION
Documents found: X
```

If 0 documents, add some via Configuration tab.

### Step 2: Check Search Receives Documents
Look for:
```
SEARCH: Documents Updated
Total documents: X
```

If 0 documents, signal connection may be broken.

### Step 3: Verify File Paths
Look for:
```
📂 File path: C:\...
✓ File exists
```

If "File not found", fix the path or re-add document.

### Step 4: Check Columns Match
Look for:
```
📋 Columns: [...]
🔍 Search columns: [...]
```

Columns must match exactly (case-sensitive!).

### Step 5: Verify Data Loading
Look for:
```
✓ Loaded X rows, Y columns
```

If error here, file format issue.

### Step 6: Check Search Execution
Look for:
```
🔎 Searching in column 'X'...
   Found Y match(es)
```

If 0 matches, search term doesn't exist in that column.

### Step 7: View Sample Data
Look for:
```
Sample values in 'Column': [...]
```

This shows what's actually in the file.

## Performance Monitoring

The debug output also helps monitor performance:

```
📖 Loading file (type: .csv)...
✓ Loaded 10000 rows, 20 columns  ← Large file may be slow
```

If searches are slow with large files:
- Consider filtering to fewer columns
- Use more specific search terms
- Limit documents to only what's needed

## Turning Off Debug

To reduce console output, search for `print()` statements and comment them out, or add a debug flag:

```python
DEBUG = False  # Set to True to enable debug output

if DEBUG:
    print(f"Debug message")
```
