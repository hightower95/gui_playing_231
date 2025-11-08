"""
Configuration management utilities
Handles reading and parsing of launch_config.ini with safe defaults
"""
from constants import DEFAULT_CONFIG
import configparser
from pathlib import Path
from typing import Dict, Any
import sys
import os

# Add the installer scripts to the path to import constants
sys.path.append(str(Path(__file__).parent.parent / "installer" / "scripts"))


def load_launch_config(config_file: Path) -> Dict[str, Any]:
    """Load launch configuration with safe defaults"""
    # Use centralized defaults from constants
    config = DEFAULT_CONFIG.copy()

    if not config_file.exists():
        return config

    try:
        parser = configparser.ConfigParser()
        parser.read(config_file)

        # Read from [Settings] section with fallbacks
        if parser.has_section('Settings'):
            section = parser['Settings']

            # String values
            config['app_name'] = section.get('app_name', config['app_name'])
            config['library_name'] = section.get(
                'library_name', config['library_name'])
            config['venv_dir_name'] = section.get(
                'venv_dir_name', config['venv_dir_name'])

            # Boolean values with safe parsing
            for bool_key in ['enable_log', 'auto_upgrade_major_version', 'auto_upgrade_minor_version',
                             'auto_upgrade_patches', 'allow_upgrade_to_test_releases', 'debug']:
                bool_str = section.get(bool_key, 'false')
                config[bool_key] = bool_str.lower() in (
                    'true', '1', 'yes', 'on')

    except Exception:
        # Config parsing failed, use safe defaults
        pass

    return config


def create_default_launch_config(config_file: Path):
    """Create a default launch_config.ini file with sensible defaults"""
    default_content = """[Settings]
# Application Configuration
app_name = ProductivityApp
library_name = productivity_app
venv_dir_name = .test_venv

# Automatic upgrade permissions (conservative defaults)
auto_upgrade_major_version = false
auto_upgrade_minor_version = true
auto_upgrade_patches = true

# Test release handling  
allow_upgrade_to_test_releases = false

# Logging and debugging
enable_log = false
debug = false
"""

    try:
        config_file.write_text(default_content, encoding='utf-8')
    except Exception:
        pass  # Silent fail for file creation
