"""
InputPath Parameter - Primitive input file path
"""
from productivity_app.data_pipeline.parameters.input_parameters import PrimitiveParameter
from productivity_app.data_pipeline.parameters.parameter_registry import parameter_registry


Name = "InputPath"

parameter = PrimitiveParameter(
    name="input_path",
    description="Path to input file",
    title="Input File Path"
)

# Auto-register on import
parameter_registry.register(Name, parameter)
