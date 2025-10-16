# Connector Context Provider Implementation

## Summary
Implemented the ConnectorContextProvider to provide additional context to Document Scanner search results. When a document is searched and returns results containing part numbers, the Connector tab's data is automatically queried to enrich the results with connector details.

## Changes Made

### 1. Results View - Separate Tables Per Document
**File**: `app/document_scanner/Search/view.py`
- Changed from unified table with all columns to separate tables per document
- Each document has its own collapsible section with a table
- Tables only show columns relevant to that specific document
- Removed context column from results table (context shown in detail area)

**Structure**:
```
📄 Document 1 (3 results)
  # | Column1 | Column2 | Column3
  1 | Value1  | Value2  | Value3
  2 | Value4  | Value5  | Value6

📄 Document 2 (2 results)
  # | PartNum | Description
  1 | P-123   | Widget
  2 | P-456   | Gadget
```

### 2. ConnectorContextProvider - Real Implementation
**File**: `app/connector/connector_context_provider.py`
- Implemented `_lookup_connector()` method to actually search connector data
- Searches connector model's data for part numbers
- Tries exact match first on Part Number, Part Code, and Minified Part Code
- Falls back to partial match (contains) if exact match not found
- Returns connector details:
  - Part Number
  - Family
  - Shell Type
  - Shell Size
  - Insert Arrangement
  - Material
  - Socket Type
  - Keying
  - Status

### 3. Context Provider Registration
**File**: `app/tabs/main_window.py`
- Import ConnectorContextProvider
- Create instance with connector model: `ConnectorContextProvider(self.connectors.model)`
- Register with document scanner: `self.document_scanner.search_presenter.register_context_provider(connector_context)`

## How It Works

1. **User adds document** with columns like "Part Number", "part_number", "partnumber", or "pn"
2. **User performs search** for a term
3. **Search finds matches** in the document
4. **Context enrichment happens**:
   - Each result is passed to registered context providers
   - ConnectorContextProvider examines the matched_row_data
   - If it finds a part number column, it looks up that part number
   - If found in connector database, it creates a Context object with connector details
   - Context is attached to the SearchResult
5. **Results displayed**:
   - Results shown in separate tables per document
   - User clicks on a result
   - Detail view shows matched data PLUS context from Connector tab

## Example

If a document has:
```
Part Number | Description | Location
D38999/26WA35PN | Connector | Bin A
```

And user searches for "D38999", the result will show:
- **Matched Data**: Part Number, Description, Location
- **Additional Context [Connector]**:
  - Term: D38999/26WA35PN
  - Part Number: D38999/26WA35PN
  - Family: D38999
  - Shell Type: 26 - Plug
  - Shell Size: 10
  - Material: Aluminum
  - Status: Active
  - etc.

## Testing

To test:
1. Run the application
2. Wait for Connector tab to auto-load data
3. Go to Document Scanner → Configuration
4. Add a document with a "Part Number" column containing values like "D38999/26WA35PN"
5. Go to Search tab
6. Search for a term that matches rows with part numbers
7. Click on a result
8. **Detail area should show both matched data AND connector context!**

## Next Steps

- Add more context providers (EPD, etc.)
- Consider caching lookups for performance
- Add enable/disable toggles for context providers in UI
- Add visual indicator in results table when context is available (optional)
