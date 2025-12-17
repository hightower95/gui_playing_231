"""Input parameter definitions"""
from productivity_app.data_pipeline.parameters.input_parameters import (
    Parameter,
    PrimitiveParameter,
    CollectedParameter,
    ChoiceParameter
)
from productivity_app.data_pipeline.parameters.parameter_enum import ParameterEnum
from productivity_app.data_pipeline.parameters.parameter_registry import ParameterRegistry

# Main export - clearer name for users
Variables = ParameterEnum

# For backwards compatibility
InputParameter = Parameter
ParameterEnum = ParameterEnum  # Keep old name working

# For convenience - type aliases to PrimitiveParameter
FilePath = PrimitiveParameter
InputPath = PrimitiveParameter
OutputPath = PrimitiveParameter

__all__ = [
    'Variables',  # Primary interface
    'Parameter',
    'PrimitiveParameter',
    'CollectedParameter',
    'ChoiceParameter',
    'ParameterEnum',  # Backwards compat
    'ParameterRegistry',
    'InputParameter',  # Backwards compat
    'FilePath',  # Convenience
    'InputPath',  # Convenience
    'OutputPath',  # Convenience
]
