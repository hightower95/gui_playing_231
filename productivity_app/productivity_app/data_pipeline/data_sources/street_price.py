
from productivity_app.data_pipeline.models.street_price import StreetPrice
from productivity_app.data_pipeline.types_enum import DataTypes
from productivity_app.data_pipeline.data_sources.schema_base_classes.schema_register import data_schemas
from productivity_app.data_pipeline.data_sources.schema_inference import infer_schema_from_dataclass

STREET_PRICE_LIST_SCHEMA = infer_schema_from_dataclass(
    StreetPrice,
    name="StreetPrice",
    description="Schema for street price data with street, town, and price"
)
data_schemas.register(DataTypes.StreetPriceList, STREET_PRICE_LIST_SCHEMA)
