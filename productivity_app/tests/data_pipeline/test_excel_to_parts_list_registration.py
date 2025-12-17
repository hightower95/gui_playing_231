"""
Test that ExcelToPartsListCollector is properly registered
"""
from productivity_app.productivity_app.data_pipeline.data_collectors.register import collector_registry
from productivity_app.data_pipeline.types_enum import DataTypes
from productivity_app.data_pipeline.parameters.input_parameters import DataSource
# Import to trigger registration
from productivity_app.data_pipeline.data_collectors import excel_to_parts_list


def test_excel_to_parts_list_collector_is_registered():
    """ExcelToPartsListCollector exists in registry"""
    collector = collector_registry.get_collector("ExcelToPartsListCollector")

    assert collector is not None


def test_excel_to_parts_list_collector_has_filepath_input():
    """Collector expects FilePath as input"""
    collector = collector_registry.get_collector("ExcelToPartsListCollector")

    assert DataSource.FilePath in collector['inputs']


def test_excel_to_parts_list_collector_outputs_partslist():
    """Collector promises to return PartsList"""
    collector = collector_registry.get_collector("ExcelToPartsListCollector")

    assert DataTypes.PartsList in collector['outputs']


def test_excel_to_parts_list_collector_discoverable_by_type():
    """Can find ExcelToPartsListCollector by querying for PartsList providers"""
    collectors = collector_registry.get_collectors_for_type(
        DataTypes.PartsList)

    assert "ExcelToPartsListCollector" in collectors
