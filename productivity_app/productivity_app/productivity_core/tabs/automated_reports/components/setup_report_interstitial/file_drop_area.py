"""File drop area - Drag and drop or browse for files"""
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal
from .styles import DROP_AREA_STYLE


class FileDropArea(QFrame):
    """Drag and drop area for file selection"""

    file_selected = Signal(str)  # Emits file path
    browse_clicked = Signal()  # Emits when browse is clicked

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup drop area UI"""
        self.setStyleSheet(DROP_AREA_STYLE)
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        # Upload icon
        icon_label = QLabel("⬆")
        icon_label.setStyleSheet(
            "font-size: 48px; color: #666666; background: transparent; border: none;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Drag and drop text
        drag_text = QLabel("Drag and drop files here")
        drag_text.setStyleSheet(
            "color: #e3e3e3; font-size: 13px; background: transparent; border: none;")
        drag_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(drag_text)

        # "or" text
        or_label = QLabel("or")
        or_label.setStyleSheet(
            "color: #888888; font-size: 11px; background: transparent; border: none;")
        or_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(or_label)

        # Browse files button
        browse_btn = QPushButton("browse files")
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #4a9eff;
                font-size: 12px;
                text-decoration: underline;
                padding: 4px 8px;
            }
            QPushButton:hover {
                color: #6bb3ff;
            }
        """)
        browse_btn.clicked.connect(self.browse_clicked.emit)
        layout.addWidget(browse_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def dragEnterEvent(self, event):
        """Handle drag enter"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Handle drop event"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                self.file_selected.emit(file_path)
                event.acceptProposedAction()
