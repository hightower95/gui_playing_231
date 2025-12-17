"""Input parameter definitions"""
from productivity_app.data_pipeline.parameters.input_parameters import (
    Parameter,
    PrimitiveParameter,
    CollectedParameter,
    ChoiceParameter,
    DataSource
)
from productivity_app.data_pipeline.parameters.parameter_enum import ParameterEnum
from productivity_app.data_pipeline.parameters.parameter_registry import parameter_registry

# Populate DataSource with ParameterEnum attributes for backwards compatibility
DataSource.FilePath = ParameterEnum.FilePath
DataSource.InputPath = ParameterEnum.InputPath
DataSource.OutputPath = ParameterEnum.OutputPath
DataSource.PartsList = ParameterEnum.PartsList
DataSource.Strictness = ParameterEnum.Strictness

# For backwards compatibility
InputParameter = Parameter

__all__ = [
    'Parameter',
    'PrimitiveParameter', 
    'CollectedParameter',
    'ChoiceParameter',
    'DataSource',
    'ParameterEnum',
    'parameter_registry',
    'InputParameter'  # Backwards compat
]
