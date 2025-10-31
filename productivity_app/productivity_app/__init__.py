"""
Productivity App - A comprehensive productivity tool for engineering workflows.

This package provides tools for:
- Connector management and search
- Document scanning and indexing
- EPD (Engineering Product Data) viewing
- Azure DevOps integration
- Remote documentation access
"""

import sys
import os

# CRITICAL: Add package directory to path BEFORE any imports
# This allows 'app' module imports to work from within productivity_app/app/
_package_dir = os.path.dirname(os.path.abspath(__file__))
if _package_dir not in sys.path:
    sys.path.insert(0, _package_dir)

__version__ = "0.1.0"
__author__ = "Productivity App Contributors"
__license__ = "MIT"


def start():
    """
    Start the Productivity App GUI application.

    This is the main entry point for running the application.

    Example:
        >>> import productivity_app
        >>> productivity_app.start()
    """
    # Import here to avoid circular imports and ensure path is set up
    from .main import main as _main
    _main()


def main():
    """Alias for start() for backwards compatibility."""
    start()


# Expose version info
__all__ = ["start", "main", "__version__", "__author__", "__license__"]
