"""
Data Pipeline - Public API

Recommended usage:
    from productivity_app.data_pipeline import ParameterEnum, DataTypes
    from productivity_app.data_pipeline.reports.decorator import report
    from productivity_app.data_pipeline.data_collectors.decorator import data_collector

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

__all__ = ['ParameterEnum', 'DataTypes', 'FileTypes', 'registry']
