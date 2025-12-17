# Quick Start: Build Your First Comparison Report

## ✅ YES, you can compare two CSVs!

Your data pipeline is **ready to use**. Here's the fastest path to success:

---

## 3-Step Process (5 minutes)

### Step 1: Copy the Template (1 minute)

Open: `productivity_app/data_pipeline/reports/compare_parts.py`

The simplest version:
```python
from productivity_app.data_pipeline.reports.decorator import report
from productivity_app.data_pipeline.parameters.input_parameters import DataSource
from productivity_app.data_pipeline.models.part import Part

@report(
    title="My Comparison",
    inputs=[
        DataSource.PartsList.modify(name="file1"),
        DataSource.PartsList.modify(name="file2")
    ]
)
def my_comparison(file1: list[Part], file2: list[Part]):
    numbers1 = {p.part_number for p in file1}
    numbers2 = {p.part_number for p in file2}
    
    added = numbers2 - numbers1
    removed = numbers1 - numbers2
    
    print(f"Added: {len(added)}, Removed: {len(removed)}")
    return {"added": added, "removed": removed}
```

### Step 2: Create Test CSV Files (2 minutes)

Create `test_parts_v1.csv`:
```csv
part_number,part_name,quantity
P001,Resistor,100
P002,Capacitor,50
P003,Diode,25
```

Create `test_parts_v2.csv`:
```csv
part_number,part_name,quantity
P001,Resistor,150
P003,Diode,25
P004,Transistor,75
```

### Step 3: Run It (2 minutes)

```python
from productivity_app.data_pipeline.registry import registry

# Your report is auto-registered!
report = registry.get_report("My Comparison")

# Run it
result = report['func'](
    file1=...,  # The system will load and convert CSVs
    file2=...
)
```

---

## What Happens Automatically

```
1. You call report.generate(file1="v1.csv", file2="v2.csv")
                    ↓
2. System sees you need: PartsList type
                    ↓
3. Registry finds: CSVToPartsListCollector
                    ↓
4. Collector reads CSV → converts to Part objects
                    ↓  
5. Schema validates: part_number and part_name exist
                    ↓
6. Your function receives: two List[Part] objects
                    ↓
7. You write comparison logic
                    ↓
8. Return results
```

**You only write step 7!**

---

## Key Insight: The "Magic" Explained

```python
# When you write this:
inputs=[DataSource.PartsList]

# The system does this:
# 1. Looks up PartsList in parameter registry
# 2. Finds PartsList is output_type of CSVToPartsListCollector
# 3. CSVToPartsListCollector needs FilePath input
# 4. FilePath is a ROOT parameter (user provides it)
# 5. Chain: User CSV → Collector → Part objects → Your Report
```

Not magic - just **dependency resolution**!

---

## To Add a New Report

**Only edit 1 file:**
1. Create `productivity_app/data_pipeline/reports/my_report.py`
2. Copy template from `compare_parts.py`
3. Change the business logic
4. Done!

**Files you DON'T touch:**
- Registry ❌
- Collectors ❌
- Parameters ❌
- Models ❌

They're already set up!

---

## Common Patterns

### Pattern 1: Single CSV Input
```python
@report(title="Summary", inputs=[DataSource.FilePath])
def summarize(filepath: str):
    df = pd.read_csv(filepath)
    return f"Rows: {len(df)}"
```

### Pattern 2: Parts List Input (Auto-Converts)
```python
@report(title="Count Parts", inputs=[DataSource.PartsList])
def count(parts: list[Part]):
    return len(parts)
```

### Pattern 3: Multiple Inputs (Comparison!)
```python
@report(
    title="Compare",
    inputs=[
        DataSource.PartsList.modify(name="v1"),
        DataSource.PartsList.modify(name="v2")
    ]
)
def compare(v1: list[Part], v2: list[Part]):
    # Your diff logic here
    pass
```

---

## Test Your Report

```bash
# Run the test
cd productivity_app
python -m pytest tests/data_pipeline/test_compare_two_csvs.py -v

# Should see:
# ✅ CSV comparison test passed!
# ✅ Detailed comparison test passed!
```

---

## Troubleshooting

### "Report not found"
→ Make sure you imported the module:
```python
from productivity_app.data_pipeline.reports import compare_parts
```

### "Missing parameter"
→ Check your CSV has `part_number` and `part_name` columns

### "Type error"  
→ Verify function signature matches inputs:
```python
inputs=[A, B]  → def func(a, b):  # ✅
inputs=[A, B]  → def func(x):     # ❌
```

---

## Next Steps

1. ✅ Run test: `pytest tests/data_pipeline/test_compare_two_csvs.py`
2. ✅ Try example: Open `compare_parts.py` in your IDE
3. ✅ Modify: Change the comparison logic
4. ✅ Expand: Add more fields (quantity, manufacturer, etc.)

---

## Summary

| Question | Answer |
|----------|--------|
| Can I compare two CSVs? | **YES ✅** |
| How many files to edit? | **1 file** |
| Does it work now? | **YES ✅** |
| Type hints work? | **YES ✅** |
| IDE autocomplete? | **YES ✅** |

**You're ready to build!** 🚀
