"""All Reports item widget - special case for the top-level all reports view"""
from typing import Optional
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal


class AllReportsItem(QWidget):
    """Special widget for 'All Reports' - no arrow, starts where arrow would be"""

    # Signals
    clicked = Signal()  # Simple signal - just means "clear topic selections"

    def __init__(
        self,
        count: int = 0,
        parent: Optional[QWidget] = None
    ):
        """Initialize all reports item

        Args:
            count: Total number of reports
            parent: Parent widget
        """
        super().__init__(parent)
        self.count = count
        self._setup_ui()

    def _setup_ui(self):
        """Setup the all reports item UI"""
        self.setFixedHeight(32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 2, 10, 2)
        layout.setSpacing(4)

        # "All Reports" label - prominent typography
        self.name_label = QLabel("All Reports")
        self.name_label.setStyleSheet("""
            QLabel {
                font-size: 12pt;
                color: #E0E0E0;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(self.name_label, stretch=1)

        # Count badge (fixed width for alignment)
        self.count_label = QLabel(str(self.count))
        self.count_label.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                color: #909090;
                background: transparent;
                border: none;
            }
        """)
        self.count_label.setFixedWidth(40)
        self.count_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.count_label)

        # Initial styling
        self._update_style(False)

    def _update_style(self, hovered: bool):
        """Update widget styling based on hover state

        Args:
            hovered: Whether the widget is being hovered
        """
        if hovered:
            self.setStyleSheet("""
                QWidget {
                    background-color: #2a2a2a;
                    border-radius: 6px;
                }
            """)
            self.name_label.setStyleSheet("""
                QLabel {
                    font-size: 12pt;
                    color: #ffffff;
                    background: transparent;
                    border: none;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: transparent;
                    border-radius: 6px;
                }
            """)
            self.name_label.setStyleSheet("""
                QLabel {
                    font-size: 12pt;
                    color: #E0E0E0;
                    background: transparent;
                    border: none;
                }
            """)

    def enterEvent(self, event):
        """Handle mouse enter"""
        self._update_style(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave"""
        self._update_style(False)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def update_count(self, new_count: int):
        """Update the count display

        Args:
            new_count: New count value
        """
        self.count = new_count
        self.count_label.setText(str(new_count))
