# Simple Visual: What To Use

## The One Import You Need

```python
from productivity_app.data_pipeline.parameters import ParameterEnum
```

---

## Simple Comparison Chart

```
┌─────────────────────────────────────────────────────────────┐
│                      ParameterEnum                          │
│                   (Your One-Stop Shop)                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  FilePath     →  User provides a file path                 │
│  InputPath    →  User provides input file                  │
│  OutputPath   →  User provides output file (optional)      │
│  PartsList    →  Auto-converted from CSV/Excel            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3 Common Patterns

### Pattern 1: Single File Input
```python
from productivity_app.data_pipeline.reports.decorator import report
from productivity_app.data_pipeline.parameters import ParameterEnum

@report(
    title="My Report",
    inputs=[ParameterEnum.FilePath]
)
def my_report(filepath: str):
    # filepath is a string like "C:/Users/data.csv"
    pass
```

### Pattern 2: Auto-Convert to Parts
```python
@report(
    title="Parts Summary",
    inputs=[ParameterEnum.PartsList]
)
def parts_summary(parts: list[Part]):
    # parts is already a list of Part objects!
    # The CSV was auto-read and auto-converted
    return len(parts)
```

### Pattern 3: Compare Two Files
```python
@report(
    title="Compare Parts",
    inputs=[
        ParameterEnum.PartsList(name="file1"),  # Customize name
        ParameterEnum.PartsList(name="file2")
    ]
)
def compare(file1: list[Part], file2: list[Part]):
    # Both CSVs auto-converted to Part objects
    diff = set(p.part_number for p in file1) - set(p.part_number for p in file2)
    return diff
```

---

## That's It!

You have **4 parameters** available:
1. `ParameterEnum.FilePath` - for raw file paths
2. `ParameterEnum.InputPath` - for input files
3. `ParameterEnum.OutputPath` - for output files (optional)
4. `ParameterEnum.PartsList` - for auto-converted parts lists

All in **one enum**. Simple!
