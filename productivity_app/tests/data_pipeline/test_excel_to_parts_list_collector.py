"""
Tests for excel_to_parts_list_collector
"""
import pytest
import pandas as pd
from pathlib import Path
from productivity_app.data_pipeline.data_collectors.excel_to_parts_list import excel_to_parts_list_collector
from productivity_app.productivity_app.data_pipeline.data_collectors.register import collector_registry
from productivity_app.data_pipeline.types_enum import DataTypes
from productivity_app.data_pipeline.models.part import Part


@pytest.fixture
def sample_excel_file(tmp_path):
    """Create a sample Excel file with parts data"""
    df = pd.DataFrame({
        "Part Name": ["Resistor", "Capacitor"],
        "Part Number": ["R001", "C001"],
        "Description": ["10k ohm", "100uF"],
        "Quantity": [100, 50],
        "Unit Cost": [0.10, 0.25]
    })

    filepath = tmp_path / "parts.xlsx"
    df.to_excel(filepath, index=False)
    return filepath


def test_excel_to_parts_list_returns_part_objects(sample_excel_file):
    """Collector returns list of Part objects"""
    parts = excel_to_parts_list_collector(sample_excel_file)

    assert len(parts) == 2
    assert all(isinstance(p, Part) for p in parts)


def test_excel_to_parts_list_has_correct_data(sample_excel_file):
    """Parts have correct data from Excel"""
    parts = excel_to_parts_list_collector(sample_excel_file)

    assert parts[0].part_name == "Resistor"
    assert parts[0].part_number == "R001"
    assert parts[0].quantity == 100

    assert parts[1].part_name == "Capacitor"
    assert parts[1].part_number == "C001"


def test_excel_to_parts_list_registered():
    """Collector is registered in registry"""
    collectors = collector_registry.get_collectors_for_type(
        DataTypes.PartsList)

    assert "ExcelToPartsListCollector" in collectors


def test_excel_to_parts_list_validates_schema(tmp_path):
    """Collector rejects Excel missing required columns"""
    df = pd.DataFrame({
        "Part Name": ["Resistor"],
        # Missing Part Number!
    })

    filepath = tmp_path / "invalid_parts.xlsx"
    df.to_excel(filepath, index=False)

    with pytest.raises(ValueError, match="Schema validation failed"):
        excel_to_parts_list_collector(filepath)
