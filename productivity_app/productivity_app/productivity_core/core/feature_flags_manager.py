"""
Feature Flags Manager - Global feature flag management with signal support

Provides centralized access to feature flags with signal-based subscriptions.
Feature flags are organized by their parent module/tab.

Usage:
    # Access from context
    feature_flags = context.get('feature_flags', FeatureFlagsManager)
    
    # Check if flag is enabled
    if feature_flags.get('connectors', 'advanced_search'):
        # Show advanced search UI
    
    # Subscribe to flag changes
    feature_flags.subscribe('connectors', 'advanced_search', callback)
    
    # Set flag (persists to storage)
    feature_flags.set('connectors', 'advanced_search', True)
"""
from typing import Dict, Callable, Optional, Any
from PySide6.QtCore import QObject, Signal
from .config_manager import AppSettingsConfig


class FeatureFlagsManager(QObject):
    """Global feature flags manager with signal-based subscriptions
    
    Organizes feature flags by module/tab for better organization.
    Supports reactive updates via Qt signals.
    """

    # Signal emitted when any flag changes: (module: str, flag_id: str, enabled: bool)
    flag_changed = Signal(str, str, bool)

    # Feature flag definitions organized by module
    # Structure: {module_id: {flag_id: (display_name, description, default_value)}}
    FEATURE_FLAGS_SCHEMA = {
        'connectors': {
            'advanced_search': (
                'Advanced Search',
                'Enable advanced search capabilities in Connector module',
                False
            ),
        },
        'document_scanner': {
            # Add document scanner feature flags here
        },
        'epd': {
            # Add EPD feature flags here
        },
        'devops': {
            # Add DevOps feature flags here
        },
        'remote_docs': {
            'upload': (
                'Remote Docs Upload',
                'Show file upload section in Remote Documents tab',
                True
            ),
        },
    }

    def __init__(self):
        super().__init__()
        self._subscriptions: Dict[str, Dict[str, list]] = {}
        self._cache: Dict[str, Dict[str, bool]] = {}
        self._initialize_cache()

    def _initialize_cache(self):
        """Load all feature flags from storage into cache"""
        storage = AppSettingsConfig.get_setting('feature_flags', {})

        for module_id, flags_dict in self.FEATURE_FLAGS_SCHEMA.items():
            self._cache[module_id] = {}

            for flag_id, (name, desc, default) in flags_dict.items():
                # Get from storage or use default
                module_storage = storage.get(module_id, {})
                value = module_storage.get(flag_id, default)
                self._cache[module_id][flag_id] = value

    def get(self, module_id: str, flag_id: str) -> bool:
        """Get feature flag value
        
        Args:
            module_id: Module identifier (e.g., 'connectors', 'document_scanner')
            flag_id: Flag identifier within module (e.g., 'advanced_search')
        
        Returns:
            True if flag is enabled, False otherwise
        """
        if module_id not in self._cache:
            return False

        return self._cache[module_id].get(flag_id, False)

    def set(self, module_id: str, flag_id: str, enabled: bool) -> bool:
        """Set feature flag value and persist to storage
        
        Args:
            module_id: Module identifier
            flag_id: Flag identifier
            enabled: New value
        
        Returns:
            True if successful, False otherwise
        """
        # Validate module and flag exist
        if module_id not in self.FEATURE_FLAGS_SCHEMA:
            print(f"Warning: Unknown module '{module_id}' for feature flag")
            return False

        if flag_id not in self.FEATURE_FLAGS_SCHEMA[module_id]:
            print(f"Warning: Unknown flag '{flag_id}' in module '{module_id}'")
            return False

        # Update cache
        if module_id not in self._cache:
            self._cache[module_id] = {}

        old_value = self._cache[module_id].get(flag_id)
        self._cache[module_id][flag_id] = enabled

        # Persist to storage
        storage = AppSettingsConfig.get_setting('feature_flags', {})
        if module_id not in storage:
            storage[module_id] = {}

        storage[module_id][flag_id] = enabled
        success = AppSettingsConfig.set_setting('feature_flags', storage)

        # Emit signal if value changed
        if old_value != enabled:
            self.flag_changed.emit(module_id, flag_id, enabled)

            # Call subscribed callbacks
            self._notify_subscribers(module_id, flag_id, enabled)

        return success

    def subscribe(self, module_id: str, flag_id: str, callback: Callable[[bool], None]) -> None:
        """Subscribe to flag changes via callback
        
        Args:
            module_id: Module identifier
            flag_id: Flag identifier
            callback: Function to call when flag changes, receives (enabled: bool)
        
        Example:
            def on_advanced_search_changed(enabled):
                print(f"Advanced search is now {enabled}")
            
            feature_flags.subscribe('connectors', 'advanced_search', on_advanced_search_changed)
        """
        key = f"{module_id}:{flag_id}"

        if key not in self._subscriptions:
            self._subscriptions[key] = []

        self._subscriptions[key].append(callback)

    def unsubscribe(self, module_id: str, flag_id: str, callback: Callable) -> bool:
        """Unsubscribe from flag changes
        
        Args:
            module_id: Module identifier
            flag_id: Flag identifier
            callback: Callback to remove
        
        Returns:
            True if callback was removed, False if not found
        """
        key = f"{module_id}:{flag_id}"

        if key not in self._subscriptions:
            return False

        try:
            self._subscriptions[key].remove(callback)
            return True
        except ValueError:
            return False

    def _notify_subscribers(self, module_id: str, flag_id: str, enabled: bool) -> None:
        """Notify all subscribers about flag change"""
        key = f"{module_id}:{flag_id}"

        if key in self._subscriptions:
            for callback in self._subscriptions[key]:
                try:
                    callback(enabled)
                except Exception as e:
                    print(
                        f"Error calling subscriber callback for {key}: {e}")

    def get_module_flags(self, module_id: str) -> Dict[str, bool]:
        """Get all flags for a module
        
        Args:
            module_id: Module identifier
        
        Returns:
            Dictionary mapping flag IDs to enabled state
        """
        return self._cache.get(module_id, {}).copy()

    def get_all_flags(self) -> Dict[str, Dict[str, bool]]:
        """Get all feature flags organized by module
        
        Returns:
            Nested dictionary: {module_id: {flag_id: enabled}}
        """
        return {
            module_id: flags.copy()
            for module_id, flags in self._cache.items()
        }

    def get_flag_metadata(self, module_id: str, flag_id: str) -> Optional[tuple]:
        """Get flag metadata (name, description, default)
        
        Args:
            module_id: Module identifier
            flag_id: Flag identifier
        
        Returns:
            Tuple of (name, description, default) or None if not found
        """
        if module_id in self.FEATURE_FLAGS_SCHEMA:
            if flag_id in self.FEATURE_FLAGS_SCHEMA[module_id]:
                return self.FEATURE_FLAGS_SCHEMA[module_id][flag_id]

        return None

    def reset_to_defaults(self, module_id: Optional[str] = None) -> bool:
        """Reset flags to defaults
        
        Args:
            module_id: Optional module to reset. If None, resets all.
        
        Returns:
            True if successful
        """
        if module_id is None:
            # Reset all
            storage = {}

            for mid, flags_dict in self.FEATURE_FLAGS_SCHEMA.items():
                storage[mid] = {}
                self._cache[mid] = {}

                for flag_id, (name, desc, default) in flags_dict.items():
                    storage[mid][flag_id] = default
                    self._cache[mid][flag_id] = default

            return AppSettingsConfig.set_setting('feature_flags', storage)
        else:
            # Reset specific module
            if module_id not in self.FEATURE_FLAGS_SCHEMA:
                return False

            storage = AppSettingsConfig.get_setting('feature_flags', {})
            storage[module_id] = {}
            self._cache[module_id] = {}

            for flag_id, (name, desc, default) in self.FEATURE_FLAGS_SCHEMA[module_id].items():
                storage[module_id][flag_id] = default
                self._cache[module_id][flag_id] = default

            return AppSettingsConfig.set_setting('feature_flags', storage)
