"""
CSV to Parts List collector

Composes CSV collector with schema-based conversion.
Schema is auto-registered on import.
"""
from typing import List
from productivity_app.data_pipeline.data_collectors.decorator import data_collector
from productivity_app.data_pipeline.types_enum import DataTypes
from productivity_app.data_pipeline.models.part import Part
from productivity_app.data_pipeline.data_sources.schema_base_classes.schema_register import data_schemas
from productivity_app.data_pipeline.data_collectors.csv_collector import csv_collector
from productivity_app.data_pipeline.parameters import Variables

# Auto-register schema on import
from productivity_app.data_pipeline.data_sources import parts_list as _parts_list_schema


@data_collector(
    name="CSVToPartsListCollector",
    inputs=[Variables.FilePath],
    outputs=[DataTypes.PartsList]
)
def csv_to_parts_list_collector(filepath: str) -> List[Part]:
    """Collect parts list from CSV file

    Composes:
        1. csv_collector (reads CSV to DataFrame)
        2. schema.convert (converts to Part objects)

    Args:
        filepath: Path to CSV file containing parts list

    Returns:
        List of Part objects
    """
    # Get registered schema (auto-registered on import)
    schema = data_schemas.get_schema(DataTypes.PartsList)

    # Read CSV to DataFrame
    df = csv_collector(filepath)

    # Convert using schema's converter
    parts = schema.convert(df)

    return parts
