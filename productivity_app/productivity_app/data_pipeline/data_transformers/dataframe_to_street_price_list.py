"""
DataFrame to StreetPriceList Transformer

Transforms pandas DataFrames into typed StreetPriceList objects using the registered schema.
"""
import pandas as pd
from typing import List

from ..data_sources.schema_base_classes.schema_register import data_schemas
from ..types_enum import DataTypes
from ..data_transformers.decorator import data_transformer


@data_transformer(
    name="DataFrameToStreetPriceList",
    input_type=DataTypes.DataFrame,
    output_type=DataTypes.StreetPriceList
)
def dataframe_to_street_price_list(df: pd.DataFrame) -> List:
    """Transform DataFrame to StreetPriceList using registered schema
    
    Args:
        df: DataFrame with street price data
        
    Returns:
        List of StreetPrice objects
        
    Raises:
        ValueError: If no schema is registered for StreetPriceList
    """
    schema = data_schemas.get_schema(DataTypes.StreetPriceList)
    if schema is None:
        raise ValueError("No schema registered for StreetPriceList")
    
    return schema.convert(df)
