# Type Hinting and Parameter Usage Guide

## The Pattern You Want

### ✅ Use Default Parameter
```python
from productivity_app.data_pipeline.sources.data_sources import DataSources

@register_report(
    parameters=[
        DataSources.PartsList  # Just use the default!
    ]
)
def my_report(input_parts: Iterable[Part]) -> Dict[str, Any]:
    pass
```

### ✅ Modify Specific Fields
```python
@register_report(
    parameters=[
        DataSources.PartsList.modify(
            name="custom_parts",
            description="Custom description",
            required=False
        )
    ]
)
def my_report(input_parts: Iterable[Part]) -> Dict[str, Any]:
    pass
```

## Complete Working Example

```python
"""
Type-hinted report using DataSources.PartsList
"""
from typing import Dict, Any, Iterable
from productivity_app.data_pipeline.sources.data_sources import DataSources
from productivity_app.data_pipeline.models.part import Part
from productivity_app.data_pipeline.decorators.register_report import register_report


@register_report(
    name="Parts Summary",
    description="Summarize parts list",
    category="Inventory",
    parameters=[
        # Option 1: Use default
        DataSources.PartsList
        
        # Option 2: Modify as needed
        # DataSources.PartsList.modify(name="input_parts")
    ]
)
def generate_parts_summary(input_parts: Iterable[Part]) -> Dict[str, Any]:
    """Generate summary from parts list

    Args:
        input_parts: Iterable of Part objects
                    Each Part has:
                    - part_name: str
                    - part_number: str
                    - quantity: Optional[int]
                    - unit_cost: Optional[float]
                    - description: Optional[str]

    Returns:
        Summary statistics dictionary
    """
    parts_list = list(input_parts)
    
    summary = {
        'total_parts': len(parts_list),
        'unique_part_numbers': len(set(p.part_number for p in parts_list)),
        'part_names': [p.part_name for p in parts_list]
    }
    
    # Optional fields
    parts_with_quantity = [p for p in parts_list if p.quantity is not None]
    if parts_with_quantity:
        summary['total_quantity'] = sum(p.quantity for p in parts_with_quantity)
    
    return summary
```

## The Part Dataclass

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Part:
    """Single part in a parts list"""
    part_name: str              # Required
    part_number: str            # Required
    description: Optional[str] = None
    quantity: Optional[int] = None
    unit_cost: Optional[float] = None
```

## Type Hints in Action

### Function Signature
```python
def generate_parts_summary(input_parts: Iterable[Part]) -> Dict[str, Any]:
    #                                     ^^^^^^^^^^^^^^    ^^^^^^^^^^^^^^^
    #                                     Input type        Return type
```

### Inside Function
```python
def process_parts(input_parts: Iterable[Part]):
    # IDE knows each part is a Part object
    for part in input_parts:
        print(part.part_name)      # ✓ Autocomplete works!
        print(part.part_number)    # ✓ Type checking works!
        if part.quantity:          # ✓ Optional field handling
            total = part.quantity * part.unit_cost
```

## How DataSources Works

### Structure
```python
# In sources/data_sources.py
class DataSources:
    """Namespace for pre-configured parameters"""
    
    PartsList = PartsList  # Pre-configured instance
    # BOMData = BOMData
    # TestResults = TestResults
```

### What PartsList Is
```python
# In parameters/parts_list.py
PartsList = Source.DataSource(
    name="parts_list",
    data_type=DataTypes.PartsList,
    required=True,
    description="Parts list data source"
)
```

It's a **parameter instance**, not a function!

### Modification
```python
# Original instance remains unchanged
original = DataSources.PartsList
print(original.name)  # "parts_list"

# Create modified copy
modified = DataSources.PartsList.modify(name="custom_name")
print(modified.name)  # "custom_name"
print(original.name)  # Still "parts_list"
```

## Schema Validation

The schema is **automatically applied**:

```python
# Schema defines required columns
PARTS_LIST_SCHEMA = DataSchema(
    name="PartsList",
    required_columns=["Part Name", "Part Number"],  # ← Required!
    optional_columns=["Quantity", "Unit Cost"]      # ← Optional
)

# When data comes in, it's validated:
# ✓ Has "Part Name" and "Part Number" → Valid
# ✗ Missing "Part Number" → Invalid (fails validation)
```

## Adding New Parameters

Follow the same pattern:

### 1. Define in parameters/bom_data.py
```python
from productivity_app.data_pipeline.types_enum import DataTypes
from productivity_app.data_pipeline.schemas import DataSchema, data_schemas
from productivity_app.data_pipeline.sources.base import Source

# Define schema
BOM_SCHEMA = DataSchema(
    name="BOMData",
    required_columns=["Assembly", "Component", "Quantity"]
)

# Register schema
data_schemas.register(DataTypes.BOMData, BOM_SCHEMA)

# Create parameter instance
BOMData = Source.DataSource(
    name="bom_data",
    data_type=DataTypes.BOMData,
    required=True,
    description="Bill of Materials data"
)
```

### 2. Add to DataSources
```python
# In sources/data_sources.py
from productivity_app.data_pipeline.parameters.bom_data import BOMData

class DataSources:
    PartsList = PartsList
    BOMData = BOMData  # ← Add this
```

### 3. Create dataclass for type hints (optional)
```python
# In models/bom_item.py
@dataclass
class BOMItem:
    assembly: str
    component: str
    quantity: int
    reference_designator: Optional[str] = None
```

### 4. Use in reports
```python
@register_report(
    parameters=[
        DataSources.BOMData  # Use default
        # or
        DataSources.BOMData.modify(name="input_bom")
    ]
)
def analyze_bom(input_bom: Iterable[BOMItem]) -> Dict[str, Any]:
    pass
```

## Summary

✅ **Use default**: `DataSources.PartsList`  
✅ **Modify fields**: `DataSources.PartsList.modify(name="...", required=False)`  
✅ **Type hint**: `input_parts: Iterable[Part]`  
✅ **Schema validates automatically**: Required columns enforced  
✅ **Immutable**: Original instance unchanged when modified  

This pattern gives you:
- Clean syntax (`DataSources.PartsList`)
- Flexibility (`.modify()` when needed)
- Type safety (`Iterable[Part]`)
- Validation (schema enforcement)
