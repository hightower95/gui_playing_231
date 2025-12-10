"""
Decorators for registering data providers and reporters.
"""

from typing import List, Callable, Optional
from functools import wraps
from ..formats import DataFormat
from .parameter import Parameter
from .registry import DataProviderRegistry, ReporterRegistry, DataProviderMetadata, ReporterMetadata


def data_provider(
    provides: List[DataFormat],
    requires: Optional[List[Parameter]] = None,
    preconditions: Optional[List[Callable]] = None,
    name: Optional[str] = None,
    description: str = ""
):
    """
    Decorator to register a function as a data provider.

    Args:
        provides: List of data formats this provider produces
        requires: List of parameters required by this provider
        preconditions: List of functions that must return True before execution
        name: Optional custom name (defaults to function name)
        description: Human-readable description

    Example:
        @data_provider(
            provides=[DataFormat.EXCEL_DATAFRAME],
            requires=[
                param('file_path', str, description='Path to Excel file'),
                param('sheet_name', str, default='Sheet1')
            ]
        )
        def load_excel_file(file_path: str, sheet_name: str):
            return pd.read_excel(file_path, sheet_name=sheet_name)
    """
    def decorator(func: Callable) -> Callable:
        provider_name = name or func.__name__

        metadata = DataProviderMetadata(
            name=provider_name,
            function=func,
            provides=provides,
            requires=requires or [],
            preconditions=preconditions or [],
            description=description or func.__doc__ or ""
        )

        DataProviderRegistry.register(metadata)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper
    return decorator


def reporter(
    inputs: List[DataFormat],
    outputs: List[DataFormat],
    parameters: Optional[List[Parameter]] = None,
    name: Optional[str] = None,
    description: str = ""
):
    """
    Decorator to register a function as a reporter.

    Args:
        inputs: List of data formats this reporter consumes
        outputs: List of data formats this reporter produces
        parameters: List of parameters/options for the reporter
        name: Optional custom name (defaults to function name)
        description: Human-readable description

    Example:
        @reporter(
            inputs=[DataFormat.EXCEL_DATAFRAME, DataFormat.EXCEL_DATAFRAME],
            outputs=[DataFormat.EXCEL_REPORT],
            parameters=[
                param('output_path', str, description='Path for output file'),
                param('merge_key', str, default='id')
            ]
        )
        def merge_excel_files(df1, df2, output_path: str, merge_key: str):
            merged = pd.merge(df1, df2, on=merge_key)
            merged.to_excel(output_path, index=False)
            return output_path
    """
    def decorator(func: Callable) -> Callable:
        reporter_name = name or func.__name__

        metadata = ReporterMetadata(
            name=reporter_name,
            function=func,
            inputs=inputs,
            outputs=outputs,
            parameters=parameters or [],
            description=description or func.__doc__ or ""
        )

        ReporterRegistry.register(metadata)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper
    return decorator
