"""
Example Report Using PartsList Parameter

This demonstrates how to:
1. Define a parameter with a schema
2. Use it in a report decorator
3. Validate the input data
4. Type hint with Iterable[Part]
"""
from typing import Dict, Any, Union, Iterable
from pathlib import Path
import pandas as pd

from productivity_app.data_pipeline.sources.data_sources import DataSources
from productivity_app.data_pipeline.models.part import Part
from productivity_app.data_pipeline.decorators.register_report import register_report
from productivity_app.data_pipeline.sources.base import Source
from productivity_app.data_pipeline.types_enum import FileTypes


@register_report(
    name="Parts Summary Report",
    description="Generate a summary report from a parts list",
    category="Inventory",
    parameters=[
        # Use default PartsList parameter
        DataSources.PartsList
        
        # Or modify it:
        # DataSources.PartsList.modify(name="input_parts", description="Custom description")
    ]
)
def generate_parts_summary(input_parts: Iterable[Part]) -> Dict[str, Any]:
    """Generate summary from parts list

    Args:
        input_parts: Iterable of Part objects (typically from DataFrame conversion)
                    Each Part has part_name, part_number, and optional quantity, etc.

    Returns:
        Summary statistics dictionary containing:
            - total_parts: int
            - unique_part_numbers: int
            - part_names: list[str]
            - total_quantity: int (optional, if parts have quantity)

    Example:
        parts = [
            Part(part_name="Resistor", part_number="R001", quantity=100),
            Part(part_name="Capacitor", part_number="C002", quantity=50),
        ]
        result = generate_parts_summary(parts)
    """
    # Convert to list if needed for multiple iterations
    parts_list = list(input_parts)
    
    # The parameter's schema automatically validates that
    # each Part has part_name and part_number fields
    
    summary = {
        'total_parts': len(parts_list),
        'unique_part_numbers': len(set(p.part_number for p in parts_list)),
        'part_names': [p.part_name for p in parts_list]
    }
    
    # Check if any parts have quantity
    parts_with_quantity = [p for p in parts_list if p.quantity is not None]
    if parts_with_quantity:
        summary['total_quantity'] = sum(p.quantity for p in parts_with_quantity)

    return summary


# Example of using Source.FileSource for file-based parameters
@register_report(
    name="Parts File Import",
    description="Import and validate parts from an Excel file",
    category="Import",
    parameters=[
        Source.FileSource(
            name="parts_file",
            file_type=FileTypes.ExcelFile,
            required=True,
            description="Excel file containing parts list"
        )
    ]
)
def import_parts_file(parts_file: Union[str, Path]) -> pd.DataFrame:
    """Import parts from file

    Args:
        parts_file: Path to Excel file (string or Path object)

    Returns:
        DataFrame with parts data containing at least 'Part Name' and 'Part Number' columns
    """

    # Load the file
    df = pd.read_excel(parts_file)

    # Process...
    return df
