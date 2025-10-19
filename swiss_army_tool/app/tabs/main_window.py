from PySide6.QtWidgets import QMainWindow, QTabWidget
from app.epd.epd_presenter import EpdPresenter
from app.presenters.connectors_presenter import ConnectorsPresenter
from app.presenters.fault_presenter import FaultFindingPresenter
from app.document_scanner import DocumentScannerModuleView
from app.connector.connector_context_provider import ConnectorContextProvider
from app.remote_docs import RemoteDocsPresenter


class MainWindow(QMainWindow):
    def __init__(self, context):
        super().__init__()
        self.setWindowTitle("Engineering Toolkit")
        self.resize(1200, 800)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

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

        self.tabs.addTab(self.epd.view, self.epd.title)
        self.tabs.addTab(self.connectors.view, self.connectors.title)
        self.tabs.addTab(self.fault_finding.view, self.fault_finding.title)
        self.tabs.addTab(self.document_scanner, "Document Scanner")
        self.tabs.addTab(self.remote_docs.view, self.remote_docs.title)
