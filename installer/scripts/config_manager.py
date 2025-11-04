"""
Centralized Configuration Management
Eliminates duplicate config loading across all step files
"""
import configparser
from pathlib import Path
from typing import Optional, Any


class ConfigManager:
    """Singleton configuration manager for the bootstrap application"""

    _instance: Optional['ConfigManager'] = None

    def __new__(cls) -> 'ConfigManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = None
            cls._instance._config_file = None
        return cls._instance

    def __init__(self):
        # Only initialize once
        if self._config is None:
            self._config_file = Path(__file__).parent / "config.ini"
            self._load_config()

    def _load_config(self) -> None:
        """Load configuration from config.ini file"""
        self._config = configparser.ConfigParser()
        if self._config_file.exists():
            self._config.read(self._config_file)

    def get_config(self) -> configparser.ConfigParser:
        """Get the configuration object"""
        if self._config is None:
            self._load_config()
        return self._config

    def reload(self) -> None:
        """Reload configuration from file"""
        self._load_config()

    # Convenience methods for common config access patterns

    def get_app_name(self) -> str:
        """Get application name from config"""
        return self._config.get('Settings', 'app_name', fallback='My Application')

    def get_debug_mode(self) -> bool:
        """Get debug mode setting from config"""
        debug_str = self._config.get('Settings', 'debug', fallback='false')
        return debug_str.lower() in ('true', '1', 'yes', 'on')

    def get_venv_dir(self) -> str:
        """Get virtual environment directory name from config"""
        return self._config.get('Paths', 'venv_dir', fallback='.venv')

    def get_token_url(self) -> str:
        """Get token URL from config"""
        return self._config.get('URLs', 'token_url', fallback='https://example.com/get-token')

    def get_help_page(self) -> str:
        """Get help page URL from config"""
        return self._config.get('URLs', 'help_page', fallback='https://example.com/help')

    def get_core_libraries(self) -> str:
        """Get core libraries from config"""
        return self._config.get('Dependencies', 'core_libraries', fallback='')

    def get_additional_packages(self) -> list:
        """Get additional packages as a list"""
        packages_str = self._config.get(
            'Dependencies', 'additional_packages', fallback='')
        if packages_str:
            return [pkg.strip() for pkg in packages_str.split(',')]
        return []

    def get_version(self) -> str:
        """Get application version from config"""
        return self._config.get('Settings', 'version', fallback='1.0.0')

    # DEV settings convenience methods

    def get_skip_local_index(self) -> bool:
        """Get skip local index DEV setting"""
        return self._config.getboolean('DEV', 'skip_local_index', fallback=False)

    def get_auto_generate_files(self) -> bool:
        """Get auto generate files DEV setting"""
        return self._config.getboolean('DEV', 'auto_generate_files', fallback=True)

    def is_step_simulated(self, step: str) -> bool:
        """Check if a step is set to be simulated"""
        return self._config.getboolean('DEV', f'simulate_{step}_complete', fallback=False)

    # Generic getter with fallback

    def get(self, section: str, key: str, fallback: Any = None) -> Any:
        """Generic config getter with fallback"""
        return self._config.get(section, key, fallback=fallback)

    def getboolean(self, section: str, key: str, fallback: bool = False) -> bool:
        """Generic boolean config getter with fallback"""
        return self._config.getboolean(section, key, fallback=fallback)

    def getint(self, section: str, key: str, fallback: int = 0) -> int:
        """Generic integer config getter with fallback"""
        return self._config.getint(section, key, fallback=fallback)


# Global instance for easy access
config_manager = ConfigManager()
