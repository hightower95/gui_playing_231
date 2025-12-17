"""
Input Parameters - Common Input Types

Defines common input parameter types like FilePath that can be used
in collector inputs with optional modifiers.

Usage:
    # Simple filepath input
    inputs=[DataSource.FilePath]
    
    # Optional filepath
    inputs=[DataSource.FilePath(required=False)]
"""
from dataclasses import dataclass, replace
from typing import Optional


@dataclass(frozen=True)
class InputParameter:
    """Base class for input parameters"""
    name: str
    required: bool = True
    description: str = ""
    title: Optional[str] = None

    def __post_init__(self):
        """Set title to name if not provided"""
        if self.title is None:
            object.__setattr__(self, 'title', self.name)

    def __call__(self, **kwargs):
        """Allow modifying parameters via function call syntax"""
        return replace(self, **kwargs)


class DataSource:
    """Namespace for common input parameter types"""

    FilePath = InputParameter(
        name="filepath",
        required=True,
        description="Path to file"
    )

    InputPath = InputParameter(
        name="input_path",
        required=True,
        description="Path to input file"
    )

    OutputPath = InputParameter(
        name="output_path",
        required=True,
        description="Path to output file"
    )

    # Add more common inputs here
    # DirectoryPath = InputParameter(name="dirpath", required=True, description="Path to directory")
    # ConfigDict = InputParameter(name="config", required=True, description="Configuration dictionary")
