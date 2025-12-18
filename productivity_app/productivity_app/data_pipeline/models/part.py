"""
Unified Part Model Definition - Model + Schema + Parameter in one place

This approach co-locates the model definition with its schema and parameter,
making it easier to see the complete data pipeline definition.
"""
from dataclasses import dataclass
from typing import Optional

from productivity_app.data_pipeline.data_sources.schema_inference import infer_schema_from_dataclass
from productivity_app.data_pipeline.data_sources.schema_base_classes.schema_register import data_schemas
from productivity_app.data_pipeline.parameters.input_parameters import CollectedParameter
from productivity_app.data_pipeline.parameters.parameter_registry import parameter_registry


@dataclass
class Part:
    """Single part in a parts list"""
    part_name: str
    part_number: str
    description: Optional[str] = None
    quantity: Optional[int] = None
    unit_cost: Optional[float] = None


# Auto-generate schema
_PARTS_LIST_SCHEMA = infer_schema_from_dataclass(
    Part,
    name="PartsList",
    description="Schema for parts list with part names and numbers"
)


# Define parameter using composition (no custom class needed)
PartsList = parameter_registry.define_parameter(
    name="PartsList",
    parameter=CollectedParameter(
        name='parts',
        description='List of Part objects',
        title='Parts List'
    )
)


# Register schema with parameter AFTER parameter is created
data_schemas.register(PartsList, _PARTS_LIST_SCHEMA)


# Export both the model and the parameter
__all__ = ['Part', 'PartsList']
