"""
DataSources - Centralized Parameter Definitions

Provides pre-configured parameter definitions that can be used directly
or modified for specific use cases.

Usage:
    # Use default
    parameters=[DataSources.PartsList]
    
    # Or modify
    parameters=[DataSources.PartsList.modify(name="input_parts")]
"""
from productivity_app.productivity_app.data_pipeline.parameters.parts_list import PartsList


class DataSources:
    """Namespace for pre-configured data source parameters"""

    # Parts list parameter
    PartsList = PartsList

    # Add more pre-configured parameters here
    # BOMData = BOMData
    # TestResults = TestResults
