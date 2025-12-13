"""
Search Input - Text input field for searching reports

Provides styled search input with placeholder.
"""
from typing import Optional
from PySide6.QtWidgets import QWidget, QLineEdit
from PySide6.QtCore import Signal


class SearchInput(QLineEdit):
    """Styled search input field"""

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize search input"""
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the input styling"""
        self.setPlaceholderText("Search reports...")
        self.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                background-color: #2a2a2a;
                color: #ffffff;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 1px solid #4fc3f7;
            }
        """)
