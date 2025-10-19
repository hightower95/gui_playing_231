"""
StandardDropArea Component

A standardized drag-and-drop area for file uploads.

Signals:
    file_dropped(str): Emitted when valid file is dropped (file path)

Parameters:
    label_text (str): Text to display in drop area
    allowed_extensions (tuple): Tuple of allowed file extensions (e.g., ('.csv', '.xlsx'))
    parent (QWidget, optional): Parent widget

Methods:
    clear(): Clear the drop area and reset to default state
    get_file_path(): Get the currently dropped file path (or None)

Visual States:
    - Default: Gray dashed border, light background
    - Hover: Darker background
    - Drag Active: Blue border, blue background
    - File Selected: Shows checkmark and filename

Example:
    >>> drop = StandardDropArea(
    ...     label_text="Drag & Drop CSV file here",
    ...     allowed_extensions=('.csv',)
    ... )
    >>> drop.file_dropped.connect(on_file_selected)
    >>> 
    >>> def on_file_selected(file_path: str):
    ...     print(f"File: {file_path}")
    ...     
    >>> file_path = drop.get_file_path()
    >>> drop.clear()
"""
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget, QMessageBox
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from typing import Optional
from .constants import COMPONENT_SIZES


class StandardDropArea(QFrame):
    """Standardized drag-and-drop area for file uploads"""

    file_dropped = Signal(str)

    def __init__(
        self,
        label_text: str = "Drag & Drop file here",
        allowed_extensions: tuple = ('.csv', '.xlsx', '.xls'),
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self.label_text = label_text
        self.allowed_extensions = allowed_extensions
        self.dropped_file_path = None

        self._setup_ui()

    def _setup_ui(self):
        """Setup drag-drop area UI"""
        self.setAcceptDrops(True)
        self.setFrameStyle(QFrame.Box | QFrame.Sunken)
        self.setMinimumHeight(COMPONENT_SIZES["drop_area_min_height"])

        layout = QVBoxLayout(self)
        self.label = QLabel(self.label_text)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet(
            "color: #333; font-weight: bold; font-size: 10pt;")
        layout.addWidget(self.label)

        self._apply_default_style()

    def _apply_default_style(self):
        """Apply default drop area styling"""
        self.setStyleSheet("""
            QFrame {
                background-color: #7E7E7E;
                border: 2px dashed #999;
                border-radius: 5px;
            }
            QFrame:hover {
                background-color: #6E6E6E;
                border-color: #666;
            }
        """)

    def _apply_active_style(self):
        """Apply styling when drag is over area"""
        self.setStyleSheet("""
            QFrame {
                background-color: #d0e8ff;
                border: 2px solid #0078d4;
                border-radius: 5px;
            }
        """)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._apply_active_style()

    def dragLeaveEvent(self, event):
        """Handle drag leave"""
        self._apply_default_style()

    def dropEvent(self, event: QDropEvent):
        """Handle file drop"""
        self._apply_default_style()

        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()

            # Check if file extension is allowed
            if file_path.lower().endswith(self.allowed_extensions):
                self.dropped_file_path = file_path

                # Update label to show filename
                import os
                filename = os.path.basename(file_path)
                self.label.setText(f"✓ File Selected:\n{filename}")

                # Emit signal
                self.file_dropped.emit(file_path)
                event.acceptProposedAction()
            else:
                # Invalid file type
                allowed = ", ".join(self.allowed_extensions)
                QMessageBox.warning(
                    self,
                    "Invalid File Type",
                    f"Please drop a file with one of these extensions:\n{allowed}"
                )

    def clear(self):
        """Clear the drop area"""
        self.dropped_file_path = None
        self.label.setText(self.label_text)
        self._apply_default_style()

    def get_file_path(self) -> Optional[str]:
        """Get the currently dropped file path

        Returns:
            File path or None if no file dropped
        """
        return self.dropped_file_path
