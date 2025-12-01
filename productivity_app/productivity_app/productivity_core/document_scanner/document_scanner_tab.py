"""
Document Scanner Module - Main tab containing Search, Configuration, History, and Compare Versions sub-tabs
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from ..document_scanner.Search.presenter import SearchPresenter
from ..document_scanner.Configuration.presenter import ConfigurationPresenter
from ..document_scanner.History.presenter import HistoryPresenter
from ..document_scanner.CompareVersions.presenter import CompareVersionsPresenter
from ..document_scanner.document_scanner_model import DocumentScannerModel


class DocumentScannerModuleView(QWidget):
    """Main Document Scanner module containing Search, Configuration, History, and Compare Versions tabs"""

    # ========================================================================
    # MODULE IDENTIFIER - Single source of truth for this module
    # ========================================================================
    # Used for tab registration and sub-tab visibility management
    # ========================================================================

    MODULE_ID = 'document_scanner'

    # ========================================================================
    # SUB-TAB IDENTIFIERS - Single source of truth
    # ========================================================================
    # All code that references sub-tabs should use these constants
    # When renaming: update here and everything else auto-updates
    # ========================================================================

    SUB_TAB_SEARCH = 'search'
    SUB_TAB_CONFIGURATION = 'configuration'
    SUB_TAB_HISTORY = 'history'
    SUB_TAB_COMPARE_VERSIONS = 'compare_versions'

    # Ordered list of all sub-tabs (used for iteration)
    SUB_TAB_ORDER = [
        SUB_TAB_SEARCH,
        SUB_TAB_CONFIGURATION,
        SUB_TAB_HISTORY,
        SUB_TAB_COMPARE_VERSIONS,
    ]

    # Display names (for UI labels)
    SUB_TAB_LABELS = {
        SUB_TAB_SEARCH: 'Search',
        SUB_TAB_CONFIGURATION: 'Configuration',
        SUB_TAB_HISTORY: 'History',
        SUB_TAB_COMPARE_VERSIONS: 'Compare Versions',
    }

    def __init__(self, context):
        super().__init__()
        self.context = context

        # Create shared model
        self.model = DocumentScannerModel()

        # Create sub-presenters (pass model to them)
        self.search_presenter = SearchPresenter(context, self.model)
        self.configuration_presenter = ConfigurationPresenter(
            context, self.model)
        self.history_presenter = HistoryPresenter(context, self.model)
        self.compare_versions_presenter = CompareVersionsPresenter(
            context, self.model)

        # Store sub-tabs mapping using constants
        self.sub_tabs = {
            self.SUB_TAB_SEARCH: (self.search_presenter.view, self.search_presenter),
            self.SUB_TAB_CONFIGURATION: (self.configuration_presenter.view, self.configuration_presenter),
            self.SUB_TAB_HISTORY: (self.history_presenter.view, self.history_presenter),
            self.SUB_TAB_COMPARE_VERSIONS: (self.compare_versions_presenter.view, self.compare_versions_presenter),
        }

        # Connect model to presenters
        self.model.documents_changed.connect(
            self.search_presenter.on_documents_changed
        )
        self.model.documents_changed.connect(
            self.configuration_presenter.on_documents_changed
        )

        # Connect search history changes to History presenter
        self.model.search_history_changed.connect(
            self.history_presenter.refresh_history
        )

        # Connect history to search
        self.history_presenter.search_requested.connect(
            self.on_history_search_requested
        )

        self._setup_ui()

        # Load saved configuration on startup
        self.start_loading()

    def _setup_ui(self):
        """Setup the tabbed interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        self.tabs = QTabWidget()

        # Add all sub-tabs
        self._add_sub_tabs()

        layout.addWidget(self.tabs)

    def _add_sub_tabs(self):
        """Add sub-tabs based on visibility settings"""
        from ..tabs.settings_tab import SubTabVisibilityConfig

        for sub_tab_id in self.SUB_TAB_ORDER:
            if sub_tab_id not in self.sub_tabs:
                continue

            view, presenter = self.sub_tabs[sub_tab_id]

            # Check if visible
            is_visible = SubTabVisibilityConfig.get_sub_tab_visibility(
                self.MODULE_ID, sub_tab_id)

            if is_visible:
                label = self.SUB_TAB_LABELS[sub_tab_id]
                self.tabs.addTab(view, label)

    def start_loading(self):
        """Start loading data - model loads documents in background thread"""
        print("Document Scanner: Starting...")

        # Load documents from config file (happens in background thread)
        self.model.load_from_config()

        # Initialize all presenters
        self.search_presenter.start_loading()
        self.configuration_presenter.start_loading()
        self.history_presenter.start_loading()
        self.compare_versions_presenter.start_loading()

    def on_history_search_requested(self, search_term: str):
        """Handle search request from history tab

        Args:
            search_term: The search term to search for
        """
        # Switch to search tab
        self.tabs.setCurrentIndex(0)

        # Populate search input and trigger search
        self.search_presenter.view.search_input.setText(search_term)
        self.search_presenter.on_search(search_term)

    def sub_tab_visibility_updated(self, sub_tab_names: dict):
        """Update sub-tab visibility

        Args:
            sub_tab_names: Dictionary mapping sub-tab IDs to visibility (True/False)
                          Example: {'search': True, 'configuration': False, 'history': True, 'compare_versions': False}
        """
        print(f"[DocumentScanner] Sub-tab visibility updated: {sub_tab_names}")

        # Clear existing tabs
        self.tabs.clear()

        # Re-add tabs based on new visibility
        for sub_tab_id in self.SUB_TAB_ORDER:
            if sub_tab_id not in self.sub_tabs:
                continue

            # Check new visibility
            if sub_tab_names.get(sub_tab_id, True):
                view, presenter = self.sub_tabs[sub_tab_id]
                label = self.SUB_TAB_LABELS[sub_tab_id]
                self.tabs.addTab(view, label)

        print(f"[DocumentScanner] Sub-tabs reloaded")

    def get_current_presenter(self):
        """Get the presenter for the currently active tab"""
        current_index = self.tabs.currentIndex()

        if current_index == 0:
            return self.search_presenter
        elif current_index == 1:
            return self.configuration_presenter
        elif current_index == 2:
            return self.history_presenter
        elif current_index == 3:
            return self.compare_versions_presenter

        return None
