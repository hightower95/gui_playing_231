"""
Parts List Parameter Definition

Example of how to define a reusable parameter with a schema.
The schema defines the expected columns in the parts list data.
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

# Create a reusable PartsList parameter factory
# Users can call PartsList(name="my_parts") to create an instance


def PartsList(name: str, required: bool = True, description: str = "Parts list data source"):
    """Create a PartsList data source parameter

    Args:
        name: Name for this parameter instance
        required: Whether this parameter is required
        description: Description of this specific use

    Returns:
        DataSourceParameter configured for PartsList

    Example:
        >>> parts = PartsList(name="input_parts", required=True)
        >>> parts.schema.required_columns
        ['Part Name', 'Part Number']
    """
    return Source.DataSource(
        name=name,
        data_type=DataTypes.PartsList,
        required=required,
        description=description
        # schema is auto-loaded from registry
    )
