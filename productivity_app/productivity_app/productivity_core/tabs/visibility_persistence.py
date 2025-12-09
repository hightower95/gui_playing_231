"""
Visibility Persistence Module

Handles persistence of tab and sub-tab visibility settings.
Provides configuration classes for:
- Main tab visibility
- Sub-tab visibility within modules
- Feature flags

All settings are persisted to JSON via AppSettingsConfig.
"""

from typing import Dict, List
from ..core.config_manager import AppSettingsConfig
from ..document_scanner.document_scanner_tab import DocumentScannerModuleView
from ..connector.connector_tab import ConnectorModuleView
from ..epd.epd_tab import EpdModuleView
from ..devops.devops_tab import DevOpsModuleView


# ============================================================================
# TAB VISIBILITY HELPERS
# ============================================================================
# These functions extract visibility configuration from tab_config.py
# to ensure single source of truth for tab definitions.
#
# IMPORTANT: TAB_VISIBILITY_CONFIG is dynamically generated from TAB_CONFIG.
# To change default visibility, edit the 'visible' field in tab_config.py.
# ============================================================================

def _get_tab_visibility_config() -> List[Dict[str, any]]:
    """
    Generate tab visibility configuration from TAB_CONFIG.

    This ensures visibility settings match the actual tab configuration.

    Returns:
        List of dicts with id, label, tooltip, and default visibility
    """
    from .tab_config import TAB_CONFIG, get_tab_title

    visibility_config = []
    for tab_config in TAB_CONFIG:
        tab_id = tab_config['id']
        title = get_tab_title(tab_config)
        default_visible = tab_config.get('visible', True)

        visibility_config.append({
            'id': tab_id,
            'label': title,
            'tooltip': f'Show/hide the {title} tab',
            'default': default_visible
        })

    return visibility_config


# Dynamically generate configuration from tab_config.py
TAB_VISIBILITY_CONFIG = _get_tab_visibility_config()


# ============================================================================
# SUB-TAB VISIBILITY CONFIGURATION
# ============================================================================
# Define sub-tabs for modules that have internal tabs
# References constants from module views to avoid magic strings
# Structure: {parent_tab_id: [{'id': 'subtab_id', 'label': 'Display Name', 'default': True}, ...]}
# ============================================================================

SUB_TAB_VISIBILITY_CONFIG = {
    DocumentScannerModuleView.MODULE_ID: [
        {'id': DocumentScannerModuleView.SUB_TAB_SEARCH,
            'label': 'Search', 'default': True},
        {'id': DocumentScannerModuleView.SUB_TAB_CONFIGURATION,
            'label': 'Configuration', 'default': True},
        {'id': DocumentScannerModuleView.SUB_TAB_HISTORY,
            'label': 'History', 'default': True},
        {'id': DocumentScannerModuleView.SUB_TAB_COMPARE_VERSIONS,
            'label': 'Compare Versions', 'default': False},
    ],
    ConnectorModuleView.MODULE_ID: [
        {'id': ConnectorModuleView.SUB_TAB_LOOKUP,
            'label': 'Lookup', 'default': True},
        {'id': ConnectorModuleView.SUB_TAB_CHECK_MULTIPLE,
            'label': 'Check Multiple', 'default': True},
    ],
    EpdModuleView.MODULE_ID: [
        {'id': EpdModuleView.SUB_TAB_SEARCH,
            'label': 'Search', 'default': True},
        {'id': EpdModuleView.SUB_TAB_IDENTIFY_BEST,
            'label': 'Identify Best', 'default': True},
    ],
    DevOpsModuleView.MODULE_ID: [
        {'id': DevOpsModuleView.SUB_TAB_QUERY_VIEWER,
            'label': 'Query Viewer', 'default': True},
    ],
}


class TabVisibilityPersistence:
    """
    Manages tab visibility settings with persistence.

    Handles loading and saving tab visibility state to application config.
    Used by TabVisibilityService for persistence layer.
    """

    CONFIG_KEY = "tab_visibility"

    @classmethod
    def get_visibility_settings(cls) -> Dict[str, bool]:
        """
        Get current visibility settings for all tabs.

        Returns:
            Dictionary mapping tab IDs to visibility (True/False)
        """
        settings = AppSettingsConfig.get_setting(cls.CONFIG_KEY, {})

        # Default all tabs to visible if not configured
        defaults = {config['id']: config['default']
                    for config in TAB_VISIBILITY_CONFIG}

        # Merge with saved settings
        for tab_id, default_visible in defaults.items():
            if tab_id not in settings:
                settings[tab_id] = default_visible

        return settings

    @classmethod
    def set_visibility_settings(cls, settings: Dict[str, bool]) -> bool:
        """
        Save visibility settings.

        Args:
            settings: Dictionary mapping tab IDs to visibility

        Returns:
            True if successful, False otherwise
        """
        return AppSettingsConfig.set_setting(cls.CONFIG_KEY, settings)

    @classmethod
    def get_tab_visibility(cls, tab_name: str) -> bool:
        """
        Get visibility for a specific tab.

        Args:
            tab_name: Tab ID (e.g., 'epd', 'connectors')

        Returns:
            True if tab should be visible, False otherwise
        """
        settings = cls.get_visibility_settings()
        return settings.get(tab_name, True)

    @classmethod
    def set_tab_visibility(cls, tab_name: str, visible: bool) -> bool:
        """
        Set visibility for a specific tab.

        Args:
            tab_name: Tab ID
            visible: True to show, False to hide

        Returns:
            True if successful, False otherwise
        """
        settings = cls.get_visibility_settings()
        settings[tab_name] = visible
        return AppSettingsConfig.set_setting(cls.CONFIG_KEY, settings)


class SubTabVisibilityConfig:
    """
    Manages sub-tab visibility settings with persistence.

    Handles visibility state for sub-tabs within parent tabs
    (e.g., Search/Configuration tabs within Document Scanner).
    """

    CONFIG_KEY = "sub_tab_visibility"

    @classmethod
    def get_sub_tab_visibility(cls, parent_tab: str, sub_tab: str) -> bool:
        """
        Get visibility for a specific sub-tab.

        Args:
            parent_tab: Parent tab ID (e.g., 'document_scanner')
            sub_tab: Sub-tab ID (e.g., 'search')

        Returns:
            True if sub-tab should be visible, False otherwise
        """
        settings = AppSettingsConfig.get_setting(cls.CONFIG_KEY, {})

        # Get default from config
        if parent_tab in SUB_TAB_VISIBILITY_CONFIG:
            defaults = {cfg['id']: cfg['default']
                        for cfg in SUB_TAB_VISIBILITY_CONFIG[parent_tab]}
            default_visible = defaults.get(sub_tab, True)
        else:
            default_visible = True

        # Return saved setting or default
        parent_settings = settings.get(parent_tab, {})
        return parent_settings.get(sub_tab, default_visible)

    @classmethod
    def get_all_sub_tab_visibility(cls, parent_tab: str) -> Dict[str, bool]:
        """
        Get all sub-tab visibilities for a parent tab.

        Args:
            parent_tab: Parent tab ID

        Returns:
            Dictionary mapping sub-tab IDs to visibility state
        """
        settings = AppSettingsConfig.get_setting(cls.CONFIG_KEY, {})
        parent_settings = settings.get(parent_tab, {})

        # Merge with defaults
        if parent_tab in SUB_TAB_VISIBILITY_CONFIG:
            for sub_config in SUB_TAB_VISIBILITY_CONFIG[parent_tab]:
                sub_id = sub_config['id']
                if sub_id not in parent_settings:
                    parent_settings[sub_id] = sub_config['default']

        return parent_settings

    @classmethod
    def set_sub_tab_visibility(cls, parent_tab: str, sub_tab: str, visible: bool) -> bool:
        """
        Set visibility for a specific sub-tab.

        Args:
            parent_tab: Parent tab ID
            sub_tab: Sub-tab ID
            visible: True to show, False to hide

        Returns:
            True if successful
        """
        settings = AppSettingsConfig.get_setting(cls.CONFIG_KEY, {})

        if parent_tab not in settings:
            settings[parent_tab] = {}

        settings[parent_tab][sub_tab] = visible
        return AppSettingsConfig.set_setting(cls.CONFIG_KEY, settings)

    @classmethod
    def set_all_sub_tab_visibility(cls, parent_tab: str, visibility: Dict[str, bool]) -> bool:
        """
        Set all sub-tab visibilities for a parent tab.

        Args:
            parent_tab: Parent tab ID
            visibility: Dictionary mapping sub-tab IDs to visibility state

        Returns:
            True if successful
        """
        settings = AppSettingsConfig.get_setting(cls.CONFIG_KEY, {})
        settings[parent_tab] = visibility
        return AppSettingsConfig.set_setting(cls.CONFIG_KEY, settings)


class FeatureFlagsConfig:
    """
    Manages feature flags with persistence.

    Feature flags control optional functionality throughout the application.
    """

    CONFIG_KEY = "feature_flags"

    # Feature flag definitions: {flag_id: (display_name, description, default_value)}
    FEATURE_FLAGS = {
        'remote_docs_upload': (
            'Remote Docs Upload',
            'Show file upload section in Remote Documents tab',
            True
        ),
        # Add more feature flags here as needed
        # 'example_feature': ('Example Feature', 'Description of feature', False),
    }

    @classmethod
    def get_all_flags(cls) -> Dict[str, bool]:
        """
        Get all feature flags.

        Returns:
            Dictionary mapping flag IDs to enabled state (True/False)
        """
        settings = AppSettingsConfig.get_setting(cls.CONFIG_KEY, {})

        # Merge with defaults
        for flag_id, (name, desc, default) in cls.FEATURE_FLAGS.items():
            if flag_id not in settings:
                settings[flag_id] = default

        return settings

    @classmethod
    def is_enabled(cls, flag_id: str) -> bool:
        """
        Check if a feature flag is enabled.

        Args:
            flag_id: ID of the feature flag

        Returns:
            True if enabled, False otherwise
        """
        flags = cls.get_all_flags()
        return flags.get(flag_id, False)

    @classmethod
    def set_flag(cls, flag_id: str, enabled: bool) -> bool:
        """
        Set a feature flag.

        Args:
            flag_id: ID of the feature flag
            enabled: True to enable, False to disable

        Returns:
            True if successful, False otherwise
        """
        settings = cls.get_all_flags()
        settings[flag_id] = enabled
        return AppSettingsConfig.set_setting(cls.CONFIG_KEY, settings)
