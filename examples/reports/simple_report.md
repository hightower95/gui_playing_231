# Simple CSV Columns Report

## Motivation

We want to print out the column names of a CSV file. This is a common task when exploring data - you need to quickly see what columns are available without opening the entire file in Excel or a data viewer.

## Simple Overview

The report takes a CSV file path as input and outputs a formatted list of column names.

**Input:** Path to a CSV file  
**Output:** Print columns to terminal, and also return list of all columns

## Writing the Report

Here's the complete report definition:

```python
# These function names may change, but we need two things:
# 1. A way to register our function
from productivity_app.data_pipeline.reports.decorator import report
# 2. A way to register what inputs our report needs
from productivity_app.data_pipeline.parameters.input_parameters import DataSource
# A typical report will also have parameters. But we will cover this in a later file


@report(
    title="CSV Columns Report",
    description="Generates a report of the columns in a CSV file.",
    inputs=[DataSource.FilePath],
)
def csv_columns_report(filepath: str) -> str:
    """Generate a report of CSV columns

    Args:
        filepath: Path to the CSV file

    Returns:
        A string report of the columns in the CSV file
    """
    import pandas as pd

    df = pd.read_csv(filepath)
    columns = df.columns.tolist()
    report_lines = [f"Columns in CSV file '{filepath}':"]
    for col in columns:
        report_lines.append(f"- {col}")
        print(col)
    return "\n".join(report_lines)
```

### Key Components

1. **`@report` decorator**: Registers the report in the system
   - `title`: How users find the report
   - `description`: What the report does
   - `inputs`: What parameters the report needs

2. **Function signature**: `def csv_columns_report(filepath: str)`
   - The parameter name (`filepath`) matches what the decorator expects
   - Type hint (`str`) documents what type is expected

3. **Implementation**: Read CSV with pandas, extract columns, format output

## The FilePath Input

When we write `inputs=[DataSource.FilePath]`, we're specifying that this report needs a file path.
We can still call csv_columns_report directly and not need to care about the title / description. 
The reason for the @report is to register the report in another system. That system can be read by a GUI application to enable users to run your report without touching code. 

### What is DataSource.FilePath?

`DataSource.FilePath` is an **InputParameter** object defined in the data pipeline:

```python
# From: productivity_app/data_pipeline/parameters/input_parameters.py

@dataclass(frozen=True)
class InputParameter:
    """Base class for input parameters"""
    name: str
    required: bool = True
    description: str = ""
    
    def __call__(self, **kwargs):
        """Allow modifying parameters via function call syntax"""
        return replace(self, **kwargs)


class DataSource:
    """Namespace for common input parameter types"""
    
    FilePath = InputParameter(
        name="filepath",
        required=True,
        description="Path to file"
    )
```

### Why Use InputParameter Instead of a String?

Instead of just writing `inputs=["filepath"]`, we use `DataSource.FilePath` because:

1. **Type Safety**: It's an object with known properties (name, required, description)
2. **Modifiable**: Can customize with `DataSource.FilePath(required=False)`
3. **Discoverable**: Other systems can introspect what inputs mean
4. **Consistent**: Same FilePath definition used across all reports

### How the System Uses FilePath

When you call the report:

```python
report = reports.get_report_by_name("CSV Columns Report")
report.generate(filepath="examples/reports/data/simple_data.csv")
```

The system:
1. Looks up `DataSource.FilePath` in the report's inputs
2. Extracts the parameter name: `"filepath"`
3. Passes it to the function: `csv_columns_report(filepath="...")`

### Inspecting the Report

You can see what inputs a report needs:

```python
# Get dependency tree
print(report.get_dependency_tree())
# Output:
# CSV Columns Report
#       Input: filepath

# Get parameters list
params = report.get_parameters()
print(params)  # [InputParameter(name='filepath', required=True, description='Path to file')]
```

## Running the Report

```python
from productivity_app.data_pipeline import reports

# Get the report
report = reports.get_report_by_name("CSV Columns Report")

# Generate output
result = report.generate(filepath="examples/reports/data/simple_data.csv")
print(result)
```

**Output:**
```
Columns in CSV file 'examples/reports/data/simple_data.csv':
- Column1
- Column2
- Column3
```

## Summary

- Reports are registered with `@report` decorator
- `DataSource.FilePath` is a reusable input parameter definition
- The parameter's `.name` property (`"filepath"`) determines the kwarg name
- The system automatically routes parameters from the decorator to the function
