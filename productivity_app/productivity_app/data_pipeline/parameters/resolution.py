"""
Parameter Resolution Utilities

Utilities for resolving collected parameters by composing transport collectors
and schema converters.

This implements the collector-schema separation:
- Collectors are transport-only (return DataFrames)
- Schemas handle conversion (DataFrame → domain models)
- Parameter resolution composes them
"""
from typing import List, Any
from pathlib import Path
import pandas as pd

from productivity_app.data_pipeline.types_enum import DataTypes
from productivity_app.data_pipeline.data_sources.schema_base_classes.schema_register import data_schemas

# Import schemas to trigger auto-registration
from productivity_app.data_pipeline.data_sources import parts_list as _parts_list_schema


def resolve_collected_parameter_from_file(
    filepath: str,
    output_type: DataTypes
) -> Any:
    """Resolve a collected parameter from a file path

    Composes:
    1. Transport collector (file → DataFrame)
    2. Schema converter (DataFrame → domain model)

    Args:
        filepath: Path to file (CSV, Excel, etc.)
        output_type: Expected output type (DataTypes enum)

    Returns:
        Converted domain objects (e.g., List[Part])

    Raises:
        ValueError: If file format not supported or schema not found

    Example:
        parts = resolve_collected_parameter_from_file(
            "parts.csv",
            DataTypes.PartsList
        )
        # Returns List[Part]
    """
    # Import transport collectors (not model-specific collectors)
    from productivity_app.data_pipeline.data_collectors.csv_collector import csv_collector
    from productivity_app.data_pipeline.data_collectors.generic_excel_collector import generic_excel_collector

    # Detect file format
    path = Path(filepath)
    suffix = path.suffix.lower()

    # Step 1: Transport - Get DataFrame
    if suffix == '.csv':
        df = csv_collector(filepath)
    elif suffix in ['.xlsx', '.xls']:
        # Excel collector needs schema for validation
        schema = data_schemas.get_schema(output_type)
        if schema is None:
            raise ValueError(
                f"No schema registered for output type: {output_type}"
            )
        df = generic_excel_collector(filepath, schema)
    else:
        raise ValueError(
            f"Unsupported file format: {suffix}. "
            f"Supported formats: .csv, .xlsx, .xls"
        )

    # Step 2: Conversion - Get domain models
    schema = data_schemas.get_schema(output_type)
    if schema is None:
        raise ValueError(
            f"No schema registered for output type: {output_type}"
        )

    result = schema.convert(df)
    return result


def resolve_parts_list_from_file(filepath: str) -> List[Any]:
    """Resolve a PartsList from a file path

    Convenience function for the common case of resolving parts lists.

    Args:
        filepath: Path to CSV or Excel file containing parts

    Returns:
        List of Part objects

    Example:
        parts = resolve_parts_list_from_file("parts.csv")
    """
    return resolve_collected_parameter_from_file(
        filepath,
        DataTypes.PartsList
    )
