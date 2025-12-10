"""
Registry for data providers and reporters.
"""

from typing import List, Callable, Dict, Any, Optional
from dataclasses import dataclass, field
from ..formats import DataFormat
from .parameter import Parameter


@dataclass
class DataProviderMetadata:
    """Metadata for a registered data provider"""
    
    name: str
    function: Callable
    provides: List[DataFormat]
    requires: List[Parameter] = field(default_factory=list)
    preconditions: List[Callable] = field(default_factory=list)
    description: str = ""


@dataclass
class ReporterMetadata:
    """Metadata for a registered reporter"""
    
    name: str
    function: Callable
    inputs: List[DataFormat]
    outputs: List[DataFormat]
    parameters: List[Parameter] = field(default_factory=list)
    description: str = ""


class DataProviderRegistry:
    """
    Registry for data providers.
    Data providers collect data from sources and yield known formats.
    """
    
    _providers: Dict[str, DataProviderMetadata] = {}
    
    @classmethod
    def register(cls, metadata: DataProviderMetadata) -> None:
        """Register a data provider"""
        cls._providers[metadata.name] = metadata
        print(f"[Registry] Registered data provider: {metadata.name}")
        
    @classmethod
    def get(cls, name: str) -> Optional[DataProviderMetadata]:
        """Get a registered data provider by name"""
        return cls._providers.get(name)
        
    @classmethod
    def get_all(cls) -> Dict[str, DataProviderMetadata]:
        """Get all registered data providers"""
        return cls._providers.copy()
        
    @classmethod
    def get_providers_for_format(cls, data_format: DataFormat) -> List[DataProviderMetadata]:
        """Get all providers that can provide a specific format"""
        return [
            provider for provider in cls._providers.values()
            if data_format in provider.provides
        ]


class ReporterRegistry:
    """
    Registry for reporters.
    Reporters consume data formats and generate reports.
    """
    
    _reporters: Dict[str, ReporterMetadata] = {}
    
    @classmethod
    def register(cls, metadata: ReporterMetadata) -> None:
        """Register a reporter"""
        cls._reporters[metadata.name] = metadata
        print(f"[Registry] Registered reporter: {metadata.name}")
        
    @classmethod
    def get(cls, name: str) -> Optional[ReporterMetadata]:
        """Get a registered reporter by name"""
        return cls._reporters.get(name)
        
    @classmethod
    def get_all(cls) -> Dict[str, ReporterMetadata]:
        """Get all registered reporters"""
        return cls._reporters.copy()
        
    @classmethod
    def get_reporters_for_inputs(cls, data_formats: List[DataFormat]) -> List[ReporterMetadata]:
        """Get all reporters that can consume the given formats"""
        return [
            reporter for reporter in cls._reporters.values()
            if all(fmt in data_formats for fmt in reporter.inputs)
        ]
