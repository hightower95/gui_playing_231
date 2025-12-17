"""Data pipeline reports module"""
from productivity_app.data_pipeline.reports import csv_columns
from productivity_app.data_pipeline.reports.register import report_registry


def get_report_by_name(title: str):
    """Get report by name"""
    return report_registry.get_report_by_name(title)


# Import to trigger registration

__all__ = ['get_report_by_name']
