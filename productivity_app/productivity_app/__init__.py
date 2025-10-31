"""
Productivity App - A comprehensive productivity tool for engineering workflows.

This package provides tools for:
- Connector management and search
- Document scanning and indexing
- EPD (Engineering Product Data) viewing
- Azure DevOps integration
- Remote documentation access
"""

from .main import main as _main
import sys
import os

# Add the app directory to the Python path so 'app' imports work
_package_dir = os.path.dirname(__file__)
if _package_dir not in sys.path:
    sys.path.insert(0, _package_dir)

__version__ = "0.1.0"
__author__ = "Productivity App Contributors"
__license__ = "MIT"

# Import the main application function


def start():
    """
    Start the Productivity App GUI application.

    This is the main entry point for running the application.

    Example:
        >>> import productivity_app
        >>> productivity_app.start()
    """
    _main()


# For backwards compatibility and direct execution
main = start

# Expose version info
__all__ = ["start", "main", "__version__", "__author__", "__license__"]
