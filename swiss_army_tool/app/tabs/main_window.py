from PySide6.QtWidgets import QMainWindow, QTabWidget
from app.epd.epd_presenter import EpdPresenter
from app.presenters.connectors_presenter import ConnectorsPresenter
from app.presenters.fault_presenter import FaultFindingPresenter


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

        self.tabs.addTab(self.epd.view, self.epd.title)
        self.tabs.addTab(self.connectors.view, self.connectors.title)
        self.tabs.addTab(self.fault_finding.view, self.fault_finding.title)
