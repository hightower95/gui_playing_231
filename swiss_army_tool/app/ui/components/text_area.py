"""
StandardTextArea - Consistent multi-line text component

A multi-line text edit widget with consistent styling and behavior.

Parameters:
    text (str): Initial text content (default: "")
    read_only (bool): Make text area read-only (default: False)
    placeholder (str): Placeholder text (default: "")
    height (Optional[int]): Fixed height in pixels (default: 120px)
    parent (Optional[QWidget]): Parent widget

Signals:
    text_changed(): Emitted when text content changes

Methods:
    get_text() -> str: Returns current text content
    set_text(text: str): Sets text content
    append_text(text: str): Appends text to existing content
    clear(): Clears all text
    set_read_only(read_only: bool): Sets read-only mode
    is_read_only() -> bool: Returns True if read-only

Example:
    >>> # Editable text area
    >>> text_area = StandardTextArea(placeholder="Enter notes...")
    >>> text_area.text_changed.connect(lambda: print("Text changed"))
    >>> 
    >>> # Read-only display area
    >>> display = StandardTextArea(read_only=True, height=200)
    >>> display.set_text("Read-only content")
"""

from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import Signal
from typing import Optional
from .constants import COMPONENT_SIZES


class StandardTextArea(QTextEdit):
    """A multi-line text edit widget with consistent styling"""

    # Re-expose signal for clarity
    text_changed = Signal()

    def __init__(
        self,
        text: str = "",
        read_only: bool = False,
        placeholder: str = "",
        height: Optional[int] = None,
        parent: Optional[QTextEdit] = None
    ):
        super().__init__(parent)
        self._setup_text_area(text, read_only, placeholder, height)
        self._setup_styling()
        self._setup_signals()

    def _setup_text_area(self, text: str, read_only: bool, placeholder: str, height: Optional[int]):
        """Configure text area properties"""
        self.setPlainText(text)
        self.setReadOnly(read_only)
        self.setPlaceholderText(placeholder)

        # Set height
        if height:
            self.setFixedHeight(height)
        else:
            self.setMinimumHeight(COMPONENT_SIZES["textarea_min_height"])
            self.setMaximumHeight(COMPONENT_SIZES["textarea_standard_height"])

    def _setup_styling(self):
        """Apply consistent styling"""
        self.setStyleSheet("""
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 6px;
                background-color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
                color: #333333;
            }
            
            QTextEdit:focus {
                border-color: #0078d4;
                outline: none;
            }
            
            QTextEdit:read-only {
                background-color: #f8f8f8;
                color: #666666;
            }
            
            QTextEdit:disabled {
                background-color: #f0f0f0;
                color: #999999;
                border-color: #cccccc;
            }
        """)

    def _setup_signals(self):
        """Connect internal signals"""
        super().textChanged.connect(self.text_changed.emit)

    # Public API
    def get_text(self) -> str:
        """Returns current text content"""
        return self.toPlainText()

    def set_text(self, text: str):
        """Sets text content

        Args:
            text: Text to set
        """
        self.setPlainText(text)

    def append_text(self, text: str):
        """Appends text to existing content

        Args:
            text: Text to append
        """
        self.append(text)

    def clear(self):
        """Clears all text content"""
        super().clear()

    def set_read_only(self, read_only: bool):
        """Sets read-only mode

        Args:
            read_only: True for read-only, False for editable
        """
        self.setReadOnly(read_only)

    def is_read_only(self) -> bool:
        """Returns True if text area is read-only"""
        return self.isReadOnly()
