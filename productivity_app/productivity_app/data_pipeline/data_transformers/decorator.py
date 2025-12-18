"""
Decorator for registering data transformers

Transformers convert data from one type to another, enabling automatic
chain discovery for data pipeline execution.
"""
from typing import Callable
from productivity_app.data_pipeline.parameters.input_parameters import Parameter
from productivity_app.data_pipeline.registry import registry


def data_transformer(name: str, input_type: Parameter, output_type: Parameter):
    """Decorator to register a data transformer

    Transformers convert data from one type to another (e.g., DataFrame → PartsList).
    The registry uses these to automatically discover transformation chains.

    Args:
        name: Transformer name (should be descriptive, e.g., "DataFrameToPartsList")
        input_type: Parameter this transformer consumes
        output_type: Parameter this transformer produces

    Example:
        @data_transformer(
            name="DataFrameToPartsList",
            input_type=DataTypes.DataFrame,
            output_type=DataTypes.PartsList
        )
        def transform_df_to_parts(df: pd.DataFrame) -> List[Part]:
            schema = data_schemas.get_schema(DataTypes.PartsList)
            return schema.convert(df)
    """
    def decorator(func: Callable) -> Callable:
        registry.register_transformer(name, func, input_type, output_type)
        return func
    return decorator
