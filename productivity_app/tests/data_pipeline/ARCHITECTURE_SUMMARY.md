# Data Pipeline Architecture - Quick Visual Summary

## 🎯 CURRENT STATUS: ✅ YES - You CAN compare two CSV parts lists!

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER WRITES REPORT                        │
│  @report(title="Compare Parts", inputs=[PartsList, PartsList])  │
│  def compare_parts(parts1, parts2): ...                         │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ↓ (report needs PartsList type)
┌────────────────┴────────────────────────────────────────────────┐
│                     CENTRAL REGISTRY                             │
│  Matches: PartsList → CSVToPartsListCollector                   │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ↓ (finds collector automatically)
┌────────────────┴────────────────────────────────────────────────┐
│                   DATA COLLECTOR                                 │
│  @data_collector(inputs=[FilePath], outputs=[PartsList])        │
│  def csv_to_parts_list(filepath): ...                           │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ↓ (reads CSV, converts to Part objects)
┌────────────────┴────────────────────────────────────────────────┐
│                    SCHEMA VALIDATION                             │
│  Part model: {part_name, part_number, quantity?, ...}           │
└──────────────────────────────────────────────────────────────────┘
```

---

## Component Summary (One Line Each)

| Component | Purpose | Status |
|-----------|---------|--------|
| **Registry** | Matches data needs to data providers | ✅ Working |
| **Reports** | Functions decorated with `@report` that generate output | ✅ Working |
| **Collectors** | Functions decorated with `@data_collector` that read files | ✅ Working |
| **Parameters** | Define what inputs reports need (FilePath, PartsList, etc.) | ✅ Working |
| **Schemas** | Validate data structure (e.g., Part must have part_name, part_number) | ✅ Working |
| **Part Model** | Dataclass representing a part | ✅ Working |

---

## What You Can Do RIGHT NOW

### ✅ Simple CSV Column Report (WORKING)
```python
@report(
    title="CSV Columns",
    inputs=[DataSource.FilePath]
)
def show_columns(filepath: str):
    df = pd.read_csv(filepath)
    return df.columns.tolist()
```

### ✅ Parts List Report (WORKING)
```python
@report(
    title="Parts Summary",
    inputs=[DataSource.PartsList]  # Auto-finds CSV collector!
)
def parts_summary(parts: list[Part]):
    return f"Found {len(parts)} parts"
```

### ✅ COMPARE TWO CSV PARTS LISTS (READY TO BUILD!)
```python
@report(
    title="Compare Two Parts Lists",
    description="Find differences between two CSV parts files",
    inputs=[
        DataSource.PartsList.modify(name="parts1", description="First parts list"),
        DataSource.PartsList.modify(name="parts2", description="Second parts list")
    ]
)
def compare_parts_lists(parts1: list[Part], parts2: list[Part]):
    # Both CSVs will be auto-loaded and converted to Part objects!
    parts1_numbers = {p.part_number for p in parts1}
    parts2_numbers = {p.part_number for p in parts2}
    
    added = parts2_numbers - parts1_numbers
    removed = parts1_numbers - parts2_numbers
    
    return {
        "added": list(added),
        "removed": list(removed),
        "total_in_v1": len(parts1),
        "total_in_v2": len(parts2)
    }
```

---

## Files You Need to Touch (Minimum)

To add a new report:
1. ✅ **Only 1 file**: `productivity_app/data_pipeline/reports/your_new_report.py`

The collectors are already registered! You don't need to touch anything else.

---

## Architecture Pattern Name

**"Auto-Wiring Report System"** or **"Declarative Data Pipeline"**

- Reports declare what they need (`inputs=[PartsList]`)
- Registry auto-finds providers (collectors)
- User only writes business logic
- Type hints + IDE = autocomplete

---

## Current Complexity Level

| Metric | Score |
|--------|-------|
| Files to understand | ~10 core files |
| Files to touch for new report | **1 file** |
| Auto-wiring magic | High (good for users, confusing for maintainers) |
| IDE support | Excellent (type hints work) |
| Novice friendliness | **High** (just copy a template) |

---

## Testing Status

Based on test files:
- ✅ CSV collector works
- ✅ Excel collector works  
- ✅ Parts schema validation works
- ✅ Registry matching works
- ✅ End-to-end collector→report flow works
- ✅ Multiple inputs to reports work

**Verdict: System is functional and ready to use!**
