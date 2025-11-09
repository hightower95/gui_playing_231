"""
Path Utilities
Robust path handling for virtual environment discovery and validation
"""
import os
import sys
from pathlib import Path
from typing import Optional, Tuple
import subprocess


def get_robust_app_directory() -> Path:
    """
    Get the application directory with multiple fallback strategies

    Returns:
        Path: Validated application directory

    Raises:
        RuntimeError: If no valid directory can be determined
    """
    candidates = []

    # Strategy 1: Use __file__ location (most common)
    try:
        if '__file__' in globals():
            candidates.append(Path(__file__).parent.absolute())
    except:
        pass

    # Strategy 2: Use sys.argv[0] (script path)
    try:
        if sys.argv and sys.argv[0]:
            candidates.append(Path(sys.argv[0]).parent.absolute())
    except:
        pass

    # Strategy 3: Use current working directory
    try:
        candidates.append(Path.cwd().absolute())
    except:
        pass

    # Strategy 4: Use executable path parent (if frozen/packaged)
    try:
        if getattr(sys, 'frozen', False):
            candidates.append(Path(sys.executable).parent.absolute())
    except:
        pass

    # Validate candidates
    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            return candidate

    # Last resort - use current directory
    fallback = Path('.').absolute()
    if fallback.exists():
        return fallback

    raise RuntimeError("Unable to determine application directory")


def find_virtual_environment(app_dir: Path, venv_name: str) -> Optional[Tuple[Path, Path]]:
    """
    Find virtual environment with multiple search strategies

    Args:
        app_dir: Application base directory
        venv_name: Virtual environment directory name

    Returns:
        Tuple[Path, Path]: (venv_directory, python_executable) or None if not found
    """
    search_locations = [
        app_dir / venv_name,  # Same directory as app
        app_dir.parent / venv_name,  # Parent directory
        Path.cwd() / venv_name,  # Current working directory
    ]

    # Add some common venv locations
    if venv_name.startswith('.'):
        # Hidden directory variations
        search_locations.extend([
            app_dir / venv_name[1:],  # Without the dot
            app_dir.parent / venv_name[1:],
        ])

    for venv_dir in search_locations:
        if not venv_dir.exists():
            continue

        # Check for Windows python.exe
        python_paths = [
            venv_dir / "Scripts" / "python.exe",
            venv_dir / "Scripts" / "python3.exe",
            # Unix-style (shouldn't happen on Windows but just in case)
            venv_dir / "bin" / "python",
            venv_dir / "bin" / "python3",
        ]

        for python_path in python_paths:
            if python_path.exists() and validate_python_executable(python_path):
                return venv_dir, python_path

    return None


def validate_python_executable(python_path: Path) -> bool:
    """
    Validate that a Python executable works

    Args:
        python_path: Path to Python executable

    Returns:
        bool: True if Python executable is valid
    """
    try:
        result = subprocess.run(
            [str(python_path), "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except:
        return False


def log_path_discovery_details(app_dir: Path, venv_name: str, result: Optional[Tuple[Path, Path]] = None) -> str:
    """
    Generate detailed logging information about path discovery

    Args:
        app_dir: Application directory that was determined
        venv_name: Virtual environment name being searched for
        result: Result from find_virtual_environment (if any)

    Returns:
        str: Detailed log information
    """
    log_lines = [
        "=== PATH DISCOVERY DETAILS ===",
        f"Determined app directory: {app_dir}",
        f"App directory exists: {app_dir.exists()}",
        f"App directory is_dir: {app_dir.is_dir() if app_dir.exists() else 'N/A'}",
        f"App directory absolute: {app_dir.absolute()}",
        f"Current working directory: {Path.cwd()}",
        f"Script argument (sys.argv[0]): {sys.argv[0] if sys.argv else 'None'}",
        f"Searching for venv: {venv_name}",
        "",
        "Search candidates checked:",
    ]

    search_locations = [
        app_dir / venv_name,
        app_dir.parent / venv_name,
        Path.cwd() / venv_name,
    ]

    if venv_name.startswith('.'):
        search_locations.extend([
            app_dir / venv_name[1:],
            app_dir.parent / venv_name[1:],
        ])

    for i, location in enumerate(search_locations, 1):
        exists = location.exists()
        log_lines.append(
            f"  {i}. {location} - {'EXISTS' if exists else 'NOT FOUND'}")
        if exists:
            try:
                contents = list(location.iterdir())[:5]  # First 5 items
                log_lines.append(
                    f"     Contents (first 5): {[str(p.name) for p in contents]}")
            except:
                log_lines.append(f"     Contents: Unable to list")

    if result:
        venv_dir, python_path = result
        log_lines.extend([
            "",
            "=== SUCCESSFUL DISCOVERY ===",
            f"Found venv directory: {venv_dir}",
            f"Found Python executable: {python_path}",
            f"Python executable exists: {python_path.exists()}",
        ])

        # Test the Python executable
        try:
            test_result = subprocess.run(
                [str(python_path), "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            log_lines.append(
                f"Python version test: SUCCESS - {test_result.stdout.strip()}")
        except Exception as e:
            log_lines.append(f"Python version test: FAILED - {e}")
    else:
        log_lines.extend([
            "",
            "=== NO VIRTUAL ENVIRONMENT FOUND ===",
            "No valid Python executable discovered in any search location"
        ])

    log_lines.append("=== END PATH DISCOVERY ===")
    return "\n".join(log_lines)


def get_venv_python_path(app_dir: Optional[Path] = None, venv_name: str = ".test_venv") -> Tuple[Path, Optional[Tuple[Path, Path]], str]:
    """
    Robust virtual environment Python discovery with detailed logging

    Args:
        app_dir: Application directory (auto-detected if None)
        venv_name: Virtual environment directory name

    Returns:
        Tuple containing:
        - app_dir: Determined application directory
        - result: (venv_dir, python_path) tuple if found, None if not found
        - log_info: Detailed logging information
    """
    if app_dir is None:
        app_dir = get_robust_app_directory()

    result = find_virtual_environment(app_dir, venv_name)
    log_info = log_path_discovery_details(app_dir, venv_name, result)

    return app_dir, result, log_info
