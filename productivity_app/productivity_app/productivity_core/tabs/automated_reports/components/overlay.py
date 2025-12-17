"""Overlay widget - Semi-transparent backdrop for modal-like panels"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor


class OverlayWidget(QWidget):
    """Semi-transparent overlay that covers the entire view"""

    clicked_outside = Signal()  # Emitted when clicking outside content

    def __init__(self, parent=None):
        super().__init__(parent)
        self.content_widget = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup overlay UI"""
        # Fill parent
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        # Layout for centering content
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Container frame for content
        self.container = QFrame()
        self.container.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-radius: 12px;
                border: 1px solid #3a3a3a;
            }
        """)
        self.container.setMaximumWidth(1200)
        self.container.setMaximumHeight(800)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.container)

    def paintEvent(self, event):
        """Paint semi-transparent background"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Semi-transparent black background
        painter.fillRect(self.rect(), QColor(0, 0, 0, 180))

        super().paintEvent(event)

    def set_content(self, widget: QWidget):
        """Set the content widget to display in the overlay

        Args:
            widget: Widget to display centered in overlay
        """
        # Remove old content if exists
        if self.content_widget:
            self.container.layout().removeWidget(self.content_widget)
            self.content_widget.deleteLater()

        self.content_widget = widget
        self.container.layout().addWidget(widget)

    def mousePressEvent(self, event):
        """Handle clicks on the overlay (outside content)"""
        # Check if click is outside the container
        if not self.container.geometry().contains(event.pos()):
            self.clicked_outside.emit()
        super().mousePressEvent(event)
