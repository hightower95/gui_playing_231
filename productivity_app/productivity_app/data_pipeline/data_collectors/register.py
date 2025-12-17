"""
Lightweight registry for data collectors

DEPRECATED: Use central registry instead.
This module provides backwards compatibility aliases.
"""
from productivity_app.data_pipeline.registry import registry


class CollectorRegistry:
    """Registry for data collectors - delegates to central registry"""

    def register(self, name: str, func, inputs, outputs):
        """Register a data collector"""
        registry.register_collector(name, func, inputs, outputs)

    def get_collectors_for_type(self, data_type):
        """Find collectors that provide a specific data type"""
        return registry.get_collectors_for_type(data_type)

    def get_collector(self, name: str):
        """Get collector info by name"""
        return registry.get_collector(name)

    def get_collector_by_name(self, name: str):
        """Get the actual collector function by name"""
        return registry.get_collector_by_name(name)


# Backwards compatibility alias
collector_registry = CollectorRegistry()
