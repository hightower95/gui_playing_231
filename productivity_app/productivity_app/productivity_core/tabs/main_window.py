from PySide6.QtWidgets import QMainWindow, QTabWidget
from PySide6.QtCore import QTimer
from typing import Dict, List, Optional, Any
from ..core.app_context import AppContext
from ..core.config import get_app_name
from .settings_tab import SettingsTab
from .tab_config import (
    get_default_focus_tab,
    get_tab_order
)
from .tab_loader import TabLoader


class MainWindow(QMainWindow):
    def __init__(self, services: AppContext):
        super().__init__()
        self.services = services

        # Set window title with app_name if not default
        title = "Engineering Toolkit"
        app_name = get_app_name()
        if app_name != "productivity_app":
            title = f"{title} ({app_name})"
        self.setWindowTitle(title)
        self.resize(1200, 800)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Tab loader handles lazy loading and dependency resolution
        self.tab_loader = TabLoader(self.services, self.tabs)
        self.tab_loader.tab_loaded.connect(self._on_tab_loaded)
        self.tab_loader.loading_complete.connect(self._on_loading_complete)
        self.tab_loader.loading_error.connect(self._on_loading_error)

        # Convenience property for accessing tab registry
        self.tab_registry = self.tab_loader.get_tab_registry()

        # Initialize Settings tab first (lightweight, always visible)
        print("[MainWindow] Initializing Settings tab...")
        self.settings_tab = SettingsTab(services=self.services)
        self.settings_tab.tab_visibility_changed.connect(
            self._on_tab_visibility_changed)
        self.settings_tab.feature_flag_changed.connect(
            self._on_feature_flag_changed)
        self.tabs.addTab(self.settings_tab, "⚙️ Settings")

        # Start lazy loading tabs in the background
        print("[MainWindow] Window ready, starting lazy tab loading...")
        self.tab_loader.start_loading()

    def _on_tab_loaded(self, tab_id: str, presenter, view, title: str):
        """
        Handle tab loaded signal from TabLoader.

        Args:
            tab_id: Tab identifier
            presenter: Tab presenter instance
            view: Tab view widget
            title: Tab display title
        """
        # Store presenter as instance attribute for direct access
        setattr(self, tab_id, presenter)

        # Initialize tab visibility service on first tab load
        tab_visibility_service = self.services.get('tab_visibility')
        if tab_visibility_service and not tab_visibility_service.is_initialized:
            tab_visibility_service.initialize(self.tabs, self.tab_registry)

        # Add tab if it should be visible
        # Check user settings for visibility
        user_visible = tab_visibility_service.is_tab_visible(
            tab_id) if tab_visibility_service else True

        if user_visible:
            if tab_visibility_service:
                # Don't persist on initial load
                tab_visibility_service.set_tab_as_visible(tab_id)

    def _on_loading_error(self, tab_id: str, error: Exception):
        """
        Handle tab loading error.

        Args:
            tab_id: Tab that failed to load
            error: Exception that occurred
        """
        print(f"[MainWindow] Tab '{tab_id}' failed to load: {error}")

    def _on_loading_complete(self):
        """Called when all tabs have been loaded"""
        print("[MainWindow] ✓ All tabs loaded successfully")
        self._loading_complete = True

        # Setup context providers (Phase 1: register defaults/stubs)
        from ..core.setup_context_providers import setup_context_providers
        setup_context_providers(self.services, self.tab_registry)

        # Connect sub-tab visibility changes
        self.settings_tab.sub_tab_visibility_changed.connect(
            self._on_sub_tab_visibility_changed)

        # Set default focus tab
        self._set_default_focus()

    def _set_default_focus(self):
        """Set focus to the default tab specified in configuration"""
        default_tab_id = get_default_focus_tab()
        if not default_tab_id:
            return

        if default_tab_id not in self.tab_registry:
            print(
                f"[MainWindow] Warning: Default focus tab '{default_tab_id}' not loaded")
            return

        # Use tab visibility service to set focus
        tab_visibility_service = self.services.get('tab_visibility')
        if tab_visibility_service:
            tab_visibility_service.set_focus(default_tab_id)

    def _on_tab_visibility_changed(self, tab_name: str, visible: bool):
        """
        Handle tab visibility change from Settings

        Args:
            tab_name: Name of tab (e.g., 'epd')
            visible: True to show, False to hide
        """
        print(f"[MainWindow] Tab visibility changed - {tab_name} -> {visible}")

        tab_visibility_service = self.services.get('tab_visibility')
        if tab_visibility_service:
            if visible:
                tab_visibility_service.set_tab_as_visible(tab_name, persist=True)
            else:
                tab_visibility_service.set_tab_as_hidden(tab_name, persist=True)

    def _on_feature_flag_changed(self, flag_id: str, enabled: bool):
        """
        Handle feature flag change from Settings

        Args:
            flag_id: ID of the feature flag that changed
            enabled: New state of the flag
        """
        print(f"MainWindow: Feature flag changed - {flag_id} -> {enabled}")

        # Notify remote docs presenter about upload flag changes (if loaded)
        if flag_id == 'remote_docs_upload':
            if hasattr(self, 'remote_docs'):
                self.remote_docs.on_feature_flag_changed(flag_id, enabled)
            else:
                print(
                    f"[MainWindow] Remote docs not loaded yet, flag will apply when loaded")

    def _on_sub_tab_visibility_changed(self, parent_tab: str, sub_tab: str, visible: bool):
        """Handle sub-tab visibility changes from Settings

        Args:
            parent_tab: Parent tab ID (e.g., 'document_scanner')
            sub_tab: Sub-tab ID (e.g., 'search')
            visible: New visibility state
        """
        from ..document_scanner.document_scanner_tab import DocumentScannerModuleView
        from ..connector.connector_tab import ConnectorModuleView
        from ..epd.epd_tab import EpdModuleView
        from ..devops.devops_tab import DevOpsModuleView
        from .visibility_persistence import SubTabVisibilityConfig

        print(
            f"MainWindow: Sub-tab visibility changed - {parent_tab}.{sub_tab} -> {visible}")

        if parent_tab == DocumentScannerModuleView.MODULE_ID and hasattr(self, 'document_scanner'):
            # Get current visibility state for all sub-tabs
            visibility = SubTabVisibilityConfig.get_all_sub_tab_visibility(
                DocumentScannerModuleView.MODULE_ID)
            self.document_scanner.sub_tab_visibility_updated(visibility)

        elif parent_tab == ConnectorModuleView.MODULE_ID and hasattr(self, 'connectors'):
            # Get current visibility state for all sub-tabs
            visibility = SubTabVisibilityConfig.get_all_sub_tab_visibility(
                ConnectorModuleView.MODULE_ID)
            self.connectors.sub_tab_visibility_updated(visibility)

        elif parent_tab == EpdModuleView.MODULE_ID and hasattr(self, 'epd'):
            # Get current visibility state for all sub-tabs
            visibility = SubTabVisibilityConfig.get_all_sub_tab_visibility(
                EpdModuleView.MODULE_ID)
            self.epd.sub_tab_visibility_updated(visibility)

        elif parent_tab == DevOpsModuleView.MODULE_ID and hasattr(self, 'devops'):
            # Get current visibility state for all sub-tabs
            visibility = SubTabVisibilityConfig.get_all_sub_tab_visibility(
                DevOpsModuleView.MODULE_ID)
            self.devops.sub_tab_visibility_updated(visibility)
