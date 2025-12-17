"""
Data Source Parameter

Represents a data source with type and schema validation.
"""
from dataclasses import dataclass, replace
from typing import Optional
from productivity_app.data_pipeline.sources.base import Source
from productivity_app.data_pipeline.types_enum import DataTypes
from productivity_app.data_pipeline.data_schemas.data_schema import DataSchema


@dataclass(frozen=True)
class DataSourceParameter(Source):
    """Parameter representing a typed data source with schema validation"""
    data_type: DataTypes = None
    schema: Optional[DataSchema] = None

    def validate(self, value) -> bool:
        """Validate value against schema if available

        Args:
            value: Data to validate (typically DataFrame or dict)

        Returns:
            True if valid or no schema defined, False otherwise
        """
        if self.schema is None:
            return True
        return self.schema.validate(value)

    def modify(self, name: str = None, required: bool = None, description: str = None) -> 'DataSourceParameter':
        """Create a modified copy of this parameter

        Args:
            name: New name (optional)
            required: New required status (optional)
            description: New description (optional)

        Returns:
            New DataSourceParameter with modifications
        """
        changes = {}
        if name is not None:
            changes['name'] = name
        if required is not None:
            changes['required'] = required
        if description is not None:
            changes['description'] = description

        if not changes:
            return self

        return replace(self, **changes)
