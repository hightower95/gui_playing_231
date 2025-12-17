"""
FilePath Parameter - Primitive file path input
"""
from productivity_app.data_pipeline.parameters.input_parameters import PrimitiveParameter
from productivity_app.data_pipeline.parameters.parameter_registry import parameter_registry


Name = "FilePath"

parameter = PrimitiveParameter(
    name="filepath",
    description="Path to file",
    title="File Path"
)

# Auto-register on import
parameter_registry.register(Name, parameter)
