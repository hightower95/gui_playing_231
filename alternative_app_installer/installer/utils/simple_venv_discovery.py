"""
Simple Virtual Environment Discovery
Utilities for finding and validating virtual environment paths from configuration
"""
import os
from pathlib import Path
from typing import Optional, Tuple, Dict, Any


def get_venv_from_config(config: Dict[str, Any]) -> Optional[Tuple[Path, Path]]:
    """
    Get virtual environment paths from launch configuration.

    Args:
        config: Launch configuration dictionary

    Returns:
        Tuple of (venv_dir, venv_python) or None if not found
    """
    # Try absolute python path first
    if 'venv_python_path' in config and config['venv_python_path']:
        python_path = Path(config['venv_python_path'])
        if python_path.exists() and python_path.is_file():
            venv_dir = python_path.parent.parent
            return (venv_dir, python_path)

    # Try venv directory path
    if 'venv_dir_path' in config and config['venv_dir_path']:
        venv_dir = Path(config['venv_dir_path'])
        if venv_dir.exists() and venv_dir.is_dir():
            # Construct python executable path
            if os.name == 'nt':  # Windows
                python_path = venv_dir / 'Scripts' / 'python.exe'
            else:  # Unix-like
                python_path = venv_dir / 'bin' / 'python'

            if python_path.exists():
                return (venv_dir, python_path)

    # Try relative venv directory name
    if 'venv_dir_name' in config and config['venv_dir_name']:
        # Look in current directory and parent directories
        current_dir = Path.cwd()
        for search_dir in [current_dir, current_dir.parent]:
            venv_dir = search_dir / config['venv_dir_name']
            if venv_dir.exists() and venv_dir.is_dir():
                if os.name == 'nt':  # Windows
                    python_path = venv_dir / 'Scripts' / 'python.exe'
                else:  # Unix-like
                    python_path = venv_dir / 'bin' / 'python'

                if python_path.exists():
                    return (venv_dir, python_path)

    return None


def log_venv_discovery(config: Dict[str, Any], result: Optional[Tuple[Path, Path]]) -> str:
    """
    Generate detailed log of virtual environment discovery process.

    Args:
        config: Launch configuration dictionary
        result: Result from get_venv_from_config

    Returns:
        Detailed discovery log string
    """
    log_lines = [
        "=== VIRTUAL ENVIRONMENT DISCOVERY ===",
        f"Config provided:",
        f"  venv_python_path: {config.get('venv_python_path', 'NOT SET')}",
        f"  venv_dir_path: {config.get('venv_dir_path', 'NOT SET')}",
        f"  venv_dir_name: {config.get('venv_dir_name', 'NOT SET')}",
        ""
    ]

    # Try each discovery method and log results

    # Method 1: Absolute python path
    python_path_config = config.get('venv_python_path', '')
    if python_path_config:
        python_path = Path(python_path_config)
        exists = python_path.exists()
        is_file = python_path.is_file() if exists else False
        log_lines.extend([
            f"Method 1 - Absolute python path:",
            f"  Path: {python_path}",
            f"  Exists: {exists}",
            f"  Is file: {is_file}",
            f"  Result: {'SUCCESS' if exists and is_file else 'FAILED'}",
            ""
        ])
    else:
        log_lines.extend([
            "Method 1 - Absolute python path: SKIPPED (not configured)",
            ""
        ])

    # Method 2: Venv directory path
    venv_dir_config = config.get('venv_dir_path', '')
    if venv_dir_config:
        venv_dir = Path(venv_dir_config)
        exists = venv_dir.exists()
        is_dir = venv_dir.is_dir() if exists else False

        if exists and is_dir:
            if os.name == 'nt':
                python_path = venv_dir / 'Scripts' / 'python.exe'
            else:
                python_path = venv_dir / 'bin' / 'python'
            python_exists = python_path.exists()
        else:
            python_path = None
            python_exists = False

        log_lines.extend([
            f"Method 2 - Venv directory path:",
            f"  Dir: {venv_dir}",
            f"  Exists: {exists}",
            f"  Is dir: {is_dir}",
            f"  Python path: {python_path}",
            f"  Python exists: {python_exists}",
            f"  Result: {'SUCCESS' if exists and is_dir and python_exists else 'FAILED'}",
            ""
        ])
    else:
        log_lines.extend([
            "Method 2 - Venv directory path: SKIPPED (not configured)",
            ""
        ])

    # Method 3: Relative venv name
    venv_name = config.get('venv_dir_name', '')
    if venv_name:
        current_dir = Path.cwd()
        found = False
        for search_dir in [current_dir, current_dir.parent]:
            venv_dir = search_dir / venv_name
            exists = venv_dir.exists()
            is_dir = venv_dir.is_dir() if exists else False

            if exists and is_dir:
                if os.name == 'nt':
                    python_path = venv_dir / 'Scripts' / 'python.exe'
                else:
                    python_path = venv_dir / 'bin' / 'python'
                python_exists = python_path.exists()
                if python_exists:
                    found = True
            else:
                python_path = None
                python_exists = False

            log_lines.extend([
                f"  Searching in: {search_dir}",
                f"    Venv dir: {venv_dir}",
                f"    Exists: {exists}",
                f"    Is dir: {is_dir}",
                f"    Python path: {python_path}",
                f"    Python exists: {python_exists}",
                f"    Found: {'YES' if python_exists else 'NO'}",
                ""
            ])

        log_lines.extend([
            f"Method 3 - Relative venv name '{venv_name}':",
            f"  Result: {'SUCCESS' if found else 'FAILED'}",
            ""
        ])
    else:
        log_lines.extend([
            "Method 3 - Relative venv name: SKIPPED (not configured)",
            ""
        ])

    # Final result
    if result:
        venv_dir, python_path = result
        log_lines.extend([
            "=== FINAL RESULT ===",
            f"SUCCESS: Found virtual environment",
            f"  Venv dir: {venv_dir}",
            f"  Python: {python_path}",
        ])
    else:
        log_lines.extend([
            "=== FINAL RESULT ===",
            "FAILED: No virtual environment found",
        ])

    return "\n".join(log_lines)
