"""Source selector - Upload/Server/Cache buttons"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal
from .styles import SOURCE_BUTTON_SELECTED_STYLE, SOURCE_BUTTON_UNSELECTED_STYLE


class SourceSelector(QWidget):
    """Three-button source selector"""

    source_changed = Signal(str)  # Emits: 'upload', 'server', or 'cache'

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_source = 'upload'
        self._setup_ui()

    def _setup_ui(self):
        """Setup source selector UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Upload button
        self.upload_btn = QPushButton("Upload")
        self.upload_btn.setCheckable(True)
        self.upload_btn.setChecked(True)
        self.upload_btn.setStyleSheet(SOURCE_BUTTON_SELECTED_STYLE)
        self.upload_btn.clicked.connect(
            lambda: self._on_source_selected('upload'))

        # From Server button
        self.server_btn = QPushButton("From Server")
        self.server_btn.setCheckable(True)
        self.server_btn.setStyleSheet(SOURCE_BUTTON_UNSELECTED_STYLE)
        self.server_btn.clicked.connect(
            lambda: self._on_source_selected('server'))

        # From Cache button
        self.cache_btn = QPushButton("From Cache")
        self.cache_btn.setCheckable(True)
        self.cache_btn.setStyleSheet(SOURCE_BUTTON_UNSELECTED_STYLE)
        self.cache_btn.clicked.connect(
            lambda: self._on_source_selected('cache'))

        # Add icons
        self.upload_btn.setIcon(self.upload_btn.style().standardIcon(
            self.upload_btn.style().StandardPixmap.SP_ArrowUp))
        self.server_btn.setIcon(self.server_btn.style().standardIcon(
            self.server_btn.style().StandardPixmap.SP_DriveNetIcon))
        self.cache_btn.setIcon(self.cache_btn.style().standardIcon(
            self.cache_btn.style().StandardPixmap.SP_DirIcon))

        layout.addWidget(self.upload_btn, stretch=1)
        layout.addWidget(self.server_btn, stretch=1)
        layout.addWidget(self.cache_btn, stretch=1)

    def _on_source_selected(self, source: str):
        """Handle source button click"""
        if source == 'upload':
            self.upload_btn.setChecked(True)
            self.server_btn.setChecked(False)
            self.cache_btn.setChecked(False)
            self.upload_btn.setStyleSheet(SOURCE_BUTTON_SELECTED_STYLE)
            self.server_btn.setStyleSheet(SOURCE_BUTTON_UNSELECTED_STYLE)
            self.cache_btn.setStyleSheet(SOURCE_BUTTON_UNSELECTED_STYLE)
        elif source == 'server':
            self.upload_btn.setChecked(False)
            self.server_btn.setChecked(True)
            self.cache_btn.setChecked(False)
            self.upload_btn.setStyleSheet(SOURCE_BUTTON_UNSELECTED_STYLE)
            self.server_btn.setStyleSheet(SOURCE_BUTTON_SELECTED_STYLE)
            self.cache_btn.setStyleSheet(SOURCE_BUTTON_UNSELECTED_STYLE)
        elif source == 'cache':
            self.upload_btn.setChecked(False)
            self.server_btn.setChecked(False)
            self.cache_btn.setChecked(True)
            self.upload_btn.setStyleSheet(SOURCE_BUTTON_UNSELECTED_STYLE)
            self.server_btn.setStyleSheet(SOURCE_BUTTON_UNSELECTED_STYLE)
            self.cache_btn.setStyleSheet(SOURCE_BUTTON_SELECTED_STYLE)

        self._current_source = source
        self.source_changed.emit(source)

    def get_current_source(self) -> str:
        """Get currently selected source"""
        return self._current_source
