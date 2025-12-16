"""
Generic Excel collector that reads Excel and validates against a schema
"""
import pandas as pd
from productivity_app.data_pipeline.schemas import DataSchema
from productivity_app.data_pipeline.decorators.data_collector import data_collector
from productivity_app.data_pipeline.types_enum import DataTypes


@data_collector(
    name="ExcelGeneric",
    inputs=["filepath"],
    outputs=[DataTypes.DataFrame]
)
def generic_excel_collector(filepath: str, schema: DataSchema = None) -> pd.DataFrame:
    """Read Excel file and optionally validate against schema
    
    Args:
        filepath: Path to Excel file
        schema: Optional schema defining required columns
        
    Returns:
        DataFrame (validated if schema provided)
        
    Raises:
        ValueError: If schema provided and validation fails
    """
    df = pd.read_excel(filepath)
    
    if schema is not None:
        is_valid, errors = schema.validate(df)
        if not is_valid:
            raise ValueError(f"Schema validation failed: {errors}")
    
    return df
