"""
Parameter Enum - Central access point for all parameters

Provides IDE-friendly autocomplete by explicitly importing and exposing
all registered parameters as class attributes.
"""
from productivity_app.data_pipeline.parameters.input_parameters import PrimitiveParameter
from productivity_app.data_pipeline.parameters.file_path import parameter as FilePath
from productivity_app.data_pipeline.parameters.input_path import parameter as InputPath
from productivity_app.data_pipeline.parameters.output_path import parameter as OutputPath
from productivity_app.data_pipeline.parameters.parts_list import parameter as PartsList
from productivity_app.data_pipeline.parameters.strictness import parameter as Strictness


class ParameterEnum:
    """Enumeration of all available parameters

    Usage:
        from productivity_app.data_pipeline.parameters import ParameterEnum

        # In decorator:
        inputs=[ParameterEnum.FilePath]

        # With modification:
        inputs=[ParameterEnum.FilePath(required=False)]

        # In report:
        @report(inputs=[ParameterEnum.PartsList])
    """

    # Primitive parameters (user-provided)
    FilePath: PrimitiveParameter = FilePath
    InputPath: PrimitiveParameter = InputPath
    OutputPath: PrimitiveParameter = OutputPath
    Strictness: PrimitiveParameter = Strictness

    # Collected parameters (from collectors)
    PartsList = PartsList

    # Add new parameters here as they are created
    # Each should be imported above and assigned as a class attribute
