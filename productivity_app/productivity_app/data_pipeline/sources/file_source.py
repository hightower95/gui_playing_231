"""
File Source Parameter

Represents a file-based data source with optional schema validation.
"""
from dataclasses import dataclass
from typing import Optional
from productivity_app.data_pipeline.sources.base import Source
from productivity_app.data_pipeline.types_enum import FileTypes
from productivity_app.data_pipeline.data_schemas.file_schema import FileSchema


@dataclass(frozen=True)
class FileSourceParameter(Source):
    """Parameter representing a file source with schema validation"""
    file_type: FileTypes = None
    schema: Optional[FileSchema] = None

    def validate(self, value) -> bool:
        """Validate file against schema if available

        Args:
            value: File data to validate (typically DataFrame or file path)

        Returns:
            True if valid or no schema defined, False otherwise
        """
        if self.schema is None:
            return True
        return self.schema.validate(value)
