"""Document tab - Input configuration for a single document"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame,
                               QFileDialog)
from PySide6.QtCore import Qt, Signal
from .source_selector import SourceSelector
from .file_drop_area import FileDropArea


class DocumentTab(QWidget):
    """Tab for configuring a single document input"""

    file_selected = Signal(str, str)  # Emits (input_name, file_path)

    def __init__(self, input_name: str, is_required: bool = True, parent=None):
        super().__init__(parent)
        self.input_name = input_name
        self.is_required = is_required
        self.selected_file = ""
        self._setup_ui()

    def _setup_ui(self):
        """Setup document tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Title with required indicator
        title_label = QLabel(
            self.input_name + (" *" if self.is_required else ""))
        title_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #e3e3e3;")
        layout.addWidget(title_label)

        # Required/Optional indicator
        status_label = QLabel("⭕ Required" if self.is_required else "Optional")
        status_label.setStyleSheet("color: #a3a3a3; font-size: 11px;")
        layout.addWidget(status_label)

        # Description text
        desc_text = self._get_detailed_description()
        desc_label = QLabel(desc_text)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(
            "color: #a3a3a3; font-size: 11px; margin-bottom: 8px;")
        layout.addWidget(desc_label)

        # Accepted formats
        formats_label = QLabel("Accepted formats: .xlsx, .csv, .xls")
        formats_label.setStyleSheet(
            "color: #888888; font-size: 10px; font-style: italic;")
        layout.addWidget(formats_label)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #3a3a3a; margin: 8px 0px;")
        layout.addWidget(line)

        # "or choose source" label
        source_label = QLabel("or choose source")
        source_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        source_label.setStyleSheet(
            "color: #888888; font-size: 11px; margin: 8px 0px;")
        layout.addWidget(source_label)

        # Source selection buttons
        self.source_selector = SourceSelector()
        self.source_selector.source_changed.connect(self._on_source_changed)
        layout.addWidget(self.source_selector)

        # Drag and drop area (shown when Upload is selected)
        self.drop_area = FileDropArea()
        self.drop_area.file_selected.connect(self._on_file_selected)
        self.drop_area.browse_clicked.connect(self._browse_for_file)
        layout.addWidget(self.drop_area, stretch=1)

        # Selected file display (initially hidden)
        self.selected_file_label = QLabel("")
        self.selected_file_label.setStyleSheet(
            "color: #4ec9b0; font-size: 11px; margin-top: 8px;")
        self.selected_file_label.setWordWrap(True)
        self.selected_file_label.hide()
        layout.addWidget(self.selected_file_label)

    def _on_source_changed(self, source: str):
        """Handle source selection change"""
        if source == 'upload':
            self.drop_area.show()
        else:
            self.drop_area.hide()
            # TODO: Show server/cache file browsers

    def _browse_for_file(self):
        """Open file browser dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select {self.input_name}",
            "",
            "All Files (*);;CSV Files (*.csv);;Excel Files (*.xlsx *.xls)"
        )

        if file_path:
            self._on_file_selected(file_path)

    def _on_file_selected(self, file_path: str):
        """Handle file selection"""
        self.selected_file = file_path
        self.selected_file_label.setText(f"✓ Selected: {file_path}")
        self.selected_file_label.show()
        self.file_selected.emit(self.input_name, file_path)

    def _get_detailed_description(self) -> str:
        """Get detailed description for this input"""
        if "parts" in self.input_name.lower() or "list" in self.input_name.lower():
            return "Upload the master parts list for comparison. This should include all parts that are expected to be in inventory."
        elif "inventory" in self.input_name.lower():
            return "Current inventory snapshot"
        elif "bom" in self.input_name.lower():
            return "Optional BOM for cross-reference"
        else:
            return "Required input for report generation"

    def get_selected_file(self) -> str:
        """Get the selected file path"""
        return self.selected_file
