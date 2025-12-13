"""
Search Input - Text input field for searching reports

Provides styled search input with placeholder and search icon.
"""
from typing import Optional
from pathlib import Path
from PySide6.QtWidgets import QWidget, QLineEdit, QHBoxLayout
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import Signal, QByteArray
from PySide6.QtCore import Qt


class SearchInput(QWidget):
    """Styled search input field with search icon"""

    # Signal
    textChanged = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize search input"""
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the input styling"""
        # Make widget styled background aware
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        # Container styling with visible border
        self.setStyleSheet("""
            SearchInput {
                background-color: #2a2a2a;
                border: 1px solid #4a4a4a;
                border-radius: 10px;
            }
        """)
        self.setMinimumHeight(40)
        self.setMaximumHeight(40)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(10)

        # Search icon (SVG) - no circle background
        icon_dir = Path(__file__).parent
        search_icon_path = icon_dir / "search_25dp_E3E3E3_FILL0_wght200_GRAD0_opsz24.svg"

        # Cache SVG data
        with open(search_icon_path, 'rb') as f:
            search_icon_data = QByteArray(f.read())

        self.search_icon = QSvgWidget()
        self.search_icon.load(search_icon_data)
        self.search_icon.setFixedSize(20, 20)
        layout.addWidget(self.search_icon)

        # Text input (no border, blends with container)
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Search reports...")
        self.line_edit.setStyleSheet("""
            QLineEdit {
                border: none;
                background-color: transparent;
                color: #ffffff;
                font-size: 10pt;
                padding: 0;
            }
            QLineEdit:focus {
                outline: none;
            }
        """)
        self.line_edit.setMinimumHeight(30)
        self.line_edit.textChanged.connect(self.textChanged.emit)
        layout.addWidget(self.line_edit, stretch=1)

    def clear(self):
        """Clear the search input"""
        self.line_edit.clear()

    def text(self) -> str:
        """Get current text"""
        return self.line_edit.text()
