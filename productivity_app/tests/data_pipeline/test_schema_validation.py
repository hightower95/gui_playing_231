"""
Test DataSchema validates columns of different data types
"""
import pytest
import pandas as pd
from productivity_app.data_pipeline.data_schemas import DataSchema


def test_dataschema_validates_dataframe():
    """DataSchema can validate DataFrame columns"""
    schema = DataSchema(
        name="TestSchema",
        required_columns=["Name", "ID"],
        optional_columns=["Value"]
    )

    df = pd.DataFrame({
        "Name": ["A", "B"],
        "ID": [1, 2],
        "Value": [10, 20]
    })

    is_valid = schema.validate(df)
    assert is_valid
    # assert len(errors) == 0


def test_dataschema_validates_dict():
    """DataSchema can validate dict columns"""
    schema = DataSchema(
        name="TestSchema",
        required_columns=["Name", "ID"]
    )

    data = {"Name": ["A"], "ID": [1]}

    is_valid = schema.validate(data)
    assert is_valid
    # assert len(errors) == 0


def test_dataschema_detects_missing_required():
    """DataSchema detects missing required columns"""
    schema = DataSchema(
        name="TestSchema",
        required_columns=["Name", "ID"]
    )

    df = pd.DataFrame({"Name": ["A"]})  # Missing ID

    is_valid = schema.validate(df)
    assert not is_valid
    # assert "ID" in errors[0]
