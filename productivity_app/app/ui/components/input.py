"""
StandardInput Component

A standardized text input box with consistent sizing and styling.

Parameters:
    placeholder (str): Placeholder text
    width (int, optional): Custom width in pixels (None uses standard 200px min)
    parent (QWidget, optional): Parent widget

Example:
    >>> input = StandardInput(placeholder="Enter search term...")
    >>> input = StandardInput(placeholder="File path...", width=400)
    >>> text = input.text()
    >>> input.setText("value")
"""
from PySide6.QtWidgets import QLineEdit, QWidget
from typing import Optional
from .constants import COMPONENT_SIZES


class StandardInput(QLineEdit):
    """Standardized text input box with consistent sizing and styling"""

    def __init__(
        self,
        placeholder: str = "",
        width: Optional[int] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        if placeholder:
            self.setPlaceholderText(placeholder)

        self._apply_size(width)
        self._apply_style()

    def _apply_size(self, custom_width: Optional[int] = None):
        """Apply size constraints"""
        self.setFixedHeight(COMPONENT_SIZES["input_standard_height"])

        if custom_width:
            self.setFixedWidth(custom_width)
        else:
            self.setMinimumWidth(COMPONENT_SIZES["input_standard_width"])

    def _apply_style(self):
        """Apply consistent styling"""
        self.setStyleSheet("""
            QLineEdit {
                padding: 4px 8px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                font-size: 10pt;
            }
            QLineEdit:hover {
                border-color: #0078d4;
            }
            QLineEdit:focus {
                border-color: #0078d4;
                border-width: 2px;
            }
        """)
