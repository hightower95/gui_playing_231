"""
Parts List Parameter Definition

Example of how to define a reusable parameter with a schema.
The schema defines the expected columns in the parts list data.

Usage:
    # Use default parameter
    DataSources.PartsList
    
    # Or modify specific fields
    DataSources.PartsList.modify(name="custom_parts", description="Custom description")
"""
from typing import List
import pandas as pd
from productivity_app.data_pipeline.types_enum import DataTypes
from productivity_app.data_pipeline.schemas import DataSchema, data_schemas
from productivity_app.data_pipeline.sources.base import Source
from productivity_app.data_pipeline.models.part import Part


def _dataframe_to_parts(df: pd.DataFrame) -> List[Part]:
    """Convert DataFrame to list of Part objects"""
    parts = []
    for _, row in df.iterrows():
        part = Part(
            part_name=row.get("Part Name"),
            part_number=row.get("Part Number"),
            description=row.get("Description"),
            quantity=row.get("Quantity"),
            unit_cost=row.get("Unit Cost")
        )
        parts.append(part)
    return parts


# Define the schema for parts list data
PARTS_LIST_SCHEMA = DataSchema(
    name="PartsList",
    required_columns=["Part Name", "Part Number"],
    optional_columns=["Description", "Quantity", "Unit Cost"],
    description="Schema for parts list with part names and numbers",
    converter=_dataframe_to_parts
)

# Register the schema in the global registry
data_schemas.register(DataTypes.PartsList, PARTS_LIST_SCHEMA)

# Create a default PartsList parameter instance
# This can be used directly or modified
PartsList = Source.DataSource(
    name="parts_list",
    data_type=DataTypes.PartsList,
    required=True,
    description="Parts list data source"
    # schema is auto-loaded from registry
)
