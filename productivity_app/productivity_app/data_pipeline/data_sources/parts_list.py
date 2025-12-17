import pandas as pd
from productivity_app.data_pipeline.models.part import Part
from productivity_app.data_pipeline.types_enum import DataTypes
from productivity_app.data_pipeline.data_sources.schema_base_classes import DataSchema
from productivity_app.data_pipeline.data_sources.schema_base_classes.schema_register import data_schemas

_COLUMN_MAP = {
    # Support both Title Case (with spaces) and snake_case
    "Part Name": "part_name",
    "part_name": "part_name",
    "Part Number": "part_number",
    "part_number": "part_number",
    "Description": "description",
    "description": "description",
    "Quantity": "quantity",
    "quantity": "quantity",
    "Unit Cost": "unit_cost",
    "unit_cost": "unit_cost",
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
    required_columns=["part_name", "part_number"],  # Support snake_case
    optional_columns=["description", "quantity", "unit_cost"],
    description="Schema for parts list with part names and numbers",
    converter=_dataframe_to_parts,
)

data_schemas.register(DataTypes.PartsList, PARTS_LIST_SCHEMA)
# PartsList = CollectedParameter(
#     name="parts_list",
#     data_type=DataTypes.PartsList,
#     required=True,
#     description="Parts list data source",
# )
# TODO: Sources.AddSource(PartsList)
