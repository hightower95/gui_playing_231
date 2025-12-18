"""Data collectors module"""
from productivity_app.data_pipeline.data_collectors.decorator import data_collector

# Import collectors to trigger registration
from productivity_app.data_pipeline.data_collectors import csv_collector
from productivity_app.data_pipeline.data_collectors import generic_excel_collector

__all__ = ['data_collector', 'csv_collector', 'generic_excel_collector']
