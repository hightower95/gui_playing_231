"""Report summary component - title and description"""
from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


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
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setObjectName("cardTitle")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(self.description)
        desc_label.setObjectName("cardDescription")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
