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

        # Add sub-tabs
        self.tabs.addTab(self.search_presenter.view, "Search")
        self.tabs.addTab(self.configuration_presenter.view, "Configuration")
        self.tabs.addTab(self.history_presenter.view, "History")
        self.tabs.addTab(self.compare_versions_presenter.view,
                         "Compare Versions")

        layout.addWidget(self.tabs)

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
