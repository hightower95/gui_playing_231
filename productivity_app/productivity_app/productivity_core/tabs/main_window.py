from PySide6.QtWidgets import QMainWindow, QTabWidget
from PySide6.QtCore import QTimer
from typing import Dict, List, Optional, Any
from ..core.app_context import AppContext
from ..core.config import get_app_name
from .settings_tab import SettingsTab
from .tab_config import (
    TAB_CONFIG,
    get_tab_title,
    get_default_focus_tab,
    get_tab_order
)


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

        # Tab registry for managing dynamic visibility
        # Maps tab_id -> {'presenter': ..., 'view': ..., 'title': ...}
        self.tab_registry: Dict[str, Dict[str, Any]] = {}

        # Track loading state
        self._loading_complete = False
        self._pending_tabs: List[Dict] = []

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
        self._start_lazy_loading()

    def _start_lazy_loading(self):
        """Initialize lazy loading sequence for tabs"""
        # Create loading queue from config
        self._pending_tabs = [config.copy() for config in TAB_CONFIG]

        # Schedule the first tab to load
        self._schedule_next_tab()

    def _schedule_next_tab(self):
        """Schedule the next tab to load"""
        if not self._pending_tabs:
            # All tabs loaded
            self._on_loading_complete()
            return

        tab_config = self._pending_tabs.pop(0)

        # Schedule this tab to load after delay
        QTimer.singleShot(
            tab_config['delay_ms'],
            lambda: self._load_tab(tab_config)
        )

    def _load_tab(self, tab_config: Dict):
        """
        Load a tab from configuration and schedule the next one

        Args:
            tab_config: Tab configuration dict from TAB_CONFIG
        """
        tab_id = tab_config['id']
        print(f"[MainWindow] Loading {tab_id} tab...")

        try:
            # Check dependencies are loaded
            dependencies = tab_config.get('dependencies', [])
            if dependencies:
                for dep_id in dependencies:
                    if dep_id not in self.tab_registry:
                        print(
                            f"[MainWindow] Warning: Dependency '{dep_id}' not loaded, loading now...")
                        # Find and load dependency immediately
                        dep_config = next(
                            (cfg for cfg in TAB_CONFIG if cfg['id'] == dep_id), None)
                        if dep_config:
                            self._load_tab(dep_config)

            # Build dependency map for init_args
            dep_map = {dep_id: self.tab_registry[dep_id]['presenter']
                       for dep_id in dependencies if dep_id in self.tab_registry}

            # Get init arguments
            init_args_func = tab_config['init_args']
            init_args = init_args_func(self.services, dep_map)

            # Instantiate presenter/view
            presenter_class = tab_config['presenter_class']
            presenter = presenter_class(*init_args)

            # Get view (some classes are the view, others have .view property)
            if tab_config.get('view_from_presenter', True):
                view = presenter.view
                title = presenter.title
            else:
                view = presenter
                title = get_tab_title(tab_config)

            # Store in registry
            self.tab_registry[tab_id] = {
                'presenter': presenter,
                'view': view,
                'title': title
            }

            # Store presenter as instance attribute for direct access
            setattr(self, tab_id, presenter)

            # Initialize tab visibility service on first tab load
            tab_visibility_service = self.services.get('tab_visibility')
            if tab_visibility_service and not tab_visibility_service.is_initialized:
                tab_visibility_service.initialize(self.tabs, self.tab_registry)

            # Add tab if it should be visible
            # Check both: config default visibility AND user settings
            config_visible = tab_config.get('visible', True)
            user_visible = tab_visibility_service.is_tab_visible(
                tab_id) if tab_visibility_service else True

            if config_visible and user_visible:
                if tab_visibility_service:
                    # Don't persist on initial load
                    tab_visibility_service.show_tab(tab_id, persist=False)
                else:
                    # Fallback if service not available
                    position = self._calculate_tab_position(tab_id)
                    self.tabs.insertTab(position, view, title)

            print(f"[MainWindow] ✓ {tab_id} tab loaded")

        except Exception as e:
            print(f"[MainWindow] ✗ Error loading {tab_id} tab: {e}")
            import traceback
            traceback.print_exc()

        # Schedule next tab
        self._schedule_next_tab()

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
                tab_visibility_service.show_tab(tab_name)
            else:
                tab_visibility_service.hide_tab(tab_name)

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
