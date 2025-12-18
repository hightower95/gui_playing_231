"""
Decorator for registering data collectors
"""
from typing import List, Callable
from productivity_app.data_pipeline.parameters.input_parameters import Parameter
from productivity_app.data_pipeline.registry import registry


def data_collector(name: str, inputs: List[Parameter], outputs: List[Parameter]):
    """Decorator to register a data collector

    Args:
        name: Collector name
        inputs: List of input Parameters (usually Primitive)
        outputs: List of output Parameters (usually Collected)
    """
    def decorator(func: Callable) -> Callable:
        registry.register_collector(name, func, inputs, outputs)
        return func
    return decorator
