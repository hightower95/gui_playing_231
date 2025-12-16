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
from productivity_app.data_pipeline.types_enum import DataTypes
from productivity_app.data_pipeline.schemas import DataSchema, data_schemas
from productivity_app.data_pipeline.sources.base import Source


# Define the schema for parts list data
PARTS_LIST_SCHEMA = DataSchema(
    name="PartsList",
    required_columns=["Part Name", "Part Number"],
    optional_columns=["Description", "Quantity", "Unit Cost"],
    description="Schema for parts list with part names and numbers"
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
