"""
Data Pipeline - Public API

Recommended usage:
    from productivity_app.data_pipeline import ParameterEnum, DataTypes
    from productivity_app.data_pipeline.reports.decorator import report
    from productivity_app.data_pipeline.data_collectors.decorator import data_collector
    from productivity_app.data_pipeline.data_transformers.decorator import data_transformer

Example report:
    @report(
        title="My Report",
        description="Description here",
        inputs=[ParameterEnum.FilePath]
    )
    def my_report(filepath: str):
        return f"Processed {filepath}"
"""
from productivity_app.data_pipeline.parameters import ParameterEnum
from productivity_app.data_pipeline.types_enum import DataTypes, FileTypes
from productivity_app.data_pipeline.registry import registry

# Import collectors and transformers to trigger registration
import productivity_app.data_pipeline.data_collectors
import productivity_app.data_pipeline.models.alt_street_price  # Includes transformer
import productivity_app.data_pipeline.data_transformers.dataframe_to_parts_list

__all__ = ['ParameterEnum', 'DataTypes', 'FileTypes', 'registry']
