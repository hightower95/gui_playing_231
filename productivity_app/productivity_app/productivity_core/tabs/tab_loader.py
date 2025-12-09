"""
Tab Loader

Handles lazy loading of tabs with dependency resolution and scheduling.
Separates tab loading logic from MainWindow for better organization.
"""

from typing import Dict, List, Any, Callable, Optional
from PySide6.QtWidgets import QTabWidget
from PySide6.QtCore import QTimer, QObject, Signal
from ..core.app_context import AppContext
from .tab_config import TAB_CONFIG, get_tab_title


class TabLoader(QObject):
    """
    Manages lazy loading of application tabs.

    Handles:
    - Sequential loading with configurable delays
    - Dependency resolution (loads dependencies first)
    - Tab instantiation and registration
    - Progress tracking and error handling

    Emits signals for loading events to allow MainWindow to react.
    """

    # Signals
    # (tab_id, presenter, view, title)
    tab_loaded = Signal(str, object, object, str)
    loading_complete = Signal()  # All tabs loaded
    loading_error = Signal(str, Exception)  # (tab_id, error)

    def __init__(self, services: AppContext, tab_widget: QTabWidget):
        """
        Initialize the tab loader.

        Args:
            services: Application service provider (dependency injection)
            tab_widget: The QTabWidget where tabs will be added
        """
        super().__init__()
        self.services = services
        self.tab_widget = tab_widget
        self.tab_registry: Dict[str, Dict[str, Any]] = {}
        self._pending_tabs: List[Dict] = []
        self._loading_complete = False

    def start_loading(self):
        """
        Start the lazy loading sequence.

        Loads tabs in order defined by TAB_CONFIG with configured delays.
        """
        print("[TabLoader] Starting lazy tab loading...")

        # Create loading queue from config
        self._pending_tabs = [config.copy() for config in TAB_CONFIG]

        # Schedule the first tab to load
        self._schedule_next_tab()

    def _schedule_next_tab(self):
        """Schedule the next tab in the queue to load."""
        if not self._pending_tabs:
            # All tabs loaded
            self._on_loading_complete()
            return

        tab_config = self._pending_tabs.pop(0)

        # Schedule this tab to load after its configured delay
        QTimer.singleShot(
            tab_config['delay_ms'],
            lambda: self._load_tab(tab_config)
        )

    def _load_tab(self, tab_config: Dict):
        """
        Load a single tab from configuration.

        Handles dependency resolution, instantiation, and registration.

        Args:
            tab_config: Tab configuration dict from TAB_CONFIG
        """
        tab_id = tab_config['id']
        print(f"[TabLoader] Loading {tab_id} tab...")

        try:
            # Check and resolve dependencies
            self._resolve_dependencies(tab_config)

            # Build dependency map for init_args
            dependencies = tab_config.get('dependencies', [])
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

            # Emit signal that tab was loaded
            self.tab_loaded.emit(tab_id, presenter, view, title)

            print(f"[TabLoader] ✓ {tab_id} tab loaded")

        except Exception as e:
            print(f"[TabLoader] ✗ Error loading {tab_id} tab: {e}")
            import traceback
            traceback.print_exc()

            # Emit error signal
            self.loading_error.emit(tab_id, e)

        # Schedule next tab
        self._schedule_next_tab()

    def _resolve_dependencies(self, tab_config: Dict):
        """
        Ensure all dependencies for a tab are loaded.

        If a dependency is not loaded, loads it immediately before continuing.

        Args:
            tab_config: Tab configuration dict
        """
        dependencies = tab_config.get('dependencies', [])
        if not dependencies:
            return

        for dep_id in dependencies:
            if dep_id not in self.tab_registry:
                print(
                    f"[TabLoader] Warning: Dependency '{dep_id}' not loaded, loading now...")

                # Find and load dependency immediately
                dep_config = next(
                    (cfg for cfg in TAB_CONFIG if cfg['id'] == dep_id), None)

                if dep_config:
                    self._load_tab(dep_config)
                else:
                    print(
                        f"[TabLoader] ERROR: Dependency '{dep_id}' not found in TAB_CONFIG")

    def _on_loading_complete(self):
        """Called when all tabs have been loaded."""
        print("[TabLoader] ✓ All tabs loaded successfully")
        self._loading_complete = True

        # Emit completion signal
        self.loading_complete.emit()

    def get_tab_registry(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the tab registry.

        Returns:
            Dict mapping tab_id -> {'presenter': ..., 'view': ..., 'title': ...}
        """
        return self.tab_registry

    def is_loading_complete(self) -> bool:
        """Check if all tabs have been loaded."""
        return self._loading_complete

    def get_presenter(self, tab_id: str) -> Optional[Any]:
        """
        Get a tab's presenter by ID.

        Args:
            tab_id: Tab identifier

        Returns:
            Presenter instance or None if not loaded
        """
        if tab_id in self.tab_registry:
            return self.tab_registry[tab_id]['presenter']
        return None
