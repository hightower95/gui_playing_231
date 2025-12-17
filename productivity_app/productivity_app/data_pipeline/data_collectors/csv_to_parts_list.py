"""
CSV to Parts List collector

Composes CSV collector with schema-based conversion.
"""
from typing import List
from productivity_app.data_pipeline.data_collectors.decorator import data_collector
from productivity_app.data_pipeline.types_enum import DataTypes
from productivity_app.data_pipeline.models.part import Part
from productivity_app.data_pipeline.data_sources.schema_base_classes.schema_register import data_schemas
from productivity_app.data_pipeline.data_collectors.csv_collector import csv_collector
from productivity_app.data_pipeline.parameters.input_parameters import DataSource
# Alternative import: from productivity_app.data_pipeline.parameters import ParameterEnum


@data_collector(
    name="CSVToPartsListCollector",
    inputs=[DataSource.FilePath],  # or ParameterEnum.FilePath - both work!
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
    # Get registered schema (includes converter)
    schema = data_schemas.get_schema(DataTypes.PartsList)

    # Read CSV to DataFrame
    df = csv_collector(filepath)

    # Convert using schema's converter
    parts = schema.convert(df)

    return parts
