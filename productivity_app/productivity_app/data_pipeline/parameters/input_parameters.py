"""
Input Parameters - Common Input Types

Defines common input parameter types like FilePath that can be used
in collector inputs with optional modifiers.

Usage:
    # Simple filepath input
    inputs=[DataSource.FilePath]
    
    # Optional filepath
    inputs=[DataSource.FilePath(required=False)]
    
    # Choice parameter
    inputs=[DataSource.Strictness]
"""
from dataclasses import dataclass, replace
from typing import Optional, List, Any


@dataclass(frozen=True)
class InputParameter:
    """Base class for input parameters"""
    name: str
    required: bool = True
    description: str = ""
    title: Optional[str] = None
    is_root: bool = False  # True for primitive inputs like FilePath

    def __post_init__(self):
        """Set title to name if not provided"""
        if self.title is None:
            object.__setattr__(self, 'title', self.name)

    def __call__(self, **kwargs):
        """Allow modifying parameters via function call syntax"""
        return replace(self, **kwargs)


@dataclass(frozen=True)
class ChoiceParameter(InputParameter):
    """Parameter with predefined choices (dropdown/select)"""
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


class DataSource:
    """Namespace for common input parameter types"""

    FilePath = InputParameter(
        name="filepath",
        description="Path to file",
        is_root=True  # Root input - user provides directly
    )

    InputPath = InputParameter(
        name="input_path",
        title="Input File Path",
        description="Path to input file",
        is_root=True  # Root input - user provides directly
    )

    OutputPath = InputParameter(
        name="output_path",
        title="Output File Path",
        required=False,
        description="Path to output file",
        is_root=True  # Root input - user provides directly
    )

    Strictness = ChoiceParameter(
        name="strictness",
        required=False,
        description="Validation strictness level",
        title="Strictness Level",
        choices=["strict", "moderate", "lenient"],
        default="moderate"
    )

    # In input_parameters.py
    PartsList = InputParameter(
        name="parts",
        description="List of Part objects",
        title="Parts List",
        is_root=False  # Derived input - comes from collectors
    )

    # Add more common inputs here
    # DirectoryPath = InputParameter(name="dirpath", required=True, description="Path to directory")
    # ConfigDict = InputParameter(name="config", required=True, description="Configuration dictionary")
