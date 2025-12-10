"""
God Module - Data Pipeline System

A flexible data pipeline framework for registering data providers and reporters.
Data providers collect data from sources and yield known formats.
Reporters generate reports by consuming those known formats.
"""

from .core.registry import DataProviderRegistry, ReporterRegistry
from .core.decorators import data_provider, reporter
from .core.parameter import param
from .core.pipeline import Pipeline
from .core.context import PipelineContext
from .formats import DataFormat

__all__ = [
    'DataProviderRegistry',
    'ReporterRegistry',
    'data_provider',
    'reporter',
    'param',
    'param',
    'Pipeline',
    'PipelineContext',
    'DataFormat',
]
