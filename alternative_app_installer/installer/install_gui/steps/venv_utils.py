"""
Virtual Environment Path Utilities

This module provides utility functions to derive all venv-related paths
from the base venv_path stored in shared state.

Design: Store only venv_path, derive everything else as needed.
"""
import os
from pathlib import Path
from typing import Dict, Any


class VenvPathUtils:
    """Utility class for deriving venv-related paths and information"""

    @staticmethod
    def get_venv_python_path(venv_path: str) -> str:
        """Get the Python executable path within the venv

        Args:
            venv_path: Absolute path to the virtual environment

        Returns:
            Absolute path to the Python executable in the venv
        """
        venv_dir = Path(venv_path)

        if os.name == 'nt':  # Windows
            return str(venv_dir / 'Scripts' / 'python.exe')
        else:  # Unix-like
            return str(venv_dir / 'bin' / 'python')

    @staticmethod
    def get_venv_pip_path(venv_path: str) -> str:
        """Get the pip executable path within the venv

        Args:
            venv_path: Absolute path to the virtual environment

        Returns:
            Absolute path to the pip executable in the venv
        """
        venv_dir = Path(venv_path)

        if os.name == 'nt':  # Windows
            return str(venv_dir / 'Scripts' / 'pip.exe')
        else:  # Unix-like
            return str(venv_dir / 'bin' / 'pip')

    @staticmethod
    def get_venv_activate_path(venv_path: str) -> str:
        """Get the activation script path within the venv

        Args:
            venv_path: Absolute path to the virtual environment

        Returns:
            Absolute path to the activation script
        """
        venv_dir = Path(venv_path)

        if os.name == 'nt':  # Windows
            return str(venv_dir / 'Scripts' / 'activate.bat')
        else:  # Unix-like
            return str(venv_dir / 'bin' / 'activate')

    @staticmethod
    def get_venv_name(venv_path: str) -> str:
        """Get the virtual environment directory name

        Args:
            venv_path: Absolute path to the virtual environment

        Returns:
            Directory name of the venv (e.g., '.test_venv')
        """
        return Path(venv_path).name

    @staticmethod
    def get_installation_directory(venv_path: str) -> str:
        """Get the installation directory (parent of venv)

        Args:
            venv_path: Absolute path to the virtual environment

        Returns:
            Absolute path to the installation directory
        """
        return str(Path(venv_path).parent)

    @staticmethod
    def is_venv_created(venv_path: str) -> bool:
        """Check if the virtual environment exists and is valid

        Args:
            venv_path: Absolute path to the virtual environment

        Returns:
            True if venv exists and has required files
        """
        try:
            venv_dir = Path(venv_path)

            if not venv_dir.exists():
                return False

            # Check for essential files
            python_exe = Path(VenvPathUtils.get_venv_python_path(venv_path))
            activate_script = Path(
                VenvPathUtils.get_venv_activate_path(venv_path))

            return python_exe.exists() and activate_script.exists()

        except Exception:
            return False

    @staticmethod
    def enrich_shared_state(shared_state: Dict[str, Any]) -> Dict[str, str]:
        """Enrich shared state with derived venv information

        Args:
            shared_state: Dictionary containing at least 'venv_path'

        Returns:
            Dictionary with all derived venv information

        Raises:
            KeyError: If 'venv_path' not in shared_state
            ValueError: If venv_path is invalid
        """
        venv_path = shared_state.get('venv_path')

        if not venv_path:
            raise KeyError("venv_path not found in shared_state")

        if not isinstance(venv_path, str) or not venv_path.strip():
            raise ValueError("venv_path must be a non-empty string")

        return {
            'venv_path': venv_path,
            'venv_python_path': VenvPathUtils.get_venv_python_path(venv_path),
            'venv_pip_path': VenvPathUtils.get_venv_pip_path(venv_path),
            'venv_activate_path': VenvPathUtils.get_venv_activate_path(venv_path),
            'venv_name': VenvPathUtils.get_venv_name(venv_path),
            'installation_directory': VenvPathUtils.get_installation_directory(venv_path),
            'venv_exists': VenvPathUtils.is_venv_created(venv_path)
        }


# Convenience functions for direct use
def get_python_executable_from_shared_state(shared_state: Dict[str, Any]) -> str:
    """Get Python executable path from shared state

    Args:
        shared_state: Must contain 'venv_path' key

    Returns:
        Absolute path to Python executable in venv
    """
    venv_path = shared_state.get('venv_path')
    if not venv_path:
        raise KeyError("venv_path not found in shared_state")

    return VenvPathUtils.get_venv_python_path(venv_path)


def get_pip_executable_from_shared_state(shared_state: Dict[str, Any]) -> str:
    """Get pip executable path from shared state

    Args:
        shared_state: Must contain 'venv_path' key

    Returns:
        Absolute path to pip executable in venv
    """
    venv_path = shared_state.get('venv_path')
    if not venv_path:
        raise KeyError("venv_path not found in shared_state")

    return VenvPathUtils.get_venv_pip_path(venv_path)
