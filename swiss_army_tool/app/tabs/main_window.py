from PySide6.QtWidgets import QMainWindow, QTabWidget
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
        self.setWindowTitle("Engineering Toolkit")
        self.resize(1200, 800)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Initialize Settings tab first
        self.settings_tab = SettingsTab()
        self.settings_tab.tab_visibility_changed.connect(
            self._on_tab_visibility_changed)
        self.settings_tab.feature_flag_changed.connect(
            self._on_feature_flag_changed)

        # Tab registry for managing dynamic visibility
        self.tab_registry = {}

        # Initialize presenters (which create their own views)
        self.epd = EpdPresenter(context)
        self.connectors = ConnectorsPresenter(context)
        self.fault_finding = FaultFindingPresenter(
            context, self.epd.model)
        self.document_scanner = DocumentScannerModuleView(context)
        self.remote_docs = RemoteDocsPresenter(context)

        # Register context providers with document scanner
        # This allows the connector tab to provide additional context to search results
        connector_context = ConnectorContextProvider(self.connectors.model)
        self.document_scanner.search_presenter.register_context_provider(
            connector_context)

        # Add tabs and register them
        # EPD Tab
        self.tab_registry['epd'] = {
            'presenter': self.epd,
            'view': self.epd.view,
            'title': self.epd.title
        }
        self.tabs.addTab(self.epd.view, self.epd.title)

        # Connectors Tab
        self.tab_registry['connectors'] = {
            'presenter': self.connectors,
            'view': self.connectors.view,
            'title': self.connectors.title
        }
        self.tabs.addTab(self.connectors.view, self.connectors.title)

        # Fault Finding Tab
        self.tab_registry['fault_finding'] = {
            'presenter': self.fault_finding,
            'view': self.fault_finding.view,
            'title': self.fault_finding.title
        }
        self.tabs.addTab(self.fault_finding.view, self.fault_finding.title)

        # Document Scanner Tab
        self.tab_registry['document_scanner'] = {
            'presenter': self.document_scanner,
            'view': self.document_scanner,
            'title': "Document Scanner"
        }
        self.tabs.addTab(self.document_scanner, "Document Scanner")

        # Remote Docs Tab
        self.tab_registry['remote_docs'] = {
            'presenter': self.remote_docs,
            'view': self.remote_docs.view,
            'title': self.remote_docs.title
        }
        self.tabs.addTab(self.remote_docs.view, self.remote_docs.title)

        # Add Settings tab at the end (always visible)
        self.tabs.addTab(self.settings_tab, "⚙️ Settings")

        # Apply initial tab visibility from saved settings
        self._apply_initial_tab_visibility()

    def _apply_initial_tab_visibility(self):
        """Apply saved tab visibility settings on startup"""
        # Apply visibility for all registered tabs
        for tab_name in self.tab_registry.keys():
            if not self.settings_tab.is_tab_visible(tab_name):
                self._hide_tab(tab_name)

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

        # Notify remote docs presenter about upload flag changes
        if flag_id == 'remote_docs_upload':
            self.remote_docs.on_feature_flag_changed(flag_id, enabled)

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
