from PySide6.QtWidgets import QMainWindow, QTabWidget
from PySide6.QtCore import QTimer
from app.epd.epd_presenter import EpdPresenter
from app.presenters.connectors_presenter import ConnectorsPresenter
from app.presenters.fault_presenter import FaultFindingPresenter
from app.document_scanner import DocumentScannerModuleView
from app.connector.connector_context_provider import ConnectorContextProvider
from app.remote_docs import RemoteDocsPresenter
from app.tabs.settings_tab import SettingsTab


class MainWindow(QMainWindow):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.setWindowTitle("Engineering Toolkit")
        self.resize(1200, 800)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Tab registry for managing dynamic visibility
        self.tab_registry = {}

        # Track loading state
        self._loading_complete = False
        self._pending_tabs = []

        # Initialize Settings tab first (lightweight, always visible)
        print("[MainWindow] Initializing Settings tab...")
        self.settings_tab = SettingsTab()
        self.settings_tab.tab_visibility_changed.connect(
            self._on_tab_visibility_changed)
        self.settings_tab.feature_flag_changed.connect(
            self._on_feature_flag_changed)
        self.tabs.addTab(self.settings_tab, "⚙️ Settings")

        # Show a loading placeholder initially
        print("[MainWindow] Window ready, starting lazy tab loading...")

        # Start lazy loading tabs in the background
        self._start_lazy_loading()

    def _start_lazy_loading(self):
        """Initialize lazy loading sequence for tabs"""
        # Define loading order: most commonly used tabs first
        self._pending_tabs = [
            ('connectors', self._load_connectors_tab, 50),      # Load immediately
            # Load after 100ms
            ('epd', self._load_epd_tab, 100),
            # Load after 200ms
            ('document_scanner', self._load_document_scanner_tab, 200),
            # Load after 300ms
            ('fault_finding', self._load_fault_finding_tab, 300),
            ('remote_docs', self._load_remote_docs_tab,
             400),            # Load after 400ms
        ]

        # Schedule the first tab to load
        self._schedule_next_tab()

    def _schedule_next_tab(self):
        """Schedule the next tab to load"""
        if not self._pending_tabs:
            # All tabs loaded
            self._on_loading_complete()
            return

        tab_name, load_func, delay = self._pending_tabs.pop(0)

        # Schedule this tab to load after delay
        QTimer.singleShot(delay, lambda: self._load_tab(tab_name, load_func))

    def _load_tab(self, tab_name: str, load_func):
        """Load a tab and schedule the next one

        Args:
            tab_name: Name of the tab
            load_func: Function to call to load the tab
        """
        print(f"[MainWindow] Loading {tab_name} tab...")

        try:
            # Call the loading function
            load_func()
            print(f"[MainWindow] ✓ {tab_name} tab loaded")
        except Exception as e:
            print(f"[MainWindow] ✗ Error loading {tab_name} tab: {e}")
            import traceback
            traceback.print_exc()

        # Schedule next tab
        self._schedule_next_tab()

    def _load_connectors_tab(self):
        """Load the Connectors tab"""
        self.connectors = ConnectorsPresenter(self.context)
        self.tab_registry['connectors'] = {
            'presenter': self.connectors,
            'view': self.connectors.view,
            'title': self.connectors.title
        }

        # Add tab if it should be visible
        if self.settings_tab.is_tab_visible('connectors'):
            position = self._get_tab_position('connectors')
            self.tabs.insertTab(
                position, self.connectors.view, self.connectors.title)

    def _load_epd_tab(self):
        """Load the EPD tab"""
        self.epd = EpdPresenter(self.context)
        self.tab_registry['epd'] = {
            'presenter': self.epd,
            'view': self.epd.view,
            'title': self.epd.title
        }

        # Add tab if it should be visible
        if self.settings_tab.is_tab_visible('epd'):
            position = self._get_tab_position('epd')
            self.tabs.insertTab(position, self.epd.view, self.epd.title)

    def _load_document_scanner_tab(self):
        """Load the Document Scanner tab"""
        self.document_scanner = DocumentScannerModuleView(self.context)
        self.tab_registry['document_scanner'] = {
            'presenter': self.document_scanner,
            'view': self.document_scanner,
            'title': "Document Scanner"
        }

        # Add tab if it should be visible
        if self.settings_tab.is_tab_visible('document_scanner'):
            position = self._get_tab_position('document_scanner')
            self.tabs.insertTab(
                position, self.document_scanner, "Document Scanner")

    def _load_fault_finding_tab(self):
        """Load the Fault Finding tab (requires EPD to be loaded first)"""
        # Ensure EPD is loaded
        if not hasattr(self, 'epd'):
            print("[MainWindow] Warning: EPD not loaded yet, loading now...")
            self._load_epd_tab()

        self.fault_finding = FaultFindingPresenter(
            self.context, self.epd.model)
        self.tab_registry['fault_finding'] = {
            'presenter': self.fault_finding,
            'view': self.fault_finding.view,
            'title': self.fault_finding.title
        }

        # Add tab if it should be visible
        if self.settings_tab.is_tab_visible('fault_finding'):
            position = self._get_tab_position('fault_finding')
            self.tabs.insertTab(
                position, self.fault_finding.view, self.fault_finding.title)

    def _load_remote_docs_tab(self):
        """Load the Remote Docs tab"""
        self.remote_docs = RemoteDocsPresenter(self.context)
        self.tab_registry['remote_docs'] = {
            'presenter': self.remote_docs,
            'view': self.remote_docs.view,
            'title': self.remote_docs.title
        }

        # Add tab if it should be visible
        if self.settings_tab.is_tab_visible('remote_docs'):
            position = self._get_tab_position('remote_docs')
            self.tabs.insertTab(
                position, self.remote_docs.view, self.remote_docs.title)

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

    def _apply_initial_tab_visibility(self):
        """Apply saved tab visibility settings on startup

        Note: This is now handled during lazy loading
        """
        pass  # No longer needed - visibility handled in load functions

    def _on_tab_visibility_changed(self, tab_name: str, visible: bool):
        """Handle tab visibility change from Settings

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
        """Handle feature flag change from Settings

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
        """Show a tab by inserting it at the correct position

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
        """Hide a tab by removing it from the tab widget

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
        """Get the correct position to insert a tab

        Maintains the tab order: EPD -> Connectors -> Fault Finding -> 
                                Document Scanner -> Remote Docs -> Settings

        Args:
            tab_name: Name of tab to position

        Returns:
            Index where tab should be inserted
        """
        # Define desired order (excluding Settings which is always last)
        tab_order = ['epd', 'connectors', 'fault_finding',
                     'document_scanner', 'remote_docs']

        if tab_name not in tab_order:
            return self.tabs.count() - 1  # Before Settings tab

        target_index = tab_order.index(tab_name)

        # Count how many tabs before this one are currently visible
        position = 0
        for i in range(target_index):
            other_tab_name = tab_order[i]
            if other_tab_name in self.tab_registry:
                other_view = self.tab_registry[other_tab_name]['view']
                # Check if visible
                for j in range(self.tabs.count()):
                    if self.tabs.widget(j) == other_view:
                        position += 1
                        break

        return position
