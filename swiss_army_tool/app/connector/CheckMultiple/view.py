"""
Check Multiple Connector View - Placeholder for future implementation
"""
from PySide6.QtWidgets import QLabel, QVBoxLayout
from PySide6.QtCore import Qt
from app.ui.base_sub_tab_view import BaseTabView


class CheckMultipleConnectorView(BaseTabView):
    """Placeholder view for checking multiple connectors"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_placeholder()

    def _setup_placeholder(self):
        """Setup placeholder content"""
        layout = QVBoxLayout(self.left_content_frame)
        layout.setContentsMargins(20, 20, 20, 20)

        placeholder = QLabel("Check Multiple Connectors\n\nComing Soon...")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                font-size: 18pt;
                color: #888888;
            }
        """)

        layout.addWidget(placeholder)
