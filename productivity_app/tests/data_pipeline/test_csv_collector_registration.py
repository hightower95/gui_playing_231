"""
Test that CSVCollector is properly registered and callable
"""
import pytest
import pandas as pd
from pathlib import Path
from productivity_app.data_pipeline.data_collectors.register import collector_registry
from productivity_app.data_pipeline.types_enum import DataTypes
from productivity_app.data_pipeline.parameters.input_parameters import DataSource
# Import to trigger registration
# from productivity_app.data_pipeline.data_collectors import csv_collector


@pytest.fixture
def dummy_csv(tmp_path):
    """Create a dummy CSV file"""
    csv_path = tmp_path / "test.csv"
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': ['x', 'y', 'z']
    })
    df.to_csv(csv_path, index=False)
    return str(csv_path)


def test_csv_collector_is_registered():
    """CSVCollector appears in registry"""
    collector = collector_registry.get_collector("CSVCollector")

    assert collector is not None


def test_csv_collector_has_filepath_input():
    """CSVCollector expects FilePath input"""
    collector = collector_registry.get_collector("CSVCollector")

    assert DataSource.FilePath in collector['inputs']


def test_csv_collector_outputs_dataframe():
    """CSVCollector outputs DataFrame"""
    collector = collector_registry.get_collector("CSVCollector")

    assert DataTypes.DataFrame in collector['outputs']


def test_get_collector_by_name_and_call(dummy_csv):
    """Can get collector by name and call it"""
    # Get the actual callable function
    collector = collector_registry.get_collector_by_name("CSVCollector")

    assert collector is not None

    # Call it with dummy CSV
    result = collector(dummy_csv)

    # Verify result is a DataFrame
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 3
    assert list(result.columns) == ['A', 'B']
    assert result['A'].tolist() == [1, 2, 3]
