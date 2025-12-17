import pandas as pd
from models.part import Part
from framework import DataTypes, Source
from framework.schema import DataSchema
from framework.registry import data_schemas

_COLUMN_MAP = {
    "Part Name": "part_name",
    "Part Number": "part_number",
    "Description": "description",
    "Quantity": "quantity",
    "Unit Cost": "unit_cost",
}


def _dataframe_to_parts(df: pd.DataFrame) -> list[Part]:
    parts = []

    for _, row in df.iterrows():
        kwargs = {
            model_field: row[col]
            for col, model_field in _COLUMN_MAP.items()
            if col in row and not pd.isna(row[col])
        }
        parts.append(Part(**kwargs))

    return parts


PARTS_LIST_SCHEMA = DataSchema(
    name="PartsList",
    required_columns=["Part Name", "Part Number"],
    optional_columns=["Description", "Quantity", "Unit Cost"],
    description="Schema for parts list with part names and numbers",
    converter=_dataframe_to_parts,
)

data_schemas.register(DataTypes.PartsList, PARTS_LIST_SCHEMA)

PartsList = Source.DataSource(
    name="parts_list",
    data_type=DataTypes.PartsList,
    required=True,
    description="Parts list data source",
)
