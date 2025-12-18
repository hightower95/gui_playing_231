"""
Report decorator
"""
import inspect
from typing import List, Any, Callable
from productivity_app.data_pipeline.registry import registry


def report(title: str, description: str, inputs: List[Any], **kwargs) -> Callable:
    """Decorator to register a report"""
    def decorator(func: Callable) -> Callable:
        # Validate inputs match function signature
        sig = inspect.signature(func)
        func_params = set(sig.parameters.keys())

        # Get input parameter names
        input_names = []
        for inp in inputs:
            if hasattr(inp, 'name'):
                input_names.append(inp.name)
            else:
                input_names.append(str(inp))

        # Check for inputs not in function signature
        extra_inputs = [
            name for name in input_names if name not in func_params]
        if extra_inputs:
            raise ValueError(
                f"Report '{title}': inputs {extra_inputs} not found in function "
                f"signature. Function parameters: {list(func_params)}"
            )

        registry.register_report(title, func, description, inputs)
        return func
    return decorator
