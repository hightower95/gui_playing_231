"""
DataFrame to PartsList Transformer

Transforms pandas DataFrames into typed PartsList objects using the registered schema.
"""
import pandas as pd
from typing import List

from ..data_sources.schema_base_classes.schema_register import data_schemas
from ..types_enum import DataTypes
from ..data_transformers.decorator import data_transformer


@data_transformer(
    name="DataFrameToPartsList",
    input_type=DataTypes.DataFrame,
    output_type=DataTypes.PartsList
)
def dataframe_to_parts_list(df: pd.DataFrame) -> List:
    """Transform DataFrame to PartsList using registered schema
    
    Args:
        df: DataFrame with parts data
        
    Returns:
        List of Part objects
        
    Raises:
        ValueError: If no schema is registered for PartsList
    """
    schema = data_schemas.get_schema(DataTypes.PartsList)
    if schema is None:
        raise ValueError("No schema registered for PartsList")
    
    return schema.convert(df)
