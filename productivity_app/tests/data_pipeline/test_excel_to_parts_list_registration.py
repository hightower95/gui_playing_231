"""
Test parameter resolution architecture (collector-schema separation)

NOTE: This file previously tested ExcelToPartsListCollector registration.
That collector has been deprecated as part of the collector-schema separation refactoring.

New architecture:
- Transport collectors (CSV, Excel) return DataFrames
- Schemas handle DataFrame → Model conversion
- Parameter resolution composes them

See test_excel_to_parts_list_collector.py for functional tests of the new pattern.
"""
import pytest
from productivity_app.data_pipeline.data_collectors.register import collector_registry
from productivity_app.data_pipeline.types_enum import DataTypes


@pytest.mark.skip(reason="ExcelToPartsListCollector deprecated - use parameter resolution")
def test_excel_to_parts_list_collector_is_registered():
    """DEPRECATED: ExcelToPartsListCollector no longer exists"""
    pass


@pytest.mark.skip(reason="ExcelToPartsListCollector deprecated - use parameter resolution")
def test_excel_to_parts_list_collector_has_filepath_input():
    """DEPRECATED: ExcelToPartsListCollector no longer exists"""
    pass


@pytest.mark.skip(reason="ExcelToPartsListCollector deprecated - use parameter resolution")
def test_excel_to_parts_list_collector_outputs_partslist():
    """DEPRECATED: ExcelToPartsListCollector no longer exists"""
    pass


@pytest.mark.skip(reason="ExcelToPartsListCollector deprecated - use parameter resolution")
def test_excel_to_parts_list_collector_discoverable_by_type():
    """DEPRECATED: Model-specific collectors no longer registered"""
    pass
