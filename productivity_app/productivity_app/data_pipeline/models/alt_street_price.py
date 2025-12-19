"""
Unified Model Definition - Model + Schema + Parameter + Transformer in one place

This approach co-locates the model definition with its schema, parameter, and transformer,
making it easier to see the complete data pipeline definition.
"""
from dataclasses import dataclass
import pandas as pd
from typing import List

from productivity_app.data_pipeline.data_sources.schema_inference import infer_schema_from_dataclass
from productivity_app.data_pipeline.data_sources.schema_base_classes.schema_register import data_schemas
from productivity_app.data_pipeline.parameters.input_parameters import CollectedParameter
from productivity_app.data_pipeline.parameters.parameter_registry import parameter_registry
from productivity_app.data_pipeline.data_transformers.decorator import data_transformer


@dataclass
class StreetPrice:
    """House price data for a specific street"""
    street: str
    town: str
    price: int


# Auto-generate schema
_STREET_PRICE_SCHEMA = infer_schema_from_dataclass(
    StreetPrice,
    name="StreetPrice",
    description="Schema for street price data with street, town, and price"
)


# Define parameter using composition (no custom class needed)
StreetPriceList = parameter_registry.define_parameter(
    name="StreetPriceList",
    parameter=CollectedParameter(
        name='street_prices',
        description='List of StreetPrice objects',
        title='Street Prices'
    )
)


# Register schema with parameter AFTER parameter is created
data_schemas.register(StreetPriceList, _STREET_PRICE_SCHEMA)


# Define transformer function (decorator applied lazily at first use)
def dataframe_to_street_price_list(df: pd.DataFrame) -> List[StreetPrice]:
    """Transform DataFrame to StreetPriceList using registered schema

    Args:
        df: DataFrame with street price data

    Returns:
        List of StreetPrice objects

    Raises:
        ValueError: If no schema is registered for StreetPriceList
    """
    from productivity_app.data_pipeline.parameters import Variables
    schema = data_schemas.get_schema(Variables.StreetPriceList)
    if schema is None:
        raise ValueError("No schema registered for StreetPriceList")

    return schema.convert(df)


# Register transformer when this module is explicitly imported (not during parameter_enum import)
# This happens later when the system loads transformers
if __name__ != '__main__':
    try:
        from productivity_app.data_pipeline.parameters import Variables
        from productivity_app.data_pipeline.data_transformers.decorator import data_transformer
        dataframe_to_street_price_list = data_transformer(
            name="DataFrameToStreetPriceList",
            input_type=Variables.DataFrame,
            output_type=Variables.StreetPriceList
        )(dataframe_to_street_price_list)
    except ImportError:
        # Variables not ready yet, transformer will register when called
        pass


# Export the model, parameter, and transformer
__all__ = ['StreetPrice', 'StreetPriceList', 'dataframe_to_street_price_list']
