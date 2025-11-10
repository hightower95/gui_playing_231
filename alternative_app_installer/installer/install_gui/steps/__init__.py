"""
Installation Steps Package

This package contains all the individual installation steps.
Each step inherits from BaseStep and handles a specific part of the installation process.

Available Steps:
- GetFolderStep: Folder selection and validation
- FolderStep: Alias for GetFolderStep (backward compatibility)
"""

from .base_step import BaseStep
from .folder_step import GetFolderStep, FolderStep

__all__ = [
    'BaseStep',
    'GetFolderStep',
    'FolderStep',
]
