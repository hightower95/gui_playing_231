"""
Simple Virtual Environment Discovery
Uses only the absolute path written by step_venv.py - no fallbacks
"""
from pathlib import Path
from typing import Optional, Tuple
import subprocess


def get_venv_from_config(config: dict) -> Optional[Tuple[Path, Path]]:
    """
    Get virtual environment paths from config - ABSOLUTE PATHS ONLY

    Args:
        config: Launch configuration dictionary

    Returns:
        Tuple[Path, Path]: (venv_dir, python_exe) or None if not found/invalid
    """
    # Only use the absolute python path written by step_venv.py
    venv_python_path = config.get('venv_python_path', '').strip()
    if not venv_python_path:
        return None

    python_exe = Path(venv_python_path)
    if not python_exe.exists():
        return None

    if not _validate_python_executable(python_exe):
        return None

    # Get venv directory from python executable path
    venv_dir = python_exe.parent.parent  # Scripts/python.exe -> venv_dir

    return venv_dir, python_exe


def _validate_python_executable(python_path: Path) -> bool:
    """
    Quick validation that Python executable works

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
            timeout=5
        )
        return result.returncode == 0
    except:
        return False


def log_venv_discovery(config: dict, result: Optional[Tuple[Path, Path]]) -> str:
    """
    Generate log information about venv discovery attempt

    Args:
        config: Configuration used for discovery
        result: Discovery result

    Returns:
        str: Log information
    """
    venv_python_path = config.get('venv_python_path', 'NOT SET')

    log_lines = [
        "=== VIRTUAL ENVIRONMENT DISCOVERY ===",
        f"Config venv_python_path: {venv_python_path}",
        ""
    ]

    if result:
        venv_dir, python_exe = result
        log_lines.extend([
            "✅ SUCCESS - Virtual environment found:",
            f"  Venv directory: {venv_dir}",
            f"  Python executable: {python_exe}",
        ])

        # Test Python executable
        try:
            test_result = subprocess.run(
                [str(python_exe), "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if test_result.returncode == 0:
                log_lines.append(
                    f"  Python version: {test_result.stdout.strip()}")
            else:
                log_lines.append(
                    f"  Python test failed with code: {test_result.returncode}")
        except Exception as e:
            log_lines.append(f"  Python test error: {e}")
    else:
        if not venv_python_path or venv_python_path == 'NOT SET':
            log_lines.extend([
                "❌ FAILED - No venv_python_path in config",
                "This means step_venv.py did not run successfully or config was not saved."
            ])
        else:
            python_path = Path(venv_python_path)
            log_lines.extend([
                "❌ FAILED - venv_python_path exists in config but Python executable not found",
                f"  Expected path: {python_path}",
                f"  Path exists: {python_path.exists()}",
                f"  Path is file: {python_path.is_file() if python_path.exists() else 'N/A'}"
            ])

    log_lines.append("=== END VENV DISCOVERY ===")
    return "\n".join(log_lines)
