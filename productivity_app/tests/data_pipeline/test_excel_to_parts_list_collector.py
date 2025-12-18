"""
Tests for parameter resolution from Excel files

Tests the new collector-schema separation pattern where:
- Generic Excel collector handles transport (file → DataFrame)
- Schema handles conversion (DataFrame → Part objects)
- Parameter resolution composes them
"""
import pytest
import pandas as pd
from pathlib import Path
from productivity_app.data_pipeline.parameters.resolution import resolve_parts_list_from_file
from productivity_app.data_pipeline.models.part import Part


@pytest.fixture
def sample_excel_file(tmp_path):
    """Create a sample Excel file with parts data"""
    df = pd.DataFrame({
        "part_name": ["Resistor", "Capacitor"],
        "part_number": ["R001", "C001"],
        "description": ["10k ohm", "100uF"],
        "quantity": [100, 50],
        "unit_cost": [0.10, 0.25]
    })

    filepath = tmp_path / "parts.xlsx"
    df.to_excel(filepath, index=False)
    return filepath


def test_resolve_parts_list_from_excel(sample_excel_file):
    """Parameter resolution returns list of Part objects from Excel"""
    parts = resolve_parts_list_from_file(str(sample_excel_file))

    assert len(parts) == 2
    assert all(isinstance(p, Part) for p in parts)


def test_resolved_parts_have_correct_data(sample_excel_file):
    """Parts have correct data from Excel"""
    parts = resolve_parts_list_from_file(str(sample_excel_file))

    assert parts[0].part_name == "Resistor"
    assert parts[0].part_number == "R001"
    assert parts[0].quantity == 100

    assert parts[1].part_name == "Capacitor"
    assert parts[1].part_number == "C001"


def test_resolve_parts_list_validates_schema(tmp_path):
    """Resolution rejects Excel missing required columns"""
    df = pd.DataFrame({
        "Part Name": ["Resistor"],
        # Missing part_number!
    })

    filepath = tmp_path / "invalid_parts.xlsx"
    df.to_excel(filepath, index=False)

    with pytest.raises(ValueError):
        resolve_parts_list_from_file(str(filepath))
