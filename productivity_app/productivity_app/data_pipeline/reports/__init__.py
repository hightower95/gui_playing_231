"""Data pipeline reports module"""
from productivity_app.data_pipeline.reports import csv_columns
from productivity_app.data_pipeline.reports.register import report_registry
from productivity_app.data_pipeline.reports.decorator import report


def get_report_by_name(title: str):
    """Get report by name"""
    return report_registry.get_report_by_name(title)


def get_all_reports():
    """Get all registered reports as wrappers
    
    Returns:
        List of ReportWrapper objects
    """
    return report_registry.get_all_reports()


# Import to trigger registration

__all__ = ['report', 'get_report_by_name', 'get_all_reports']
