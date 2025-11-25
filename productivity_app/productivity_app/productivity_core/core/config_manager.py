"""
Centralized Configuration Manager

Handles all persistent configuration storage in configurable directory.
Implements in-memory caching to reduce file I/O overhead.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from .config import CONFIG_DIR, CONFIG_FILES


class ConfigManager:
    """Manages application configuration files in configurable directory"""

    # Class-level config directory (resolved from template)
    CONFIG_DIR = CONFIG_DIR

    # Configuration file names (from config.py)
    DOCUMENT_SCANNER_CONFIG = CONFIG_FILES["document_scanner"]
    APP_SETTINGS_CONFIG = CONFIG_FILES["app_settings"]
    
    # In-memory cache to reduce file I/O
    # Format: {config_name: (timestamp, data)}
    _cache: Dict[str, Tuple[float, Any]] = {}
    _cache_ttl = 2.0  # Cache TTL in seconds (2 second cache)

    @classmethod
    def initialize(cls):
        """Initialize the configuration directory

        Creates configuration directory if it doesn't exist.
        Should be called on application startup.
        """
        cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✓ Configuration directory: {cls.CONFIG_DIR.absolute()}")

    @classmethod
    def get_config_path(cls, config_name: str) -> Path:
        """Get full path to a configuration file

        Args:
            config_name: Name of the config file (e.g., 'document_scanner.json')

        Returns:
            Path object for the configuration file
        """
        return cls.CONFIG_DIR / config_name

    @classmethod
    def save_config(cls, config_name: str, data: Any) -> bool:
        """Save configuration data to file and invalidate cache

        Args:
            config_name: Name of the config file
            data: Data to save (must be JSON-serializable)

        Returns:
            True if successful, False otherwise
        """
        try:
            config_path = cls.get_config_path(config_name)
            print(f"📝 Saving to: {config_path.absolute()}")
            print(f"📝 Data type: {type(data)}")
            if isinstance(data, dict) and 'documents' in data:
                print(f"📝 Number of documents: {len(data['documents'])}")

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            # Invalidate cache after successful save
            cls._cache.pop(config_name, None)
            print(f"✓ Saved configuration: {config_path}")
            return True
        except Exception as e:
            print(f"❌ ERROR saving configuration '{config_name}': {e}")
            import traceback
            traceback.print_exc()
            return False

    @classmethod
    def load_config(cls, config_name: str, default: Any = None) -> Any:
        """Load configuration data from file with caching

        Args:
            config_name: Name of the config file
            default: Default value to return if file doesn't exist

        Returns:
            Loaded data or default value
        """
        try:
            config_path = cls.get_config_path(config_name)
            
            # Check cache first (avoids file I/O)
            if config_name in cls._cache:
                timestamp, cached_data = cls._cache[config_name]
                if time.time() - timestamp < cls._cache_ttl:
                    print(f"📖 Cache hit for: {config_name}")
                    return cached_data
            
            print(f"📖 Looking for config at: {config_path.absolute()}")
            print(f"📖 File exists: {config_path.exists()}")

            if not config_path.exists():
                print(f"ℹ️  Configuration file not found, using default")
                # Cache the default value too
                cls._cache[config_name] = (time.time(), default)
                return default

            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Store in cache
            cls._cache[config_name] = (time.time(), data)
            
            print(f"✓ Loaded configuration: {config_path}")
            if isinstance(data, dict) and 'documents' in data:
                print(f"✓ Loaded {len(data['documents'])} document(s)")
            return data

        except Exception as e:
            print(f"❌ ERROR loading configuration '{config_name}': {e}")
            import traceback
            traceback.print_exc()
            return default

    @classmethod
    def config_exists(cls, config_name: str) -> bool:
        """Check if a configuration file exists

        Args:
            config_name: Name of the config file

        Returns:
            True if file exists, False otherwise
        """
        return cls.get_config_path(config_name).exists()

    @classmethod
    def delete_config(cls, config_name: str) -> bool:
        """Delete a configuration file and invalidate cache

        Args:
            config_name: Name of the config file

        Returns:
            True if successful, False otherwise
        """
        try:
            config_path = cls.get_config_path(config_name)
            if config_path.exists():
                config_path.unlink()
                # Invalidate cache
                cls._cache.pop(config_name, None)
                print(f"✓ Deleted configuration: {config_path}")
                return True
            return False
        except Exception as e:
            print(f"❌ ERROR deleting configuration '{config_name}': {e}")
            return False
    
    @classmethod
    def clear_cache(cls, config_name: str = None) -> None:
        """Clear cache for one or all config files

        Args:
            config_name: Optional specific config to clear. If None, clears all cache.
        """
        if config_name:
            if config_name in cls._cache:
                cls._cache.pop(config_name)
                print(f"✓ Cleared cache for: {config_name}")
        else:
            cache_size = len(cls._cache)
            cls._cache.clear()
            print(f"✓ Cleared cache for all {cache_size} config file(s)")
    
    @classmethod
    def get_cache_stats(cls) -> Dict[str, Any]:
        """Get cache statistics for debugging

        Returns:
            Dict with cache info
        """
        now = time.time()
        stats = {
            'cached_files': len(cls._cache),
            'cache_ttl_seconds': cls._cache_ttl,
            'files': {}
        }
        
        for config_name, (timestamp, data) in cls._cache.items():
            age = now - timestamp
            is_valid = age < cls._cache_ttl
            stats['files'][config_name] = {
                'age_seconds': round(age, 2),
                'is_valid': is_valid,
                'data_type': type(data).__name__,
                'size_bytes': len(json.dumps(data)) if data else 0
            }
        
        return stats


class DocumentScannerConfig:
    """Helper class for Document Scanner configuration"""

    CONFIG_NAME = ConfigManager.DOCUMENT_SCANNER_CONFIG

    @classmethod
    def save_documents(cls, documents: List[Dict]) -> bool:
        """Save document scanner configurations

        Args:
            documents: List of document configuration dictionaries

        Returns:
            True if successful, False otherwise
        """
        config_data = {
            "documents": documents
        }
        return ConfigManager.save_config(cls.CONFIG_NAME, config_data)

    @classmethod
    def load_documents(cls) -> List[Dict]:
        """Load document scanner configurations

        Returns:
            List of document configurations, or empty list if none exist
        """
        config_data = ConfigManager.load_config(
            cls.CONFIG_NAME, default={"documents": []})
        return config_data.get("documents", [])

    @classmethod
    def clear_documents(cls) -> bool:
        """Clear all document scanner configurations

        Returns:
            True if successful, False otherwise
        """
        return cls.save_documents([])

    @classmethod
    def save_search_history(cls, history: List[str]) -> bool:
        """Save search history

        Args:
            history: List of search terms (most recent first)

        Returns:
            True if successful, False otherwise
        """
        config_data = ConfigManager.load_config(cls.CONFIG_NAME, default={})
        config_data["search_history"] = history
        return ConfigManager.save_config(cls.CONFIG_NAME, config_data)

    @classmethod
    def load_search_history(cls) -> List[str]:
        """Load search history

        Returns:
            List of search terms (most recent first), or empty list if none exist
        """
        config_data = ConfigManager.load_config(cls.CONFIG_NAME, default={})
        return config_data.get("search_history", [])


class AppSettingsConfig:
    """Helper class for application-wide settings"""

    CONFIG_NAME = ConfigManager.APP_SETTINGS_CONFIG

    @classmethod
    def save_settings(cls, settings: Dict[str, Any]) -> bool:
        """Save application settings

        Args:
            settings: Dictionary of settings

        Returns:
            True if successful, False otherwise
        """
        return ConfigManager.save_config(cls.CONFIG_NAME, settings)

    @classmethod
    def load_settings(cls) -> Dict[str, Any]:
        """Load application settings

        Returns:
            Dictionary of settings, or empty dict if none exist
        """
        return ConfigManager.load_config(cls.CONFIG_NAME, default={})

    @classmethod
    def get_setting(cls, key: str, default: Any = None) -> Any:
        """Get a specific setting value

        Args:
            key: Setting key
            default: Default value if key doesn't exist

        Returns:
            Setting value or default
        """
        settings = cls.load_settings()
        return settings.get(key, default)

    @classmethod
    def set_setting(cls, key: str, value: Any) -> bool:
        """Set a specific setting value

        Args:
            key: Setting key
            value: Setting value

        Returns:
            True if successful, False otherwise
        """
        settings = cls.load_settings()
        settings[key] = value
        return cls.save_settings(settings)
