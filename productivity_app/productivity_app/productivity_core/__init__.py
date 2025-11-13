"""
Swiss Army Tool Application Package

A comprehensive engineering toolkit for connector management, EPD operations,
and document scanning with intelligent context enrichment.
"""

__version__ = "0.1.0"
__author__ = "Swiss Army Tool Contributors"
__license__ = "MIT"

# Expose key classes for library usage
from productivity_core.core.app_context import AppContext
from productivity_core.core.config_manager import ConfigManager, DocumentScannerConfig

__all__ = [
    "AppContext",
    "ConfigManager",
    "DocumentScannerConfig",
    "__version__",
]
