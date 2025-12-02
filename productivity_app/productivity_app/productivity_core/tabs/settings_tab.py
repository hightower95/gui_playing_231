"""
Settings Tab - Application configuration and tab visibility controls
"""
from ..document_scanner.document_scanner_tab import DocumentScannerModuleView
from ..connector.connector_tab import ConnectorModuleView
from ..epd.epd_tab import EpdModuleView
from ..devops.devops_tab import DevOpsModuleView
from typing import Dict, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QMessageBox, QCheckBox, QScrollArea
)
from PySide6.QtCore import Signal
from ..ui.components import (
    StandardLabel, TextStyle,
    StandardButton, ButtonRole,
    StandardGroupBox
)
from ..core.config_manager import AppSettingsConfig
from ..core.app_context import AppContext


# ============================================================================
# TAB VISIBILITY CONFIGURATION
# ============================================================================
# Define which tabs can be toggled on/off in Settings.
# Add new tabs here to automatically create checkboxes.
#
# IMPORTANT: The 'default' value MUST match the 'visible' field in TAB_CONFIG
# in main_window.py. This ensures consistent startup behavior.
# ============================================================================

TAB_VISIBILITY_CONFIG = [
    {'id': 'epd', 'label': 'EPD Tools',
        'tooltip': 'Show/hide the EPD Tools tab', 'default': False},
    {'id': 'connectors', 'label': 'Connectors',
        'tooltip': 'Show/hide the Connectors tab', 'default': True},
    {'id': 'fault_finding', 'label': 'Fault Finding',
        'tooltip': 'Show/hide the Fault Finding tab', 'default': False},
    {'id': 'document_scanner', 'label': 'Document Scanner',
        'tooltip': 'Show/hide the Document Scanner tab', 'default': True},
    {'id': 'remote_docs', 'label': 'Remote Docs',
        'tooltip': 'Show/hide the Remote Docs tab', 'default': False},
    {'id': 'devops', 'label': 'DevOps',
        'tooltip': 'Show/hide the DevOps tab', 'default': False},
]


# ============================================================================
# SUB-TAB VISIBILITY CONFIGURATION
# ============================================================================
# Define sub-tabs for modules that have internal tabs
# References constants from DocumentScannerModuleView to avoid magic strings
# Structure: {parent_tab_id: [{'id': 'subtab_id', 'label': 'Display Name', 'default': True}, ...]}
# ============================================================================

# Import sub-tab constants from modules

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
    # Add more modules with sub-tabs as needed
}


class TabVisibilityConfig:
    """Manages tab visibility settings with simple synchronous saves"""

    CONFIG_KEY = "tab_visibility"

    @classmethod
    def get_visibility_settings(cls) -> dict:
        """Get current visibility settings for all tabs

        Returns:
            Dictionary mapping tab names to visibility (True/False)
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
    def set_visibility_settings(cls, settings: dict) -> bool:
        """Save visibility settings

        Args:
            settings: Dictionary mapping tab names to visibility

        Returns:
            True if successful, False otherwise
        """
        return AppSettingsConfig.set_setting(cls.CONFIG_KEY, settings)

    @classmethod
    def get_tab_visibility(cls, tab_name: str) -> bool:
        """Get visibility for a specific tab

        Args:
            tab_name: Name of the tab (e.g., 'epd', 'connectors')

        Returns:
            True if tab should be visible, False otherwise
        """
        settings = cls.get_visibility_settings()
        return settings.get(tab_name, True)

    @classmethod
    def set_tab_visibility(cls, tab_name: str, visible: bool) -> bool:
        """Set visibility for a specific tab

        Args:
            tab_name: Name of the tab
            visible: True to show, False to hide

        Returns:
            True if successful, False otherwise
        """
        settings = cls.get_visibility_settings()
        settings[tab_name] = visible
        return AppSettingsConfig.set_setting(cls.CONFIG_KEY, settings)


class FeatureFlagsConfig:
    """Manages feature flags with simple synchronous saves"""

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
    def get_all_flags(cls) -> dict:
        """Get all feature flags

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
        """Check if a feature flag is enabled

        Args:
            flag_id: ID of the feature flag

        Returns:
            True if enabled, False otherwise
        """
        flags = cls.get_all_flags()
        return flags.get(flag_id, False)

    @classmethod
    def set_flag(cls, flag_id: str, enabled: bool) -> bool:
        """Set a feature flag

        Args:
            flag_id: ID of the feature flag
            enabled: True to enable, False to disable

        Returns:
            True if successful, False otherwise
        """
        settings = cls.get_all_flags()
        settings[flag_id] = enabled
        return AppSettingsConfig.set_setting(cls.CONFIG_KEY, settings)


class SubTabVisibilityConfig:
    """Manages sub-tab visibility settings"""

    CONFIG_KEY = "sub_tab_visibility"

    @classmethod
    def get_sub_tab_visibility(cls, parent_tab: str, sub_tab: str) -> bool:
        """Get visibility for a specific sub-tab

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
    def get_all_sub_tab_visibility(cls, parent_tab: str) -> dict:
        """Get all sub-tab visibilities for a parent tab

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
        """Set visibility for a specific sub-tab

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
    def set_all_sub_tab_visibility(cls, parent_tab: str, visibility: dict) -> bool:
        """Set all sub-tab visibilities for a parent tab

        Args:
            parent_tab: Parent tab ID
            visibility: Dictionary mapping sub-tab IDs to visibility state

        Returns:
            True if successful
        """
        settings = AppSettingsConfig.get_setting(cls.CONFIG_KEY, {})
        settings[parent_tab] = visibility
        return AppSettingsConfig.set_setting(cls.CONFIG_KEY, settings)


class SettingsTab(QWidget):
    """Settings tab for application configuration"""

    # Signal emitted when tab visibility changes
    # Emits tuple: (tab_name: str, visible: bool)
    tab_visibility_changed = Signal(str, bool)

    # Signal emitted when feature flag changes
    # Emits tuple: (flag_id: str, enabled: bool)
    feature_flag_changed = Signal(str, bool)

    # Signal emitted when any settings change
    settings_changed = Signal(dict)

    # Signal emitted when sub-tab visibility changes
    # Emits tuple: (parent_tab: str, sub_tab: str, visible: bool)
    sub_tab_visibility_changed = Signal(str, str, bool)

    def __init__(self, context: Optional[AppContext] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.context = context
        self.feature_flags = context.get('feature_flags') if context else None

        # Store checkboxes dynamically
        self.tab_checkboxes: Dict[str, QCheckBox] = {}
        # parent_tab -> {sub_tab_id -> checkbox}
        self.sub_tab_checkboxes: Dict[str, Dict[str, QCheckBox]] = {}
        # module_id -> {flag_id -> checkbox}
        self.feature_flag_checkboxes: Dict[str, Dict[str, QCheckBox]] = {}

        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title
        title = StandardLabel("Application Settings", style=TextStyle.TITLE)
        layout.addWidget(title)

        # Description
        description = StandardLabel(
            "Configure application behavior and tab visibility. Changes apply immediately.",
            style=TextStyle.NOTES
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        # Tab Visibility Section
        visibility_group = StandardGroupBox("Tab Visibility", collapsible=True)
        visibility_layout = QVBoxLayout()

        visibility_help = StandardLabel(
            "Control which tabs are visible in the application. "
            "Unchecking a tab will hide it immediately. "
            "You can always re-enable tabs from this Settings page.",
            style=TextStyle.NOTES
        )
        visibility_help.setWordWrap(True)
        visibility_layout.addWidget(visibility_help)

        # Create checkboxes dynamically from config
        form_layout = QFormLayout()
        form_layout.setSpacing(8)

        for tab_config in TAB_VISIBILITY_CONFIG:
            tab_id = tab_config['id']
            checkbox = QCheckBox(tab_config['label'])
            checkbox.setToolTip(tab_config['tooltip'])
            checkbox.clicked.connect(
                lambda checked, tid=tab_id: self._on_visibility_clicked(
                    tid, checked)
            )
            self.tab_checkboxes[tab_id] = checkbox
            form_layout.addRow("", checkbox)

            # Add sub-tabs if this tab has any
            if tab_id in SUB_TAB_VISIBILITY_CONFIG:
                self.sub_tab_checkboxes[tab_id] = {}

                for sub_config in SUB_TAB_VISIBILITY_CONFIG[tab_id]:
                    sub_tab_id = sub_config['id']
                    # Prefix with module ID for clarity
                    sub_label = f"{tab_id} → {sub_config['label']}"
                    sub_checkbox = QCheckBox(sub_label)
                    sub_checkbox.setToolTip(f"Show/hide {sub_config['label']}")
                    sub_checkbox.clicked.connect(
                        lambda checked, ptid=tab_id, stid=sub_tab_id: self._on_sub_tab_visibility_clicked(
                            ptid, stid, checked)
                    )
                    self.sub_tab_checkboxes[tab_id][sub_tab_id] = sub_checkbox

                    # Add with module ID prefix
                    form_layout.addRow("", sub_checkbox)

        visibility_layout.addLayout(form_layout)
        visibility_group.setLayout(visibility_layout)
        layout.addWidget(visibility_group)

        # Preset Buttons Section
        preset_group = StandardGroupBox("Quick Presets")
        preset_layout = QHBoxLayout()

        self.show_all_btn = StandardButton(
            "Show All Tabs", role=ButtonRole.SUCCESS)
        self.show_all_btn.clicked.connect(self._on_show_all)
        preset_layout.addWidget(self.show_all_btn)

        self.hide_all_btn = StandardButton(
            "Hide All Tabs", role=ButtonRole.SECONDARY)
        self.hide_all_btn.clicked.connect(self._on_hide_all)
        preset_layout.addWidget(self.hide_all_btn)

        preset_layout.addStretch()
        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)

        # Feature Flags Section
        flags_group = StandardGroupBox("Feature Flags", collapsible=True)
        flags_layout = QVBoxLayout()

        flags_help = StandardLabel(
            "Enable or disable experimental and optional features. "
            "Changes apply immediately.",
            style=TextStyle.NOTES
        )
        flags_help.setWordWrap(True)
        flags_layout.addWidget(flags_help)

        # Create scrollable area for feature flags
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(300)  # Limit height to make it scrollable

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(8)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        # If we have feature flags manager, use it
        if self.feature_flags:
            # Group flags by module
            all_flags = self.feature_flags.get_all_flags()

            for module_id, module_flags in sorted(all_flags.items()):
                # Skip empty modules
                if not module_flags:
                    continue

                # Module header
                module_label = StandardLabel(f"{module_id.replace('_', ' ').title()}",
                                             style=TextStyle.SECTION)
                scroll_layout.addWidget(module_label)

                # Module flags
                self.feature_flag_checkboxes[module_id] = {}

                for flag_id, is_enabled in module_flags.items():
                    # Get metadata
                    metadata = self.feature_flags.get_flag_metadata(
                        module_id, flag_id)
                    if metadata:
                        name, description, default = metadata

                        checkbox = QCheckBox(name)
                        checkbox.setToolTip(description)
                        checkbox.clicked.connect(
                            lambda checked, mid=module_id, fid=flag_id: self._on_feature_flag_clicked(
                                mid, fid, checked)
                        )
                        self.feature_flag_checkboxes[module_id][flag_id] = checkbox

                        # Add with indent
                        flag_layout = QHBoxLayout()
                        flag_layout.addSpacing(20)
                        flag_layout.addWidget(checkbox)
                        flag_layout.addStretch()
                        scroll_layout.addLayout(flag_layout)
        else:
            # Fallback to old config if no context
            if 'legacy' not in self.feature_flag_checkboxes:
                self.feature_flag_checkboxes['legacy'] = {}
            for flag_id, (name, description, default) in FeatureFlagsConfig.FEATURE_FLAGS.items():
                checkbox = QCheckBox(name)
                checkbox.setToolTip(description)
                checkbox.clicked.connect(
                    lambda checked, fid=flag_id: self._on_feature_flag_clicked(
                        'legacy', fid, checked)
                )
                self.feature_flag_checkboxes['legacy'][flag_id] = checkbox
                scroll_layout.addWidget(checkbox)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        flags_layout.addWidget(scroll_area)

        flags_group.setLayout(flags_layout)
        layout.addWidget(flags_group)

        # Action Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.reset_btn = StandardButton(
            "Reset to Defaults", role=ButtonRole.SECONDARY)
        self.reset_btn.clicked.connect(self._on_reset)
        button_layout.addWidget(self.reset_btn)

        layout.addLayout(button_layout)
        layout.addStretch()

    def _load_settings(self):
        """Load settings from config and update UI"""
        # Load tab visibility settings
        settings = TabVisibilityConfig.get_visibility_settings()

        # Update checkboxes from settings
        for tab_id, checkbox in self.tab_checkboxes.items():
            checkbox.blockSignals(True)
            checkbox.setChecked(settings.get(tab_id, True))
            checkbox.blockSignals(False)

        # Load sub-tab visibility settings
        for parent_tab, sub_tabs_dict in self.sub_tab_checkboxes.items():
            visibility = SubTabVisibilityConfig.get_all_sub_tab_visibility(
                parent_tab)
            for sub_tab_id, checkbox in sub_tabs_dict.items():
                checkbox.blockSignals(True)
                checkbox.setChecked(visibility.get(sub_tab_id, True))
                checkbox.blockSignals(False)

        # Load feature flags
        if self.feature_flags:
            for module_id, module_flags in self.feature_flag_checkboxes.items():
                if module_id == 'legacy':
                    continue
                for flag_id, checkbox in module_flags.items():
                    checkbox.blockSignals(True)
                    is_enabled = self.feature_flags.get(module_id, flag_id)
                    checkbox.setChecked(is_enabled)
                    checkbox.blockSignals(False)
        else:
            # Legacy fallback
            flags = FeatureFlagsConfig.get_all_flags()
            for flag_id, checkbox in self.feature_flag_checkboxes.get('legacy', {}).items():
                checkbox.blockSignals(True)
            checkbox.setChecked(flags.get(flag_id, False))
            checkbox.blockSignals(False)

    def _on_visibility_clicked(self, tab_name: str, checked: bool):
        """Handle checkbox clicked (uses clicked signal instead of stateChanged)

        Args:
            tab_name: Name of the tab
            checked: True if checkbox is now checked, False otherwise
        """
        print(f"[SettingsTab] Checkbox clicked: {tab_name} -> {checked}")

        # Update cache (instant, thread-safe, no file I/O in test mode)
        TabVisibilityConfig.set_tab_visibility(tab_name, checked)

        # Emit signals for UI update
        self.tab_visibility_changed.emit(tab_name, checked)
        self.settings_changed.emit(
            TabVisibilityConfig.get_visibility_settings())

        print(f"[SettingsTab] Signals emitted for {tab_name}")

    def _on_sub_tab_visibility_clicked(self, parent_tab: str, sub_tab: str, checked: bool):
        """Handle sub-tab checkbox clicked

        Args:
            parent_tab: Parent tab ID
            sub_tab: Sub-tab ID
            checked: True if checkbox is now checked, False otherwise
        """
        print(
            f"[SettingsTab] Sub-tab visibility clicked: {parent_tab}.{sub_tab} -> {checked}")

        # Update cache (instant, thread-safe)
        SubTabVisibilityConfig.set_sub_tab_visibility(
            parent_tab, sub_tab, checked)

        # Emit signal for UI update
        self.sub_tab_visibility_changed.emit(parent_tab, sub_tab, checked)

        print(f"[SettingsTab] Signals emitted for {parent_tab}.{sub_tab}")

    def _on_feature_flag_clicked(self, module_id: str, flag_id: str, checked: bool):
        """Handle feature flag checkbox clicked

        Args:
            module_id: Module ID of the feature flag
            flag_id: ID of the feature flag
            checked: True if checkbox is now checked, False otherwise
        """
        print(
            f"[SettingsTab] Feature flag clicked: {module_id}.{flag_id} -> {checked}")

        if self.feature_flags:
            # Update via FeatureFlagsManager
            self.feature_flags.set(module_id, flag_id, checked)
            print(
                f"[SettingsTab] Feature flag updated via manager for {module_id}.{flag_id}")
        else:
            # Legacy fallback
            FeatureFlagsConfig.set_flag(flag_id, checked)
            # Emit signal for UI update
            self.feature_flag_changed.emit(flag_id, checked)
            print(f"[SettingsTab] Feature flag signal emitted for {flag_id}")

    def _on_show_all(self):
        """Show all tabs"""
        for checkbox in self.tab_checkboxes.values():
            checkbox.setChecked(True)

        QMessageBox.information(
            self,
            "All Tabs Shown",
            "All tabs are now visible."
        )

    def _on_hide_all(self):
        """Hide all tabs (with warning)"""
        reply = QMessageBox.warning(
            self,
            "Hide All Tabs",
            "This will hide all tabs except Settings.\n\n"
            "You can re-enable tabs from this Settings page.\n\n"
            "Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            for checkbox in self.tab_checkboxes.values():
                checkbox.setChecked(False)

    def _on_reset(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Reset all settings to default values?\n\n"
            "This will show all tabs.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Reset to defaults from config
            defaults = {config['id']: config['default']
                        for config in TAB_VISIBILITY_CONFIG}
            TabVisibilityConfig.set_visibility_settings(defaults)
            self._load_settings()

            # Emit signals to update UI
            for tab_id, visible in defaults.items():
                self.tab_visibility_changed.emit(tab_id, visible)

            self.settings_changed.emit(defaults)

            QMessageBox.information(
                self,
                "Settings Reset",
                "Settings have been reset to defaults."
            )

    def get_tab_visibility(self, tab_name: str) -> bool:
        """Get visibility state for a tab

        Args:
            tab_name: Name of the tab

        Returns:
            True if tab should be visible
        """
        return TabVisibilityConfig.get_tab_visibility(tab_name)

    def is_tab_visible(self, tab_name: str) -> bool:
        """Alias for get_tab_visibility"""
        return self.get_tab_visibility(tab_name)
