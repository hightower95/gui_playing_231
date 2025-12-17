"""
DEPRECATED: This module is deprecated and will be removed in v2.0

Use the new parameter system instead:
    from productivity_app.data_pipeline.parameters import ParameterEnum
    
Old way:  Source.FileSource("file", FileTypes.CSV)
New way:  ParameterEnum.FilePath
"""
import warnings

warnings.warn(
    "The 'sources' module is deprecated and will be removed in v2.0. "
    "Use 'from productivity_app.data_pipeline.parameters import ParameterEnum' instead. "
    "See MIGRATION.md for details.",
    DeprecationWarning,
    stacklevel=2
)

from productivity_app.data_pipeline.sources.base import Source
from productivity_app.data_pipeline.sources.file_source import FileSourceParameter
from productivity_app.data_pipeline.sources.data_source import DataSourceParameter

__all__ = ['Source', 'FileSourceParameter', 'DataSourceParameter']
