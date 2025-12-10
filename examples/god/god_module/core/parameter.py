"""
Parameter definition for data providers and reporters.
"""

from typing import Any, Optional
from dataclasses import dataclass


# Sentinel value to distinguish "no default" from "default is None"
_NO_DEFAULT = object()


@dataclass
class Parameter:
    """Defines a parameter required by a data provider or reporter"""

    name: str
    type: type
    default: Any = _NO_DEFAULT
    required: bool = True
    description: str = ""

    def __post_init__(self):
        # If a default value is provided (including None), mark as not required
        if self.default is not _NO_DEFAULT:
            self.required = False

    def get_default(self):
        """Get the default value, or raise if none exists"""
        if self.default is _NO_DEFAULT:
            raise ValueError(f"Parameter '{self.name}' has no default")
        return self.default

    def has_default(self) -> bool:
        """Check if this parameter has a default value"""
        return self.default is not _NO_DEFAULT


def param(name: str, param_type: type, default: Any = _NO_DEFAULT, description: str = "") -> Parameter:
    """
    Helper function to define a parameter.

    Args:
        name: Parameter name
        param_type: Expected type
        default: Default value (makes parameter optional)
        description: Human-readable description

    Returns:
        Parameter definition

    Example:
        param('file_path', str, description='Path to input file')
        param('include_header', bool, default=True)
    """
    return Parameter(
        name=name,
        type=param_type,
        default=default,
        required=not (default is not _NO_DEFAULT),
        description=description
    )
