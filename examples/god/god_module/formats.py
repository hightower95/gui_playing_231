"""
Data formats that can be provided and consumed in the pipeline.
"""

from enum import Enum


class DataFormat(str, Enum):
    """Known data formats that can flow through the pipeline"""
    
    # Excel formats
    EXCEL_WORKBOOK = "excel_workbook"
    EXCEL_DATAFRAME = "excel_dataframe"
    
    # CSV formats
    CSV_DATA = "csv_data"
    
    # Generic formats
    DATAFRAME = "dataframe"
    JSON_DATA = "json_data"
    DICT_LIST = "dict_list"
    
    # Reports
    EXCEL_REPORT = "excel_report"
    PDF_REPORT = "pdf_report"
    HTML_REPORT = "html_report"
