"""
Unified Model Definition - Model + Schema + Parameter in one place

This approach co-locates the model definition with its schema and parameter,
making it easier to see the complete data pipeline definition.
"""
from dataclasses import dataclass

from productivity_app.data_pipeline.types_enum import DataTypes
from productivity_app.data_pipeline.data_sources.schema_inference import infer_schema_from_dataclass
from productivity_app.data_pipeline.data_sources.schema_base_classes.schema_register import data_schemas
from productivity_app.data_pipeline.parameters.input_parameters import CollectedParameter
from productivity_app.data_pipeline.parameters.parameter_registry import parameter_registry


@dataclass
class StreetPrice:
    """House price data for a specific street"""
    street: str
    town: str
    price: int


# Auto-generate and register schema on import
_STREET_PRICE_SCHEMA = infer_schema_from_dataclass(
    StreetPrice,
    name="StreetPrice",
    description="Schema for street price data with street, town, and price"
)
data_schemas.register(DataTypes.StreetPriceList, _STREET_PRICE_SCHEMA)


# Define parameter using composition (no custom class needed)
StreetPriceList = parameter_registry.define_parameter(
    name="StreetPriceList",
    parameter=CollectedParameter(
        name='street_prices',
        description='List of StreetPrice objects',
        title='Street Prices',
        output_type=DataTypes.StreetPriceList
    )
)


# Export both the model and the parameter
__all__ = ['StreetPrice', 'StreetPriceList']
