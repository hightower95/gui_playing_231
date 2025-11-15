from PySide6.QtWidgets import QMainWindow, QTabWidget
from PySide6.QtCore import QTimer
from typing import Dict, List, Callable, Optional, Any
from ..epd.epd_presenter import EpdPresenter
from ..presenters.connectors_presenter import ConnectorsPresenter
from ..presenters.fault_presenter import FaultFindingPresenter
from ..document_scanner import DocumentScannerModuleView
from ..connector.connector_context_provider import ConnectorContextProvider
from ..remote_docs import RemoteDocsPresenter
from ..devops import DevOpsPresenter
from .settings_tab import SettingsTab


# ============================================================================
# TAB CONFIGURATION
# ============================================================================
# To add a new tab, just add an entry to this list with:
# - id: unique identifier (used in settings)
# - title: display title
# - presenter_class: the presenter/view class to instantiate
# - init_args: arguments to pass to __init__ (can be callable for dynamic values)
# - delay_ms: milliseconds to wait before loading (for lazy loading)
# - dependencies: list of tab IDs that must be loaded first (optional)
# ============================================================================

TAB_CONFIG = [
    {
        'id': 'connectors',
        'title': 'Connectors',
        'presenter_class': ConnectorsPresenter,
        'init_args': lambda ctx, deps: [ctx],
        'delay_ms': 50,
    },
    {
        'id': 'epd',
        'title': 'EPD',
        'presenter_class': EpdPresenter,
        'init_args': lambda ctx, deps: [ctx],
        'delay_ms': 100,
    },
    {
        'id': 'document_scanner',
        'title': 'Document Scanner',
        'presenter_class': DocumentScannerModuleView,
        'init_args': lambda ctx, deps: [ctx],
        'delay_ms': 200,
        'view_from_presenter': False,  # This class IS the view, not a presenter
    },
    {
        'id': 'fault_finding',
        'title': 'Fault Finding',
        'presenter_class': FaultFindingPresenter,
        'init_args': lambda ctx, deps: [ctx, deps['epd'].model],
        'delay_ms': 300,
        'dependencies': ['epd'],  # Requires EPD to be loaded first
    },
    {
        'id': 'remote_docs',
        'title': 'Remote Docs',
        'presenter_class': RemoteDocsPresenter,
        'init_args': lambda ctx, deps: [ctx],
        'delay_ms': 400,
    },
    {
        'id': 'devops',
        'title': 'DevOps',
        'presenter_class': DevOpsPresenter,
        'init_args': lambda ctx, deps: [ctx],
        'delay_ms': 450,
    },
]


class MainWindow(QMainWindow):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.setWindowTitle("Engineering Toolkit")
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
        self.settings_tab = SettingsTab()
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
            init_args = init_args_func(self.context, dep_map)

            # Instantiate presenter/view
            presenter_class = tab_config['presenter_class']
            presenter = presenter_class(*init_args)

            # Get view (some classes are the view, others have .view property)
            if tab_config.get('view_from_presenter', True):
                view = presenter.view
                title = presenter.title
            else:
                view = presenter
                title = tab_config['title']

            # Store in registry
            self.tab_registry[tab_id] = {
                'presenter': presenter,
                'view': view,
                'title': title
            }

            # Store presenter as instance attribute for direct access
            setattr(self, tab_id, presenter)

            # Add tab if it should be visible
            if self.settings_tab.is_tab_visible(tab_id):
                position = self._get_tab_position(tab_id)
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

        # Register context providers now that all tabs are loaded
        if hasattr(self, 'connectors') and hasattr(self, 'document_scanner'):
            connector_context = ConnectorContextProvider(self.connectors.model)
            self.document_scanner.search_presenter.register_context_provider(
                connector_context)
            print("[MainWindow] ✓ Context providers registered")

    def _on_tab_visibility_changed(self, tab_name: str, visible: bool):
        """
        Handle tab visibility change from Settings

        Args:
            tab_name: Name of tab (e.g., 'epd')
            visible: True to show, False to hide
        """
        print(f"MainWindow: Tab visibility changed - {tab_name} -> {visible}")

        if visible:
            self._show_tab(tab_name)
        else:
            self._hide_tab(tab_name)

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

    def _show_tab(self, tab_name: str):
        """
        Show a tab by inserting it at the correct position

        Args:
            tab_name: Name of tab to show (e.g., 'epd')
        """
        try:
            if tab_name not in self.tab_registry:
                print(f"Warning: Tab '{tab_name}' not found in registry")
                return

            tab_info = self.tab_registry[tab_name]

            # Check if tab is already visible
            for i in range(self.tabs.count()):
                if self.tabs.widget(i) == tab_info['view']:
                    print(f"Tab '{tab_info['title']}' already visible")
                    return  # Already visible

            # Find correct position to insert
            position = self._get_tab_position(tab_name)

            # Insert tab at correct position
            self.tabs.insertTab(position, tab_info['view'], tab_info['title'])

            print(f"Shown tab: {tab_info['title']} at position {position}")

        except Exception as e:
            print(f"ERROR in _show_tab for {tab_name}: {e}")
            import traceback
            traceback.print_exc()

    def _hide_tab(self, tab_name: str):
        """
        Hide a tab by removing it from the tab widget

        Args:
            tab_name: Name of tab to hide (e.g., 'epd')
        """
        try:
            if tab_name not in self.tab_registry:
                print(f"Warning: Tab '{tab_name}' not found in registry")
                return

            tab_info = self.tab_registry[tab_name]

            # Find the tab index
            tab_index = -1
            for i in range(self.tabs.count()):
                if self.tabs.widget(i) == tab_info['view']:
                    tab_index = i
                    break

            if tab_index >= 0:
                self.tabs.removeTab(tab_index)
                print(f"Hidden tab: {tab_info['title']}")
            else:
                print(f"Tab '{tab_info['title']}' was not visible")

        except Exception as e:
            print(f"ERROR in _hide_tab for {tab_name}: {e}")
            import traceback
            traceback.print_exc()

    def _get_tab_position(self, tab_name: str) -> int:
        """
        Get the correct position to insert a tab based on TAB_CONFIG order

        Args:
            tab_name: Name of tab to position

        Returns:
            Index where tab should be inserted
        """
        # Get tab order from config (excluding settings which is always last)
        tab_order = [config['id'] for config in TAB_CONFIG]

        if tab_name not in tab_order:
            return self.tabs.count() - 1  # Before Settings tab

        target_index = tab_order.index(tab_name)

        # Count how many tabs before this one are currently visible
        position = 0
        for i in range(target_index):
            other_tab_id = tab_order[i]
            if other_tab_id in self.tab_registry:
                other_view = self.tab_registry[other_tab_id]['view']
                # Check if visible
                for j in range(self.tabs.count()):
                    if self.tabs.widget(j) == other_view:
                        position += 1
                        break

        return position
