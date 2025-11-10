"""
Utility Functions for Launch Configuration and Version Management
"""
import configparser
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List


def load_launch_config(config_file: Path) -> Dict[str, Any]:
    """Load launch configuration from file with safe defaults"""
    config = configparser.ConfigParser()
    
    if config_file.exists():
        config.read(config_file)
        
    # Return as dictionary with defaults
    defaults = {
        'library_name': 'productivity_app',
        'venv_python_path': '',
        'venv_dir_path': '',
        'venv_dir_name': '',
        'always_upgrade': 'true',
        'allow_upgrade_to_test_releases': 'false',
        'enable_log': 'false',
        'log_level': 'INFO'
    }
    
    if config.has_section('DEFAULT'):
        defaults.update(dict(config['DEFAULT']))
    
    return defaults


def create_default_launch_config(config_file: Path):
    """Create a default launch configuration file"""
    config = configparser.ConfigParser()
    config['DEFAULT'] = {
        'library_name': 'productivity_app',
        'venv_python_path': '',
        'venv_dir_path': '',
        'venv_dir_name': '',
        'always_upgrade': 'true',
        'allow_upgrade_to_test_releases': 'false',
        'enable_log': 'false',
        'log_level': 'INFO'
    }
    
    with config_file.open('w') as f:
        config.write(f)


def get_installed_version(venv_python: Path, library_name: str) -> Optional[str]:
    """Get the currently installed version of a library"""
    try:
        result = subprocess.run(
            [str(venv_python), "-m", "pip", "show", library_name],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            for line in result.stdout.split('\\n'):
                if line.startswith('Version:'):
                    return line.split(':', 1)[1].strip()
        return None
    except Exception:
        return None


def get_all_versions(venv_python: Path, library_name: str) -> List[str]:
    """Get all available versions of a library"""
    try:
        result = subprocess.run(
            [str(venv_python), "-m", "pip", "index", "versions", library_name],
            capture_output=True, text=True, timeout=60
        )
        
        versions = []
        if result.returncode == 0:
            for line in result.stdout.split('\\n'):
                if 'Available versions:' in line:
                    version_part = line.split('Available versions:')[1].strip()
                    versions = [v.strip() for v in version_part.split(',') if v.strip()]
                    break
        
        return versions
    except Exception:
        return []


def should_upgrade(current_version: str, config: Dict[str, Any], 
                  venv_python: Path, library_name: str) -> Optional[str]:
    """Determine if an upgrade should be performed and to which version"""
    
    # Check if upgrades are enabled
    always_upgrade = config.get('always_upgrade', 'true').lower() == 'true'
    if not always_upgrade:
        return None
    
    # Get available versions
    available_versions = get_all_versions(venv_python, library_name)
    if not available_versions:
        return None
    
    # Find latest stable version
    allow_test = config.get('allow_upgrade_to_test_releases', 'false').lower() == 'true'
    
    latest_version = None
    for version in available_versions:
        # Simple heuristic: avoid pre-release versions unless allowed
        if not allow_test and any(marker in version.lower() for marker in ['a', 'b', 'rc', 'dev']):
            continue
        latest_version = version
        break  # First non-prerelease version (should be latest stable)
    
    # Compare versions (simple string comparison for now)
    if latest_version and latest_version != current_version:
        return latest_version
    
    return None


def upgrade_to_version(venv_python: Path, library_name: str, target_version: str) -> bool:
    """Upgrade library to specific version"""
    try:
        result = subprocess.run(
            [str(venv_python), "-m", "pip", "install", f"{library_name}=={target_version}"],
            capture_output=True, text=True, timeout=300
        )
        return result.returncode == 0
    except Exception:
        return False


def log_upgrade_event(app_dir: Path, event_type: str, **kwargs):
    """Log an upgrade/launch event"""
    log_file = app_dir / "upgrade_history.log"
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    details = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
    
    log_entry = f"{timestamp} | {event_type} | {details}\\n"
    
    try:
        with log_file.open('a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception:
        pass  # Don't fail if logging fails


def write_comprehensive_log(app_dir: Path, config: Dict[str, Any], 
                          venv_python: Path, result: subprocess.CompletedProcess, 
                          runner_script: str):
    """Write comprehensive launch log if enabled"""
    if not config.get('enable_log', False):
        return
        
    log_file = app_dir / "launch_log.txt"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    log_content = f"""
=== LAUNCH LOG - {timestamp} ===

Config:
{config}

Virtual Environment:
{venv_python}

Runner Script:
{runner_script}

Result:
  Return Code: {result.returncode}
  
STDOUT:
{result.stdout}

STDERR:
{result.stderr}

================================
"""
    
    try:
        with log_file.open('w', encoding='utf-8') as f:
            f.write(log_content)
    except Exception:
        pass  # Don't fail if logging fails