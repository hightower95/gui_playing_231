"""
Document Scanner History View
"""
from PySide6.QtWidgets import QVBoxLayout, QLabel
from PySide6.QtCore import Signal
from app.ui.base_sub_tab_view import BaseTabView


class HistoryView(BaseTabView):
    """View for document scanner search history - placeholder for future implementation"""
    
    # Signals (for future use)
    history_item_selected = Signal(dict)
    clear_history_requested = Signal()
    export_history_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui_content()
    
    def _setup_ui_content(self):
        """Setup the history UI - placeholder for now"""
        # Update header
        self.header_frame.setFixedHeight(60)
        header_layout = QVBoxLayout(self.header_frame)
        header_layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title_label = QLabel("Search History")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        # Placeholder content in left content frame
        content_layout = QVBoxLayout(self.left_content_frame)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        placeholder_label = QLabel("History feature coming soon...")
        placeholder_label.setStyleSheet("color: gray; font-size: 12pt; font-style: italic;")
        content_layout.addWidget(placeholder_label)
        content_layout.addStretch()
        
        # Context area
        self.context_box.setPlaceholderText("History details will appear here...")
