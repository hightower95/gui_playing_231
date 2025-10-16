"""
Document Scanner History View
"""
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QListWidget, QListWidgetItem)
from PySide6.QtCore import Signal, Qt
from app.ui.base_sub_tab_view import BaseTabView
from typing import List, Dict


class HistoryView(BaseTabView):
    """View for document scanner search history"""

    # Signals
    history_item_selected = Signal(str)  # search_term
    clear_history_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui_content()

    def _setup_ui_content(self):
        """Setup the history UI"""
        # Update header
        self.header_frame.setFixedHeight(80)
        header_layout = QVBoxLayout(self.header_frame)
        header_layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title_label = QLabel("Search History")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        header_layout.addWidget(title_label)

        # Subtitle
        subtitle = QLabel("Click on a search term to re-run that search")
        subtitle.setStyleSheet("color: gray; font-size: 9pt;")
        header_layout.addWidget(subtitle)

        # Button row
        btn_row = QHBoxLayout()

        self.clear_btn = QPushButton("🗑️ Clear History")
        self.clear_btn.clicked.connect(self._on_clear_history)
        btn_row.addWidget(self.clear_btn)
        btn_row.addStretch()

        header_layout.addLayout(btn_row)

        # History list in left content frame
        content_layout = QVBoxLayout(self.left_content_frame)
        content_layout.setContentsMargins(10, 10, 10, 10)

        self.history_list = QListWidget()
        self.history_list.setAlternatingRowColors(True)
        self.history_list.itemClicked.connect(self._on_item_clicked)
        content_layout.addWidget(self.history_list)

        # Context area
        self.context_box.setPlaceholderText(
            "Click on a history item to see details...")

    def _on_item_clicked(self, item: QListWidgetItem):
        """Handle history item click"""
        search_term = item.data(Qt.UserRole)
        if search_term:
            self.history_item_selected.emit(search_term)

    def _on_clear_history(self):
        """Handle clear history button click"""
        self.clear_history_requested.emit()

    def display_history(self, history: List[str]):
        """Display search history

        Args:
            history: List of search terms (newest first)
        """
        self.history_list.clear()

        if not history:
            item = QListWidgetItem("No search history yet")
            item.setFlags(Qt.ItemIsEnabled)  # Not selectable
            item.setForeground(Qt.gray)
            self.history_list.addItem(item)
            self.clear_btn.setEnabled(False)
            return

        self.clear_btn.setEnabled(True)

        for idx, search_term in enumerate(history, 1):
            item = QListWidgetItem(f"{idx}. {search_term}")
            item.setData(Qt.UserRole, search_term)
            self.history_list.addItem(item)

    def update_details(self, search_term: str, timestamp: str = None):
        """Update context area with search details

        Args:
            search_term: The search term
            timestamp: When the search was performed (optional)
        """
        details = f"Search Term: {search_term}\n\n"
        if timestamp:
            details += f"Last Searched: {timestamp}\n\n"
        details += "Click to re-run this search in the Search tab"

        self.context_box.setPlainText(details)
