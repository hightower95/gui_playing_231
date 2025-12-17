"""
Excel to Parts List collector

Composes generic Excel collector with schema-based conversion.
"""
from typing import List
from productivity_app.data_pipeline.data_collectors.decorator import data_collector
from productivity_app.data_pipeline.types_enum import DataTypes
from productivity_app.data_pipeline.models.part import Part
from productivity_app.data_pipeline.data_sources.schema_base_classes.schema_register import data_schemas
from productivity_app.data_pipeline.data_collectors.generic_excel_collector import generic_excel_collector
from productivity_app.data_pipeline.parameters import Variables


@data_collector(
    name="ExcelToPartsListCollector",
    inputs=[Variables.FilePath],
    outputs=[DataTypes.PartsList]
)
def excel_to_parts_list_collector(filepath: str) -> List[Part]:
    """Collect parts list from Excel file

    Composes:
        1. generic_excel_collector (reads + validates)
        2. schema.convert (converts to Part objects)

    Args:
        filepath: Path to Excel file containing parts list

    Returns:
        List of Part objects
    """
    # Get registered schema (includes converter)
    schema = data_schemas.get_schema(DataTypes.PartsList)

    # Read and validate
    df = generic_excel_collector(filepath, schema)

    # Convert using schema's converter
    parts = schema.convert(df)

    return parts
