"""
Document Scanner Module - Main tab containing Search, Configuration, and History sub-tabs
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from app.document_scanner.Search.presenter import SearchPresenter
from app.document_scanner.Configuration.presenter import ConfigurationPresenter
from app.document_scanner.History.presenter import HistoryPresenter
from app.document_scanner.document_scanner_model import DocumentScannerModel


class DocumentScannerModuleView(QWidget):
    """Main Document Scanner module containing Search, Configuration, and History tabs"""

    def __init__(self, context):
        super().__init__()
        self.context = context

        # Create shared model
        self.model = DocumentScannerModel()

        # Create sub-presenters (pass model to them)
        self.search_presenter = SearchPresenter(context, self.model)
        self.configuration_presenter = ConfigurationPresenter(context, self.model)
        self.history_presenter = HistoryPresenter(context)

        # Connect model to presenters
        self.model.documents_changed.connect(
            self.search_presenter.on_documents_changed
        )
        self.model.documents_changed.connect(
            self.configuration_presenter.on_documents_changed
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

        layout.addWidget(self.tabs)

    def start_loading(self):
        """Start loading data - model loads documents in background thread"""
        print("Document Scanner: Starting...")
        
        # Load documents from config file (happens in background thread)
        self.model.load_from_config()
        
        # Initialize presenters
        current_index = self.tabs.currentIndex()
        if current_index == 0:  # Search tab
            self.search_presenter.start_loading()
        elif current_index == 1:  # Configuration tab
            self.configuration_presenter.start_loading()
        elif current_index == 2:  # History tab
            self.history_presenter.start_loading()

    def get_current_presenter(self):
        """Get the presenter for the currently active tab"""
        current_index = self.tabs.currentIndex()

        if current_index == 0:
            return self.search_presenter
        elif current_index == 1:
            return self.configuration_presenter
        elif current_index == 2:
            return self.history_presenter

        return None
