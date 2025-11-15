"""
EPD Module - Electronic Parts Data analysis interface with multiple sub-tabs
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from .SearchEpd.presenter import SearchEpdPresenter
from .IdentifyBestEpd.presenter import IdentifyBestEpdPresenter


class EpdModuleView(QWidget):
    """Main EPD module containing SearchEpd and IdentifyBestEpd tabs"""

    def __init__(self, context, epd_model):
        super().__init__()
        self.context = context
        self.epd_model = epd_model

        # Create sub-presenters
        self.search_presenter = SearchEpdPresenter(context, epd_model)
        self.identify_presenter = IdentifyBestEpdPresenter(context, epd_model)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the tabbed interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        self.tabs = QTabWidget()

        # Add sub-tabs
        self.tabs.addTab(self.search_presenter.view, "Search EPD")
        self.tabs.addTab(self.identify_presenter.view, "Identify Best EPD")

        layout.addWidget(self.tabs)

    def start_loading(self):
        """Start loading data for the currently active tab"""
        current_index = self.tabs.currentIndex()

        if current_index == 0:  # Search EPD tab
            self.search_presenter.start_loading()
        elif current_index == 1:  # Identify Best EPD tab
            self.identify_presenter.start_loading()

    def get_current_presenter(self):
        """Get the presenter for the currently active tab"""
        current_index = self.tabs.currentIndex()

        if current_index == 0:
            return self.search_presenter
        elif current_index == 1:
            return self.identify_presenter

        return None
