# CORRECTED: What Actually Exists in Your Code

## 🚨 The Confusion

I made an error in my examples - I used `DataSource.FilePath` but that **doesn't exist in your code anymore**!

---

## ✅ What ACTUALLY Works

### The Real Import Pattern

```python
# THIS EXISTS AND WORKS:
from productivity_app.data_pipeline.parameters import ParameterEnum

@report(
    title="My Report",
    inputs=[ParameterEnum.FilePath]  # ✅ THIS IS CORRECT
)
def my_report(filepath: str):
    pass
```

### What Your Files Use

Looking at [csv_columns.py](productivity_app/productivity_app/data_pipeline/reports/csv_columns.py#L7):
```python
from productivity_app.data_pipeline.parameters import ParameterEnum

@report(
    title="CSV Columns Report",
    inputs=[ParameterEnum.FilePath],  # ✅ This is what actually works!
)
```

---

## 🗺️ The Actual Mapping

### ParameterEnum (The Central Hub)

Located: `productivity_app/data_pipeline/parameters/parameter_enum.py`

```python
class ParameterEnum:
    # Primitive parameters (you provide directly)
    FilePath = FilePath      # From file_path.py
    InputPath = InputPath    # From input_path.py
    OutputPath = OutputPath  # From output_path.py
    
    # Collected parameters (from collectors)
    PartsList = PartsList    # From parts_list.py
```

### How It Works

```
1. Individual parameter files define parameters:
   └─ file_path.py → Creates FilePath parameter
   └─ parts_list.py → Creates PartsList parameter

2. parameter_enum.py imports them all:
   └─ from ...file_path import parameter as FilePath

3. You import the enum:
   └─ from parameters import ParameterEnum
   
4. You use: ParameterEnum.FilePath
```

---

## CORRECTED Example: Compare Two CSV Files

```python
"""
CORRECTED - This actually works with your codebase!
"""
from typing import List
from productivity_app.data_pipeline.reports.decorator import report
from productivity_app.data_pipeline.parameters import ParameterEnum  # ✅ Use ParameterEnum
from productivity_app.data_pipeline.models.part import Part


@report(
    title="Compare Two Parts Lists",
    description="Find differences between two CSV files",
    inputs=[
        # WRONG: DataSource.PartsList  ❌
        # RIGHT: ParameterEnum.PartsList ✅
        
        ParameterEnum.PartsList(  # ✅ Use ParameterEnum!
            name="old_parts",
            description="Original parts list (CSV file)"
        ),
        ParameterEnum.PartsList(  # ✅ Use ParameterEnum!
            name="new_parts", 
            description="Updated parts list (CSV file)"
        )
    ]
)
def compare_two_parts_lists(
    old_parts: List[Part], 
    new_parts: List[Part]
):
    """Compare two parts lists"""
    
    old_numbers = {p.part_number for p in old_parts}
    new_numbers = {p.part_number for p in new_parts}
    
    added = new_numbers - old_numbers
    removed = old_numbers - new_numbers
    
    print(f"Added: {len(added)}, Removed: {len(removed)}")
    
    return {
        "added": list(added),
        "removed": list(removed)
    }
```

---

## Why The Confusion?

### Option 1: Old Code (Might Have Existed Before)
Some collectors use:
```python
from productivity_app.data_pipeline.parameters.input_parameters import DataSource
inputs=[DataSource.FilePath]  # This import might fail or be old
```

### Option 2: The Current Way (What Works)
```python
from productivity_app.data_pipeline.parameters import ParameterEnum
inputs=[ParameterEnum.FilePath]  # ✅ This is the correct pattern
```

---

## 📋 Quick Reference

| What You Want | Correct Import | Usage |
|---------------|----------------|-------|
| Use FilePath | `from parameters import ParameterEnum` | `ParameterEnum.FilePath` |
| Use PartsList | `from parameters import ParameterEnum` | `ParameterEnum.PartsList` |
| Modify parameter | Same | `ParameterEnum.FilePath(required=False)` |
| Multiple inputs | Same | `[ParameterEnum.PartsList(name="v1"), ParameterEnum.PartsList(name="v2")]` |

---

## TLDR

**❌ DON'T USE:** `DataSource.FilePath` (doesn't exist or is deprecated)  
**✅ USE THIS:** `ParameterEnum.FilePath` (this is the current pattern)

The enum provides:
- IDE autocomplete
- Single import point
- All parameters in one place

**I apologize for the confusion in my earlier examples!**
