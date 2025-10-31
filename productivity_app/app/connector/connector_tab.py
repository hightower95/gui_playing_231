"""
Connector Module - Connector configuration and lookup interface with multiple sub-tabs
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PySide6.QtCore import QTimer
from app.connector.Lookup.presenter import LookupConnectorPresenter
from app.connector.CheckMultiple.presenter import CheckMultipleConnectorPresenter


class ConnectorModuleView(QWidget):
    """Main Connector module containing Lookup and Check Multiple tabs"""

    def __init__(self, context, connector_model):
        super().__init__()
        self.context = context
        self.connector_model = connector_model

        # Create sub-presenters
        self.lookup_presenter = LookupConnectorPresenter(
            context, connector_model)
        self.check_multiple_presenter = CheckMultipleConnectorPresenter(
            context, connector_model)

        # Connect signals for tab switching
        self.check_multiple_presenter.switch_to_lookup.connect(
            self._switch_to_lookup_with_search)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the tabbed interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        self.tabs = QTabWidget()

        # Add sub-tabs
        self.tabs.addTab(self.lookup_presenter.view, "Lookup")
        self.tabs.addTab(self.check_multiple_presenter.view, "Check Multiple")

        layout.addWidget(self.tabs)

    def start_loading(self):
        """Start loading data for the currently active tab"""
        current_index = self.tabs.currentIndex()

        if current_index == 0:  # Lookup tab
            self.lookup_presenter.start_loading()
        elif current_index == 1:  # Check Multiple tab
            self.check_multiple_presenter.start_loading()

    def get_current_presenter(self):
        """Get the presenter for the currently active tab"""
        current_index = self.tabs.currentIndex()

        if current_index == 0:
            return self.lookup_presenter
        elif current_index == 1:
            return self.check_multiple_presenter

        return None

    def _switch_to_lookup_with_search(self, part_numbers_str: str):
        """Switch to Lookup tab, populate search box, and automatically trigger search"""
        print(
            f"DEBUG CONNECTOR_TAB: _switch_to_lookup_with_search called with: {part_numbers_str[:100]}...")

        # Switch to Lookup tab (index 0)
        self.tabs.setCurrentIndex(0)
        print("DEBUG CONNECTOR_TAB: Switched to tab 0")

        # Populate the search box
        self.lookup_presenter.view.search_input.setText(part_numbers_str)
        print(
            f"DEBUG CONNECTOR_TAB: Set search text to: {part_numbers_str[:100]}...")

        # Trigger the search after a short delay to ensure UI is ready
        # This ensures the tab switch is complete before triggering the search
        def trigger_search():
            self.lookup_presenter.view.search_requested.emit(
                {'search_text': part_numbers_str}
            )
            print("DEBUG CONNECTOR_TAB: Emitted search_requested signal (delayed)")

        QTimer.singleShot(100, trigger_search)  # 100ms delay
        print("DEBUG CONNECTOR_TAB: Scheduled search trigger")
