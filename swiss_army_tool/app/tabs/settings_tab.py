"""
Settings Tab - Application configuration and tab visibility controls
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QMessageBox, QCheckBox, QScrollArea
)
from PySide6.QtCore import Signal, QTimer, QThread, QObject
from app.ui.components import (
    StandardLabel, TextStyle,
    StandardButton, ButtonRole,
    StandardGroupBox
)
from app.core.config_manager import AppSettingsConfig
import threading


class ConfigSaveWorker(QObject):
    """Worker to save configuration in a background thread"""
    finished = Signal()
    error = Signal(str)

    def __init__(self, config_key: str, data: dict):
        super().__init__()
        self.config_key = config_key
        self.data = data.copy()  # Make a copy to avoid threading issues

    def run(self):
        """Save configuration to disk"""
        try:
            AppSettingsConfig.set_setting(self.config_key, self.data)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class TabVisibilityConfig:
    """Manages tab visibility settings with caching and threaded saves"""

    CONFIG_KEY = "tab_visibility"

    # Cache the settings in memory
    _cache = None
    _cache_lock = threading.Lock()
    _save_thread = None
    _save_worker = None

    # **TESTING MODE**: Set to False to enable file I/O
    _test_mode = False

    @classmethod
    def _load_cache(cls):
        """Load settings from disk into cache (called once on first access)"""
        with cls._cache_lock:
            if cls._cache is None:
                if cls._test_mode:
                    # TEST MODE: Skip file I/O, use defaults only
                    print(
                        "[TabVisibilityConfig] TEST MODE: Using in-memory defaults only")
                    settings = {}
                else:
                    settings = AppSettingsConfig.get_setting(
                        cls.CONFIG_KEY, {})

                # Default all tabs to visible if not configured
                defaults = {
                    'epd': True,
                    'connectors': True,
                    'fault_finding': True,
                    'document_scanner': True,
                    'remote_docs': True,
                    'devops': True
                }

                # Merge with saved settings
                for tab_name, default_visible in defaults.items():
                    if tab_name not in settings:
                        settings[tab_name] = default_visible

                cls._cache = settings
                print(f"[TabVisibilityConfig] Loaded cache: {cls._cache}")

    @classmethod
    def get_visibility_settings(cls) -> dict:
        """Get current visibility settings for all tabs (from cache)

        Returns:
            Dictionary mapping tab names to visibility (True/False)
        """
        cls._load_cache()
        with cls._cache_lock:
            return cls._cache.copy()

    @classmethod
    def set_visibility_settings(cls, settings: dict) -> bool:
        """Save visibility settings (to cache immediately, to disk in background)

        Args:
            settings: Dictionary mapping tab names to visibility

        Returns:
            True (always succeeds for cache, disk save is async)
        """
        cls._load_cache()
        with cls._cache_lock:
            cls._cache.update(settings)
            settings_to_save = cls._cache.copy()

        # Save to disk in background thread
        cls._save_to_disk_async(settings_to_save)
        return True

    @classmethod
    def get_tab_visibility(cls, tab_name: str) -> bool:
        """Get visibility for a specific tab (from cache)

        Args:
            tab_name: Name of the tab (e.g., 'epd', 'connectors')

        Returns:
            True if tab should be visible, False otherwise
        """
        settings = cls.get_visibility_settings()
        return settings.get(tab_name, True)

    @classmethod
    def set_tab_visibility(cls, tab_name: str, visible: bool) -> bool:
        """Set visibility for a specific tab (cache immediately, save async)

        Args:
            tab_name: Name of the tab
            visible: True to show, False to hide

        Returns:
            True (always succeeds for cache, disk save is async)
        """
        cls._load_cache()
        with cls._cache_lock:
            cls._cache[tab_name] = visible
            settings_to_save = cls._cache.copy()

        # Save to disk in background thread
        cls._save_to_disk_async(settings_to_save)
        return True

    @classmethod
    def _save_to_disk_async(cls, settings: dict):
        """Save settings to disk in a background thread (non-blocking)

        Args:
            settings: Settings dictionary to save
        """
        if cls._test_mode:
            # TEST MODE: Skip file I/O completely
            print(
                f"[TabVisibilityConfig] TEST MODE: Skipping disk save: {settings}")
            return

        # Use Python's threading for simple async save (no Qt dependencies needed)
        def save_worker():
            try:
                AppSettingsConfig.set_setting(cls.CONFIG_KEY, settings)
                print(f"[TabVisibilityConfig] Saved to disk: {settings}")
            except Exception as e:
                print(f"[TabVisibilityConfig] Error saving to disk: {e}")

        # Start background thread
        thread = threading.Thread(target=save_worker, daemon=True)
        thread.start()


class FeatureFlagsConfig:
    """Manages feature flags with caching and threaded saves"""

    CONFIG_KEY = "feature_flags"

    # Cache the settings in memory
    _cache = None
    _cache_lock = threading.Lock()

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
    def _load_cache(cls):
        """Load feature flags from disk into cache"""
        with cls._cache_lock:
            if cls._cache is None:
                settings = AppSettingsConfig.get_setting(cls.CONFIG_KEY, {})

                # Merge with defaults
                for flag_id, (name, desc, default) in cls.FEATURE_FLAGS.items():
                    if flag_id not in settings:
                        settings[flag_id] = default

                cls._cache = settings
                print(f"[FeatureFlagsConfig] Loaded cache: {cls._cache}")

    @classmethod
    def get_all_flags(cls) -> dict:
        """Get all feature flags (from cache)

        Returns:
            Dictionary mapping flag IDs to enabled state (True/False)
        """
        cls._load_cache()
        with cls._cache_lock:
            return cls._cache.copy()

    @classmethod
    def is_enabled(cls, flag_id: str) -> bool:
        """Check if a feature flag is enabled

        Args:
            flag_id: ID of the feature flag

        Returns:
            True if enabled, False otherwise
        """
        cls._load_cache()
        with cls._cache_lock:
            return cls._cache.get(flag_id, False)

    @classmethod
    def set_flag(cls, flag_id: str, enabled: bool) -> bool:
        """Set a feature flag (cache immediately, save async)

        Args:
            flag_id: ID of the feature flag
            enabled: True to enable, False to disable

        Returns:
            True (always succeeds for cache, disk save is async)
        """
        cls._load_cache()
        with cls._cache_lock:
            cls._cache[flag_id] = enabled
            settings_to_save = cls._cache.copy()

        # Save to disk in background thread
        cls._save_to_disk_async(settings_to_save)
        return True

    @classmethod
    def _save_to_disk_async(cls, settings: dict):
        """Save settings to disk in a background thread (non-blocking)

        Args:
            settings: Settings dictionary to save
        """
        def save_worker():
            try:
                AppSettingsConfig.set_setting(cls.CONFIG_KEY, settings)
                print(f"[FeatureFlagsConfig] Saved to disk: {settings}")
            except Exception as e:
                print(f"[FeatureFlagsConfig] Error saving to disk: {e}")

        # Start background thread
        thread = threading.Thread(target=save_worker, daemon=True)
        thread.start()


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

    def __init__(self, parent=None):
        super().__init__(parent)
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

        # Create checkboxes for each tab (using plain QCheckBox to eliminate custom widget issues)
        form_layout = QFormLayout()
        form_layout.setSpacing(8)

        # EPD Tools
        self.epd_checkbox = QCheckBox("EPD Tools")
        self.epd_checkbox.setToolTip("Show/hide the EPD Tools tab")
        self.epd_checkbox.clicked.connect(
            lambda checked, name='epd': self._on_visibility_clicked(name, checked))
        form_layout.addRow("", self.epd_checkbox)

        # Connectors
        self.connectors_checkbox = QCheckBox("Connectors")
        self.connectors_checkbox.setToolTip("Show/hide the Connectors tab")
        self.connectors_checkbox.clicked.connect(
            lambda checked, name='connectors': self._on_visibility_clicked(name, checked))
        form_layout.addRow("", self.connectors_checkbox)

        # Fault Finding
        self.fault_finding_checkbox = QCheckBox("Fault Finding")
        self.fault_finding_checkbox.setToolTip(
            "Show/hide the Fault Finding tab")
        self.fault_finding_checkbox.clicked.connect(
            lambda checked, name='fault_finding': self._on_visibility_clicked(name, checked))
        form_layout.addRow("", self.fault_finding_checkbox)

        # Document Scanner
        self.document_scanner_checkbox = QCheckBox("Document Scanner")
        self.document_scanner_checkbox.setToolTip(
            "Show/hide the Document Scanner tab")
        self.document_scanner_checkbox.clicked.connect(
            lambda checked, name='document_scanner': self._on_visibility_clicked(name, checked))
        form_layout.addRow("", self.document_scanner_checkbox)

        # Remote Docs
        self.remote_docs_checkbox = QCheckBox("Remote Docs")
        self.remote_docs_checkbox.setToolTip("Show/hide the Remote Docs tab")
        self.remote_docs_checkbox.clicked.connect(
            lambda checked, name='remote_docs': self._on_visibility_clicked(name, checked))
        form_layout.addRow("", self.remote_docs_checkbox)

        # DevOps
        self.devops_checkbox = QCheckBox("DevOps")
        self.devops_checkbox.setToolTip("Show/hide the DevOps tab")
        self.devops_checkbox.clicked.connect(
            lambda checked, name='devops': self._on_visibility_clicked(name, checked))
        form_layout.addRow("", self.devops_checkbox)

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
        scroll_area.setMaximumHeight(200)  # Limit height to make it scrollable

        scroll_widget = QWidget()
        scroll_layout = QFormLayout(scroll_widget)
        scroll_layout.setSpacing(8)

        # Store checkboxes for feature flags
        self.feature_flag_checkboxes = {}

        # Create checkbox for each feature flag
        for flag_id, (name, description, default) in FeatureFlagsConfig.FEATURE_FLAGS.items():
            checkbox = QCheckBox(name)
            checkbox.setToolTip(description)
            checkbox.clicked.connect(
                lambda checked, fid=flag_id: self._on_feature_flag_clicked(
                    fid, checked)
            )
            self.feature_flag_checkboxes[flag_id] = checkbox
            scroll_layout.addRow("", checkbox)

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

        # Block signals while loading to avoid triggering change events
        self.epd_checkbox.blockSignals(True)
        self.connectors_checkbox.blockSignals(True)
        self.fault_finding_checkbox.blockSignals(True)
        self.document_scanner_checkbox.blockSignals(True)
        self.remote_docs_checkbox.blockSignals(True)
        self.devops_checkbox.blockSignals(True)

        # Set checkbox states
        self.epd_checkbox.setChecked(settings.get('epd', True))
        self.connectors_checkbox.setChecked(settings.get('connectors', True))
        self.fault_finding_checkbox.setChecked(
            settings.get('fault_finding', True))
        self.document_scanner_checkbox.setChecked(
            settings.get('document_scanner', True))
        self.remote_docs_checkbox.setChecked(settings.get('remote_docs', True))
        self.devops_checkbox.setChecked(settings.get('devops', True))

        # Unblock signals
        self.epd_checkbox.blockSignals(False)
        self.connectors_checkbox.blockSignals(False)
        self.fault_finding_checkbox.blockSignals(False)
        self.document_scanner_checkbox.blockSignals(False)
        self.remote_docs_checkbox.blockSignals(False)
        self.devops_checkbox.blockSignals(False)

        # Load feature flags
        flags = FeatureFlagsConfig.get_all_flags()
        for flag_id, checkbox in self.feature_flag_checkboxes.items():
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

    def _on_feature_flag_clicked(self, flag_id: str, checked: bool):
        """Handle feature flag checkbox clicked

        Args:
            flag_id: ID of the feature flag
            checked: True if checkbox is now checked, False otherwise
        """
        print(f"[SettingsTab] Feature flag clicked: {flag_id} -> {checked}")

        # Update cache (instant, thread-safe)
        FeatureFlagsConfig.set_flag(flag_id, checked)

        # Emit signal for UI update
        self.feature_flag_changed.emit(flag_id, checked)

        print(f"[SettingsTab] Feature flag signal emitted for {flag_id}")

    def _get_checkbox_for_tab(self, tab_name: str):
        """Get checkbox widget for a tab name"""
        checkbox_map = {
            'epd': self.epd_checkbox,
            'connectors': self.connectors_checkbox,
            'fault_finding': self.fault_finding_checkbox,
            'document_scanner': self.document_scanner_checkbox,
            'remote_docs': self.remote_docs_checkbox,
            'devops': self.devops_checkbox
        }
        return checkbox_map.get(tab_name)

    def _on_show_all(self):
        """Show all tabs"""
        self.epd_checkbox.setChecked(True)
        self.connectors_checkbox.setChecked(True)
        self.fault_finding_checkbox.setChecked(True)
        self.document_scanner_checkbox.setChecked(True)
        self.remote_docs_checkbox.setChecked(True)
        self.devops_checkbox.setChecked(True)

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
            self.epd_checkbox.setChecked(False)
            self.connectors_checkbox.setChecked(False)
            self.fault_finding_checkbox.setChecked(False)
            self.document_scanner_checkbox.setChecked(False)
            self.remote_docs_checkbox.setChecked(False)
            self.devops_checkbox.setChecked(False)

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
            # Reset to defaults (all visible)
            defaults = {
                'epd': True,
                'connectors': True,
                'fault_finding': True,
                'document_scanner': True,
                'remote_docs': True,
                'devops': True
            }
            TabVisibilityConfig.set_visibility_settings(defaults)
            self._load_settings()

            # Emit signals to update UI
            for tab_name, visible in defaults.items():
                self.tab_visibility_changed.emit(tab_name, visible)

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
