"""
Input Parameters - Parameter Hierarchy

Defines parameter types for the data pipeline:
- Parameter: Base class
- PrimitiveParameter: User-provided inputs (FilePath, URL, etc.)
- CollectedParameter: Derived from collectors (PartsList, DataFrame, etc.)
- ChoiceParameter: Parameters with predefined choices

Individual parameters are defined in separate files and auto-register on import.
"""
from dataclasses import dataclass, replace
from typing import Optional, List, Any
from productivity_app.data_pipeline.types_enum import DataTypes


@dataclass(frozen=True)
class Parameter:
    """Base class for all input parameters"""
    name: str
    required: bool = True
    description: str = ""
    title: Optional[str] = None
    is_root: bool = False  # Overridden by subclasses

    def __post_init__(self):
        """Set title to name if not provided"""
        if self.title is None:
            object.__setattr__(self, 'title', self.name)

    def __call__(self, **kwargs):
        """Allow modifying parameters via function call syntax

        Usage:
            FilePath(required=False)
            FilePath(title="Input File")
        """
        return replace(self, **kwargs)


@dataclass(frozen=True)
class PrimitiveParameter(Parameter):
    """Parameter for raw user input (FilePath, URL, etc.)

    These inputs are provided directly by the user, not derived from collectors.
    is_root is True by default.
    """
    is_root: bool = True  # Primitives are always root inputs


@dataclass(frozen=True)
class CollectedParameter(Parameter):
    """Parameter for data derived from collectors (PartsList, DataFrame, etc.)

    These inputs come from running data collectors. The output_type field
    links to the DataType that collectors produce.
    is_root is False by default.
    """
    is_root: bool = False  # Collected parameters are derived
    output_type: Optional[DataTypes] = None  # Maps to collector output


@dataclass(frozen=True)
class ChoiceParameter(Parameter):
    """Parameter with predefined choices (dropdown/select)

    Can be either primitive or collected depending on use case.
    """
    choices: Optional[List[Any]] = None
    multiselect: bool = False
    default: Optional[Any] = None

    def __post_init__(self):
        """Validate default is in choices"""
        super().__post_init__()
        if self.default is not None and self.choices is not None:
            if self.default not in self.choices:
                raise ValueError(
                    f"Default value '{self.default}' not in choices {self.choices}"
                )


# Backwards compatibility: DataSource delegates to ParameterEnum
# Cannot import ParameterEnum here - would cause circular import
# DataSource will be populated in parameters/__init__.py after all imports
class DataSource:
    """Backwards compatible namespace - delegates to ParameterEnum

    DEPRECATED: Use ParameterEnum directly for new code.
    This class is maintained for backwards compatibility with existing code.

    Usage:
        # Old style (still works):
        inputs=[DataSource.FilePath]

        # New style (preferred):
        inputs=[ParameterEnum.FilePath]
    """
    pass  # Will be populated in parameters/__init__.py
