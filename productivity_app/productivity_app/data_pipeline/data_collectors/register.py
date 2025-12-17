"""
Lightweight registry for data collectors

Tracks what data collectors exist and what data types they provide.
"""
from typing import Dict, List, Any, Callable
from productivity_app.data_pipeline.types_enum import DataTypes


class CollectorRegistry:
    """Registry for data collectors"""

    def __init__(self):
        self._collectors: Dict[str, Dict[str, Any]] = {}

    def register(self,
                 name: str,
                 func: Callable,
                 inputs: List[Any],
                 outputs: List[DataTypes]):
        """Register a data collector

        Args:
            name: Collector name
            func: The collector function
            inputs: List of input parameter types
            outputs: List of DataTypes this collector provides
        """
        self._collectors[name] = {
            'func': func,
            'inputs': inputs,
            'outputs': outputs
        }

    def get_collectors_for_type(self, data_type: DataTypes) -> List[str]:
        """Find collectors that provide a specific data type

        Args:
            data_type: The DataType to search for

        Returns:
            List of collector names that provide this type
        """
        return [
            name for name, info in self._collectors.items()
            if data_type in info['outputs']
        ]

    def get_collector(self, name: str) -> Dict[str, Any]:
        """Get collector info by name"""
        return self._collectors.get(name)

    def get_collector_by_name(self, name: str) -> Callable:
        """Get the actual collector function by name

        Args:
            name: Collector name

        Returns:
            The collector function that can be called
        """
        collector_info = self._collectors.get(name)
        if collector_info:
            return collector_info['func']
        return None


# Global registry instance
collector_registry = CollectorRegistry()
