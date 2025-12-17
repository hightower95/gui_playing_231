"""
Parameter Registry

Singleton registry for managing all input parameters.
Automatically populated when parameter modules are imported.
"""
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from productivity_app.data_pipeline.parameters.input_parameters import (
        Parameter,
        PrimitiveParameter,
        CollectedParameter
    )


class ParameterRegistry:
    """Singleton registry for input parameters

    Why?
    We can check that all parameters have a unique name, and allow new runtime additions without conflicts.

    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._registry: Dict[str, 'Parameter'] = {}

    def register(self, name: str, parameter: 'Parameter'):
        """Register a parameter

        Args:
            name: Parameter identifier (e.g., 'FilePath', 'PartsList')
            parameter: Parameter instance

        Raises:
            ValueError: If parameter with this name already registered
        """
        if name in self._registry:
            raise ValueError(
                f"Parameter '{name}' is already registered. "
                f"Existing: {self._registry[name]}, "
                f"New: {parameter}"
            )
        self._registry[name] = parameter

    def define_parameter(self, name: str, parameter: 'Parameter') -> 'Parameter':
        """Define and register a parameter in one call

        Convenience function for parameter definition files.

        Args:
            name: Parameter identifier (e.g., 'FilePath', 'PartsList')
            parameter: Parameter instance

        Returns:
            The registered parameter (for assignment to module variable)

        Raises:
            ValueError: If parameter with this name already registered
        """
        self.register(name, parameter)
        return parameter

    def get(self, name: str) -> Optional['Parameter']:
        """Get parameter by name

        Args:
            name: Parameter identifier

        Returns:
            Parameter instance or None if not found
        """
        return self._registry.get(name)

    def get_all_parameters(self) -> Dict[str, 'Parameter']:
        """Get all registered parameters

        Returns:
            Dictionary of name -> parameter
        """
        return self._registry.copy()

    def get_primitives(self) -> List['PrimitiveParameter']:
        """Get all primitive parameters (user-provided inputs)

        Returns:
            List of PrimitiveParameter instances
        """
        from productivity_app.data_pipeline.parameters.input_parameters import PrimitiveParameter
        return [
            p for p in self._registry.values()
            if isinstance(p, PrimitiveParameter)
        ]

    def get_collected(self) -> List['CollectedParameter']:
        """Get all collected parameters (derived from collectors)

        Returns:
            List of CollectedParameter instances
        """
        from productivity_app.data_pipeline.parameters.input_parameters import CollectedParameter
        return [
            p for p in self._registry.values()
            if isinstance(p, CollectedParameter)
        ]

    def clear(self):
        """Clear all registered parameters (useful for testing)"""
        self._registry.clear()


# Global singleton instance
parameter_registry = ParameterRegistry()
