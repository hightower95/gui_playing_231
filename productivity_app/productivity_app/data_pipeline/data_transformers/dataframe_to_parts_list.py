"""
DataFrame to PartsList Transformer

Transforms pandas DataFrames into typed PartsList objects using the registered schema.
"""
import pandas as pd
from typing import List

from ..data_sources.schema_base_classes.schema_register import data_schemas
from ..data_transformers.decorator import data_transformer


# Delay decorator application until after module init
_decorator_params = None


def dataframe_to_parts_list(df: pd.DataFrame) -> List:
    """Transform DataFrame to PartsList using registered schema

    Args:
        df: DataFrame with parts data

    Returns:
        List of Part objects

    Raises:
        ValueError: If no schema is registered for PartsList
    """
    from ..parameters import Variables
    schema = data_schemas.get_schema(Variables.PartsList)
    if schema is None:
        raise ValueError("No schema registered for PartsList")

    return schema.convert(df)


# Register transformer when fully initialized (not during initial imports)
if __name__ != '__main__':
    try:
        from ..parameters import Variables
        from ..data_transformers.decorator import data_transformer
        dataframe_to_parts_list = data_transformer(
            name="DataFrameToPartsList",
            input_type=Variables.DataFrame,
            output_type=Variables.PartsList
        )(dataframe_to_parts_list)
    except ImportError:
        # Variables not ready yet, will register when called
        pass
