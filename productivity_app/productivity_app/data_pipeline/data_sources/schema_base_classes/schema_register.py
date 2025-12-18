"""
Schema Registry

Centralized registry for data schemas mapped to parameter types.
"""
from typing import Optional
from productivity_app.data_pipeline.parameters.input_parameters import Parameter
from productivity_app.data_pipeline.data_sources.schema_base_classes.data_schema import DataSchema


class _SchemaRegister:
    """Registry for mapping Parameters to their schemas"""

    def __init__(self):
        self._registry = {}

    def register(self, param_type: Parameter, schema: DataSchema):
        """Register a schema for a parameter type

        Args:
            param_type: The parameter type
            schema: The schema definition
        """
        type_key = param_type.get_type_key()
        self._registry[type_key] = schema

    def get_schema(self, param_type: Parameter) -> Optional[DataSchema]:
        """Get schema for a parameter type

        Args:
            param_type: The parameter type

        Returns:
            The schema if registered, None otherwise
        """
        type_key = param_type.get_type_key()
        return self._registry.get(type_key)

    def list_schemas(self) -> dict[str, DataSchema]:
        """Get all registered schemas"""
        return self._registry.copy()


# Global registry instance
data_schemas = _SchemaRegister()
