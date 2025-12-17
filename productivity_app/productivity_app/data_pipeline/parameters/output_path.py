"""
OutputPath Parameter - Primitive output file path (optional)
"""
from productivity_app.data_pipeline.parameters.input_parameters import PrimitiveParameter
from productivity_app.data_pipeline.parameters.parameter_registry import parameter_registry


parameter = parameter_registry.define_parameter(
    name="OutputPath",
    parameter=PrimitiveParameter(
        name="output_path",
        required=False,
        description="Path to output file",
        title="Output File Path"
    )
)
