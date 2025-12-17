"""
PartsList Schema - Auto-generated from Part model

No manual column mapping needed - inferred from the Part dataclass.
"""
from productivity_app.data_pipeline.models.part import Part
from productivity_app.data_pipeline.types_enum import DataTypes
from productivity_app.data_pipeline.data_sources.schema_base_classes.schema_register import data_schemas
from productivity_app.data_pipeline.data_sources.schema_inference import infer_schema_from_dataclass

# Generate schema automatically from Part dataclass
PARTS_LIST_SCHEMA = infer_schema_from_dataclass(
    Part,
    name="PartsList",
    description="Schema for parts list with part names and numbers"
)

# Auto-register on import
data_schemas.register(DataTypes.PartsList, PARTS_LIST_SCHEMA)
# TODO: Sources.AddSource(PartsList)
