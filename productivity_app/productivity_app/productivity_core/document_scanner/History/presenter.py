"""
Document Scanner History Presenter
"""
from PySide6.QtCore import QObject, Signal
from productivity_core.document_scanner.History.view import HistoryView
from typing import List


class HistoryPresenter(QObject):
    """Presenter for document scanner history"""

    # Signal to notify when a history item is selected
    search_requested = Signal(str)  # search_term

    def __init__(self, context, model):
        super().__init__()
        self.context = context
        self.model = model
        self.view = HistoryView()

        # Connect view signals
        self.view.history_item_selected.connect(self.on_history_item_selected)
        self.view.clear_history_requested.connect(self.on_clear_history)

    def start_loading(self):
        """Initialize the history tab"""
        print("Document Scanner History: Ready")
        self.refresh_history()

    def refresh_history(self):
        """Refresh the history display"""
        history = self.model.get_search_history()
        self.view.display_history(history)

    def on_history_item_selected(self, search_term: str):
        """Handle history item selection

        Args:
            search_term: The selected search term
        """
        print(f"History: Selected '{search_term}'")
        self.view.update_details(search_term)
        # Emit signal to trigger search in Search tab
        self.search_requested.emit(search_term)

    def on_clear_history(self):
        """Handle clear history request"""
        print("History: Clearing history")
        self.model.clear_search_history()
        self.refresh_history()

    def on_search_performed(self, search_term: str):
        """Called when a search is performed

        Args:
            search_term: The search term that was used
        """
        self.model.add_to_search_history(search_term)
        self.refresh_history()
