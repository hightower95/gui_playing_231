"""
Decorator for registering data collectors
"""
from typing import List, Any, Callable
from productivity_app.data_pipeline.types_enum import DataTypes
from productivity_app.data_pipeline.registry import registry


def data_collector(name: str, inputs: List[Any], outputs: List[DataTypes]):
    """Decorator to register a data collector

    Args:
        name: Collector name
        inputs: List of input parameter types
        outputs: List of DataTypes this collector provides
    """
    def decorator(func: Callable) -> Callable:
        registry.register_collector(name, func, inputs, outputs)
        return func
    return decorator
