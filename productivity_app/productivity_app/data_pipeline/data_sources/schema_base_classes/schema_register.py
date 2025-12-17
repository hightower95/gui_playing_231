"""
Schema Registry

Centralized registry for data schemas mapped to data types.
"""
from typing import Optional
from productivity_app.data_pipeline.types_enum import DataTypes
from productivity_app.data_pipeline.data_sources.schema_base_classes.data_schema import DataSchema


class _SchemaRegister:
    """Registry for mapping DataTypes to their schemas"""

    def __init__(self):
        self._registry = {}

    def register(self, data_type: DataTypes, schema: DataSchema):
        """Register a schema for a data type

        Args:
            data_type: The data type enum value
            schema: The schema definition
        """
        self._registry[data_type] = schema

    def get_schema(self, data_type: DataTypes) -> Optional[DataSchema]:
        """Get schema for a data type

        Args:
            data_type: The data type enum value

        Returns:
            The schema if registered, None otherwise
        """
        return self._registry.get(data_type)

    def list_schemas(self) -> dict[DataTypes, DataSchema]:
        """Get all registered schemas"""
        return self._registry.copy()


# Global registry instance
data_schemas = _SchemaRegister()
