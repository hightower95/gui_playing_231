"""
Generic Excel collector that reads Excel and validates against a schema
"""
import pandas as pd
from productivity_app.data_pipeline.data_sources.schema_base_classes import DataSchema
from productivity_app.data_pipeline.data_collectors.decorator import data_collector
from productivity_app.data_pipeline.parameters import Variables


@data_collector(
    name="ExcelGeneric",
    inputs=[Variables.FilePath],
    outputs=[Variables.DataFrame]
)
def generic_excel_collector(filepath: str, sheet_name=None) -> pd.DataFrame:
    """Read Excel file and optionally validate against schema

    Args:
        filepath: Path to Excel file
        schema: Optional schema defining required columns

    Returns:
        DataFrame (validated if schema provided)

    Raises:
        ValueError: If schema provided and validation fails
    """
    df = pd.read_excel(filepath, sheet_name=sheet_name)

    return df
