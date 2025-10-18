# Compare Versions - Quick Start Guide

## What is Compare Versions?

A powerful tool for comparing different versions of documents to identify changes and differences. Located in the Document Scanner module as the 4th tab.

## Quick Start (5 Steps)

### 1. Open Compare Versions Tab
Navigate to: **Document Scanner → Compare Versions**

### 2. Select Document
Click the document dropdown and choose:
- A versioned document from your projects, OR
- "Custom Document" for ad-hoc comparisons

### 3. Select Versions to Compare
**Option A**: Use version dropdowns
- Left: Version 1 (e.g., "v1.0")
- Right: Version 2 (e.g., "v2.0")

**Option B**: Drag-and-drop custom files
- Drop CSV/Excel file on left area → Version 1
- Drop CSV/Excel file on right area → Version 2

### 4. Click "⚖️ Compare Versions"
Configure comparison settings:
1. **Key Column**: Select unique identifier (e.g., "Part_Number")
2. **Columns to Compare**: Check columns to analyze for differences
3. **Columns to Show**: Check columns to display in results
4. Click **OK**

### 5. View Results
- **Yellow rows** = Different
- **Gray rows** = Same
- Filter changes: Click "🔍 Filter Changes Only"
- Export: Click "📤 Export Results"

## Example Workflow

```
1. Select: "Connector Specifications" (Project 1)
   → Versions auto-populate: v1.0, v1.1, v2.0

2. Choose: v1.0 (left) and v2.0 (right)

3. Click: "⚖️ Compare Versions"

4. Configure:
   - Key Column: "Connector_ID"
   - Compare: ✓ Price, ✓ Description, ✓ Manufacturer
   - Show: ✓ Connector_ID, ✓ Description, ✓ Price

5. Results show:
   - 150 rows compared
   - 12 differences found
   - Changed columns highlighted in yellow

6. Filter: Click "🔍 Filter Changes Only"
   → See only 12 changed rows

7. Export: Click "📤 Export Results"
   → Save to comparison_results.csv
```

## Common Use Cases

### Compare Two Versions of a Document
1. Select document
2. Choose v1.0 and v2.0
3. Compare
4. Filter changes
5. Export

### Compare Custom Files
1. Select "Custom Document"
2. Drag-drop file1.csv (Version 1)
3. Drag-drop file2.csv (Version 2)
4. Compare
5. Review results

### Compare Stored Version vs. Custom File
1. Select versioned document
2. Choose v1.0 from dropdown
3. Drag-drop custom_update.xlsx (auto-sets Version 2 to "Custom")
4. Compare
5. Validate changes

## Results Interpretation

### Verdict Column

| Verdict | Meaning | Color |
|---------|---------|-------|
| Same | Identical in both versions | Gray |
| Different | Values changed | Yellow |
| Only in Version 1 | Removed or not in V2 | - |
| Only in Version 2 | Added or not in V1 | - |

### Results Table Layout

```
Part_Number | Verdict   | Changed_Columns | Description_V1 | Description_V2 | Price_V1 | Price_V2
------------|-----------|-----------------|----------------|----------------|----------|----------
ABC-123     | Same      |                 | Widget         | Widget         | $10      | $10
XYZ-456     | Different | Price           | Widget Pro     | Widget Pro     | $15      | $12
DEF-789     | Only in Version 1 |         | Old Part       |                | $20      |
```

## Tips & Tricks

### 💡 Key Column Selection
- Must be unique in both versions
- Examples: ID, Part Number, SKU, Serial Number
- If no unique column, results may be incorrect

### 💡 Comparing Large Documents
- Select only relevant columns to compare (faster)
- Use "Filter Changes Only" to focus on differences
- Export filtered results for smaller files

### 💡 Keyboard Shortcuts
- Press Enter after selecting versions → Compare
- Right-click results table → Context menu
- Drag multiple files → Last dropped wins

### 💡 Export Options
- **CSV**: Best for large data, Excel compatibility
- **Excel**: Preserves formatting, better for presentations
- Export filtered → Only changes
- Export unfiltered → All rows

## Troubleshooting

### "No columns in common"
**Cause**: Files have different column names
**Fix**: Ensure both files have at least one matching column name

### "Please select a key column"
**Cause**: No key column selected in config dialog
**Fix**: Choose a unique identifier column

### Drag-drop not working
**Cause**: Wrong file type
**Fix**: Use CSV (.csv) or Excel (.xlsx, .xls) files only

### Comparison is slow
**Cause**: Too many columns or rows
**Fix**: Reduce columns to compare; use CSV instead of Excel

## Features at a Glance

✅ **Project-grouped documents** - Organized by project
✅ **Side-by-side version selection** - Easy comparison
✅ **Drag-and-drop support** - Quick custom file comparison
✅ **Flexible configuration** - Choose what to compare/show
✅ **Intelligent results** - Clear verdicts and change tracking
✅ **Filter changes** - Focus on differences
✅ **Export** - CSV or Excel
✅ **Context menu** - Right-click for quick actions

## Next Steps

- **Full Documentation**: See `docs/COMPARE_VERSIONS.md`
- **Custom Integration**: Modify `document_store.py` for your data source
- **Advanced Usage**: Explore filtering and export options

## Getting Help

- Check full documentation: `docs/COMPARE_VERSIONS.md`
- Review error messages in console
- Ensure files are formatted correctly
- Verify key column is unique

---

**That's it!** You're now ready to compare document versions like a pro! 🚀
