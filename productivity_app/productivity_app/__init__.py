"""
Productivity App - A comprehensive productivity tool for engineering workflows.

This package provides tools for:
- Connector management and search
- Document scanning and indexing
- EPD (Engineering Product Data) viewing
- Azure DevOps integration
- Remote documentation access
"""

# Read version from package metadata (includes git hash from build)
try:
    from importlib.metadata import version
    __version__ = version("productivity-app")
# Catch all exceptions (ImportError, PackageNotFoundError, etc.)
except Exception:
    __version__ = "dev"

__author__ = "Productivity App Contributors"
__license__ = "MIT"

# Import the main application function
from .main import main as _main


def start(*args, **kwargs):
    """
    Start the Productivity App GUI application.

    This is the main entry point for running the application.

    Example:
        >>> import productivity_app
        >>> productivity_app.start()
    """
    _main(*args, **kwargs)


# For backwards compatibility and direct execution
main = start

# Expose version info
__all__ = ["start", "main", "__version__", "__author__", "__license__"]
