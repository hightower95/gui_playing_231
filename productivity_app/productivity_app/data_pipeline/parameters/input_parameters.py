"""
Input Parameters - Parameter Hierarchy

Defines parameter types for the data pipeline:
- Parameter: Base class with version support
- PrimitiveParameter: User-provided inputs (FilePath, URL, etc.)
- CollectedParameter: Derived from collectors (PartsList, DataFrame, etc.)
- ChoiceParameter: Parameters with predefined choices

Individual parameters are defined in separate files and auto-register on import.
"""
from dataclasses import dataclass, replace
from typing import Optional, List, Any


@dataclass(frozen=True)
class Parameter:
    """Base class for all input parameters with version support"""
    name: str
    required: bool = True
    description: str = ""
    title: Optional[str] = None
    is_root: bool = False  # Overridden by subclasses
    # Version metadata for compatibility tracking
    version: Optional[str] = None

    def __post_init__(self):
        """Set title to name if not provided"""
        if self.title is None:
            object.__setattr__(self, 'title', self.name)

    def __call__(self, **kwargs):
        """Allow modifying parameters via function call syntax

        Usage:
            FilePath(required=False)
            FilePath(title="Input File")
            PartsList(version="5")
        """
        return replace(self, **kwargs)

    def matches(self, other: 'Parameter') -> bool:
        """Check if this parameter matches another (for routing)

        Matches if names are the same and versions are compatible.
        None version matches any version.

        Args:
            other: Parameter to compare against

        Returns:
            True if parameters are compatible
        """
        if self.name != other.name:
            return False

        # If either has no version requirement, they match
        if self.version is None or other.version is None:
            return True

        # For now, exact version match (can extend with semver later)
        return self.version == other.version

    def get_type_key(self) -> str:
        """Get unique type key for registry lookups

        Returns:
            String key like 'PartsList' or 'PartsList_v5'
        """
        if self.version:
            return f"{self.name}_v{self.version}"
        return self.name


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

    These inputs come from running data collectors.
    is_root is False by default.
    """
    is_root: bool = False  # Collected parameters are derived


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
