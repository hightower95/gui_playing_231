"""
Utilities package for installer GUI
"""

from .version_manager import (
    get_latest_stable_version,
    get_installed_version,
    detect_local_index,
    parse_version,
    is_stable_version
)

__all__ = [
    'get_latest_stable_version',
    'get_installed_version', 
    'detect_local_index',
    'parse_version',
    'is_stable_version'
]