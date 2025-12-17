"""
Base Source Classes

Abstract base for all parameter sources (File, Data, etc.)
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from productivity_app.data_pipeline.types_enum import DataTypes, FileTypes


@dataclass(frozen=True)
class Source(ABC):
    """Abstract base class for all data sources"""
    name: str
    required: bool = True
    description: str = ""

    @abstractmethod
    def validate(self, value) -> bool:
        """Validate a value against this source's constraints"""
        pass

    @staticmethod
    def FileSource(name: str, file_type: FileTypes, schema=None, **kwargs):
        """Factory method for creating file source parameters

        Args:
            name: Parameter name
            file_type: Type of file (from FileTypes enum)
            schema: FileSchema defining expected structure (optional)
            **kwargs: Additional parameters (required, description, etc.)

        Returns:
            FileSourceParameter instance
        """
        from productivity_app.data_pipeline.sources.file_source import FileSourceParameter
        return FileSourceParameter(
            name=name,
            file_type=file_type,
            schema=schema,
            **kwargs
        )

    @staticmethod
    def DataSource(name: str, data_type: DataTypes, schema=None, **kwargs):
        """Factory method for creating data source parameters

        Args:
            name: Parameter name
            data_type: Type of data (from DataTypes enum)
            schema: DataSchema defining expected structure (optional, auto-loaded from registry)
            **kwargs: Additional parameters (required, description, etc.)

        Returns:
            DataSourceParameter instance
        """
        from productivity_app.data_pipeline.sources.data_source import DataSourceParameter
        from productivity_app.data_pipeline.data_sources.schema_base_classes.schema_register import data_schemas

        # Auto-fetch schema from registry if not provided
        if schema is None:
            schema = data_schemas.get_schema(data_type)

        return DataSourceParameter(
            name=name,
            data_type=data_type,
            schema=schema,
            **kwargs
        )
