"""
Test that ExcelToPartsListCollector is properly registered
"""
from productivity_app.data_pipeline.data_collectors.collector_registry import collector_registry
from productivity_app.data_pipeline.types_enum import DataTypes
# Import to trigger registration
from productivity_app.data_pipeline.data_collectors import excel_to_parts_list


def test_excel_to_parts_list_collector_is_registered():
    """ExcelToPartsListCollector exists in registry"""
    collector = collector_registry.get_collector("ExcelToPartsListCollector")
    
    assert collector is not None


def test_excel_to_parts_list_collector_has_filepath_input():
    """Collector expects filepath as input"""
    collector = collector_registry.get_collector("ExcelToPartsListCollector")
    
    assert "filepath" in collector['inputs']


def test_excel_to_parts_list_collector_outputs_partslist():
    """Collector promises to return PartsList"""
    collector = collector_registry.get_collector("ExcelToPartsListCollector")
    
    assert DataTypes.PartsList in collector['outputs']


def test_excel_to_parts_list_collector_discoverable_by_type():
    """Can find ExcelToPartsListCollector by querying for PartsList providers"""
    collectors = collector_registry.get_collectors_for_type(DataTypes.PartsList)
    
    assert "ExcelToPartsListCollector" in collectors
