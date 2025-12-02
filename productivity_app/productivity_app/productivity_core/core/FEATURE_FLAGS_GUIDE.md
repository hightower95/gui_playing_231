"""
Feature Flags Implementation Guide

This example demonstrates how to implement and use feature flags in the application.
We use the Connector Advanced Search feature flag as our example.

SCHEMA DEFINITION
=================
Feature flags are defined in FeatureFlagsManager.FEATURE_FLAGS_SCHEMA organized by module:

    FEATURE_FLAGS_SCHEMA = {
        'connectors': {
            'advanced_search': (
                'Advanced Search',
                'Enable advanced search capabilities in Connector module',
                False  # default value
            ),
        },
    }

CHECKING AVAILABILITY
=====================
Before rendering a feature, check if it's enabled:

    feature_flags = context.get('feature_flags')
    if feature_flags.get('connectors', 'advanced_search'):
        # Show the feature
        search_button.setEnabled(True)
    else:
        # Hide or disable
        search_button.setText('Advanced Search (unavailable)')
        search_button.setEnabled(False)

SUBSCRIBING TO CHANGES
======================
Listen for flag changes and react dynamically:

    def on_advanced_search_changed(enabled):
        search_button.setEnabled(enabled)
        suffix = '' if enabled else ' (unavailable)'
        search_button.setText(f'Advanced Search{suffix}')
    
    feature_flags.subscribe('connectors', 'advanced_search', on_advanced_search_changed)

SETTING FLAGS
=============
Update flags programmatically (persists to storage):

    feature_flags.set('connectors', 'advanced_search', True)

READING MULTIPLE FLAGS
======================
Get all flags for a module at once:

    connector_flags = feature_flags.get_module_flags('connectors')
    # Returns: {'advanced_search': False, ...}

KEY POINTS
==========
- Flags are persisted to AppSettingsConfig
- Changes emit Qt signals for reactive UI updates
- Always check availability before showing features
- Use descriptive flag IDs and names
- Group flags logically by module/tab
"""

# Example usage in a UI component:
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt


class AdvancedSearchButton(QPushButton):
    """Example button that respects the advanced_search feature flag"""

    def __init__(self, context, parent=None):
        super().__init__('Advanced Search', parent)
        self.context = context
        self.feature_flags = context.get('feature_flags')
        
        # Subscribe to changes
        self.feature_flags.subscribe(
            'connectors', 
            'advanced_search', 
            self._on_flag_changed
        )
        
        # Initial state
        self._update_ui()

    def _update_ui(self):
        """Update button state based on flag value"""
        enabled = self.feature_flags.get('connectors', 'advanced_search')
        
        if enabled:
            self.setText('Advanced Search')
            self.setEnabled(True)
        else:
            self.setText('Advanced Search (unavailable)')
            self.setEnabled(False)

    def _on_flag_changed(self, enabled: bool):
        """Called when flag value changes"""
        self._update_ui()
