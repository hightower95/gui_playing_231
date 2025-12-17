"""
PartsList Parameter - Collected list of Part objects
"""
from productivity_app.data_pipeline.parameters.input_parameters import CollectedParameter
from productivity_app.data_pipeline.parameters.parameter_registry import parameter_registry
from productivity_app.data_pipeline.types_enum import DataTypes


Name = "PartsList"

parameter = CollectedParameter(
    name="parts",
    description="List of Part objects",
    title="Parts List",
    output_type=DataTypes.PartsList
)

# Auto-register on import
parameter_registry.register(Name, parameter)
