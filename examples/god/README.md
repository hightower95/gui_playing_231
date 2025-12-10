# God Module - Data Pipeline System

A flexible data pipeline framework for building modular data processing workflows.

## Overview

The God Module provides a declarative way to:
- **Register data providers** - Functions that load/fetch data from various sources
- **Register reporters** - Functions that consume data and generate reports/outputs
- **Execute pipelines** - Orchestrate data flow from providers through reporters

## Key Concepts

### Data Formats
Define the "shape" of data flowing through the pipeline. Examples:
- `DataFormat.EXCEL_DATAFRAME` - Pandas DataFrame from Excel
- `DataFormat.EXCEL_REPORT` - Generated Excel report file
- `DataFormat.JSON_DATA` - JSON structured data

### Data Providers
Functions decorated with `@data_provider` that:
- Load data from sources (files, APIs, databases)
- Declare what formats they **provide**
- Specify required **parameters**
- Can have **preconditions** that must be met

### Reporters
Functions decorated with `@reporter` that:
- Consume data in known formats
- Generate outputs (reports, files, visualizations)
- Declare what formats they **input** and **output**
- Support configurable **parameters**

## Quick Start

### 1. Define a Data Provider

```python
from god_module import data_provider, param, DataFormat
import pandas as pd

@data_provider(
    provides=[DataFormat.EXCEL_DATAFRAME],
    requires=[
        param('file_path', str, description='Path to Excel file'),
        param('sheet_name', str, default='Sheet1')
    ]
)
def load_excel(file_path: str, sheet_name: str):
    """Load Excel file into DataFrame"""
    return pd.read_excel(file_path, sheet_name=sheet_name)
```

### 2. Define a Reporter

```python
from god_module import reporter

@reporter(
    inputs=[DataFormat.EXCEL_DATAFRAME],
    outputs=[DataFormat.EXCEL_REPORT],
    parameters=[
        param('output_path', str, description='Output file path')
    ]
)
def save_report(df: pd.DataFrame, output_path: str):
    """Save DataFrame to Excel report"""
    df.to_excel(output_path, index=False)
    return output_path
```

### 3. Execute the Pipeline

```python
from god_module import Pipeline

# Create pipeline
pipeline = Pipeline()

# Run provider
pipeline.run_provider('load_excel', file_path='data.xlsx')

# Run reporter
result = pipeline.run_reporter('save_report', output_path='report.xlsx')

print(f"Report saved to: {result}")
```

## Proof of Concept: Excel Merger

See `poc_excel_merge.py` for a complete example that:
1. Loads two Excel files using data providers
2. Merges them using a reporter
3. Outputs a combined Excel file

Run it with:
```bash
python poc_excel_merge.py
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Pipeline                         │
│  - Orchestrates execution                           │
│  - Manages PipelineContext                          │
│  - Validates parameters                             │
└─────────────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼──────────┐   ┌────────▼────────┐
│ Data Providers   │   │   Reporters     │
│ (Sources)        │   │   (Outputs)     │
└──────────────────┘   └─────────────────┘
        │                       │
        └───────────┬───────────┘
                    │
            ┌───────▼────────┐
            │  Data Formats  │
            │  (Contracts)   │
            └────────────────┘
```

## Features

### Parameter System
- **Type-safe parameters** with type hints
- **Default values** for optional parameters
- **Validation** before execution

### Context Management
- **Data sharing** between providers and reporters
- **Metadata tracking** for pipeline execution
- **Logging** built into context

### Registry System
- **Automatic registration** via decorators
- **Discovery** of providers and reporters
- **Querying** by format or capability

## Advanced Usage

### Preconditions

```python
def has_api_key(context):
    return context.has('api_key')

@data_provider(
    provides=[DataFormat.JSON_DATA],
    preconditions=[has_api_key]
)
def fetch_from_api(api_key: str):
    # Only runs if has_api_key returns True
    pass
```

### Multiple Inputs/Outputs

```python
@reporter(
    inputs=[DataFormat.EXCEL_DATAFRAME, DataFormat.EXCEL_DATAFRAME],
    outputs=[DataFormat.EXCEL_REPORT]
)
def merge_data(df1: pd.DataFrame, df2: pd.DataFrame, output_path: str):
    """Merge two DataFrames"""
    merged = pd.concat([df1, df2])
    merged.to_excel(output_path, index=False)
    return output_path
```

### Accessing Pipeline Context

```python
pipeline = Pipeline()
pipeline.context.set('user_id', 12345)
pipeline.context.log("Processing started")

# Later, in a provider/reporter
def my_function():
    user_id = pipeline.context.get('user_id')
```

## Extension Points

Add new data formats in `formats.py`:
```python
class DataFormat(str, Enum):
    MY_CUSTOM_FORMAT = "my_format"
```

Then use in providers/reporters:
```python
@data_provider(provides=[DataFormat.MY_CUSTOM_FORMAT])
def my_provider():
    return my_custom_data
```

## Future Enhancements

- **Dependency resolution** - Auto-run providers based on reporter needs
- **Parallel execution** - Run independent providers concurrently
- **Caching** - Store provider results to avoid recomputation
- **DAG visualization** - Visual pipeline flow diagrams
- **Type validation** - Runtime type checking for data formats
- **Async support** - Async/await for I/O-bound operations

## Files

- `god_module/` - Core framework
  - `core/pipeline.py` - Pipeline orchestration
  - `core/registry.py` - Provider/reporter registration
  - `core/decorators.py` - @data_provider and @reporter
  - `core/parameter.py` - Parameter definitions
  - `core/context.py` - Execution context
  - `formats.py` - Data format definitions
- `poc_excel_merge.py` - Proof of concept example
