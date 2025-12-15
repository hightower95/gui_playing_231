"""Report summary component - title and description"""
from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetrics, QPaintEvent, QPainter


class ElidingLabel(QLabel):
    """Label that shows ellipsis when text is too long"""
    
    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self._full_text = text
        
    def setText(self, text: str):
        """Set the full text"""
        self._full_text = text
        super().setText(text)
        
    def paintEvent(self, event: QPaintEvent):
        """Custom paint to show elided text"""
        painter = QPainter(self)
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(self._full_text, Qt.TextElideMode.ElideRight, self.width())
        painter.drawText(self.rect(), self.alignment() | Qt.TextFlag.TextSingleLine, elided)


class ReportSummary(QWidget):
    """Summary section with title and description"""

    def __init__(
        self,
        title: str,
        description: str,
        parent: Optional[QWidget] = None
    ):
        """Initialize report summary

        Args:
            title: Report title
            description: Report description
            parent: Parent widget
        """
        super().__init__(parent)
        self.title = title
        self.description = description
        self._build_ui()

    def _build_ui(self):
        """Build summary UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)  # Tighter spacing for related content

        # Title with ellipsis support
        title_label = ElidingLabel(self.title)
        title_label.setObjectName("cardTitle")
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel(self.description)
        desc_label.setObjectName("cardDescription")
        desc_label.setWordWrap(True)
        # Constrain height to prevent card expansion
        # Description
        desc_label = QLabel(self.description)
        desc_label.setObjectName("cardDescription")
        desc_label.setWordWrap(True)
        desc_label.setMaximumHeight(90)  # Allow more text to show
        layout.addWidget(desc_label)