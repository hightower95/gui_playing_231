from PySide6.QtWidgets import QMainWindow, QTabWidget
from PySide6.QtCore import QTimer
from typing import Dict, List, Optional, Any
from ..core.app_context import AppContext
from ..core.config import get_app_name
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
        if self.services.tab_visibility and not self.services.tab_visibility.is_initialized:
            self.services.tab_visibility.initialize(
                self.tabs, self.tab_registry)

        # Add tab if it should be visible
        # Check user settings for visibility
        user_visible = self.services.tab_visibility.is_tab_visible(
            tab_id) if self.services.tab_visibility else True

        # Special handling for start page - check if it should be shown this session
        # if tab_id == 'start_page':
        # from .start_page import StartPageView
        # if not StartPageView.should_show_on_startup():
        #     user_visible = False

        if user_visible:
            if self.services.tab_visibility:
                # Don't persist on initial load
                self.services.tab_visibility.set_tab_as_visible(tab_id)

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

        # Give Settings tab access to tab_registry so it can notify other tabs
        if 'settings' in self.tab_registry:
            settings_view = self.tab_registry['settings'].get('view')
            if settings_view and hasattr(settings_view, 'set_tab_registry'):
                settings_view.set_tab_registry(self.tab_registry)

        # Set default focus tab
        """Set focus to the default tab specified in configuration"""
        default_tab_id = get_default_focus_tab()
        if not default_tab_id:
            return

        if default_tab_id not in self.tab_registry:
            print(
                f"[MainWindow] Warning: Default focus tab '{default_tab_id}' not loaded")
            return

        # Use tab visibility service to set focus
        if self.services.tab_visibility:
            self.services.tab_visibility.set_focus(default_tab_id)

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
