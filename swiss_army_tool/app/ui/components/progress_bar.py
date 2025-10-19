"""
StandardProgressBar - Consistent progress bar component

A progress bar widget with consistent styling and behavior.

Parameters:
    show_percentage (bool): Show percentage text (default: True)
    minimum (int): Minimum value (default: 0)
    maximum (int): Maximum value (default: 100)
    parent (Optional[QWidget]): Parent widget

Signals:
    value_changed(int): Emitted when progress value changes

Methods:
    set_value(value: int): Sets progress value
    get_value() -> int: Returns current value
    set_range(minimum: int, maximum: int): Sets min/max range
    reset(): Resets progress to minimum
    set_text_visible(visible: bool): Show/hide percentage text

Example:
    >>> progress = StandardProgressBar(show_percentage=True)
    >>> progress.set_range(0, 100)
    >>> progress.value_changed.connect(lambda v: print(f"Progress: {v}%"))
    >>> progress.set_value(50)
"""

from PySide6.QtWidgets import QProgressBar
from PySide6.QtCore import Signal
from typing import Optional
from .constants import COMPONENT_SIZES


class StandardProgressBar(QProgressBar):
    """A progress bar widget with consistent styling"""

    # Re-expose signal for clarity
    value_changed = Signal(int)

    def __init__(
        self,
        show_percentage: bool = True,
        minimum: int = 0,
        maximum: int = 100,
        parent: Optional[QProgressBar] = None
    ):
        super().__init__(parent)
        self._setup_progress_bar(show_percentage, minimum, maximum)
        self._setup_styling()
        self._setup_signals()

    def _setup_progress_bar(self, show_percentage: bool, minimum: int, maximum: int):
        """Configure progress bar properties"""
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setValue(minimum)
        self.setTextVisible(show_percentage)
        self.setFixedHeight(COMPONENT_SIZES["progressbar_height"])

    def _setup_styling(self):
        """Apply consistent styling"""
        self.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: #f0f0f0;
                text-align: center;
                font-size: 9pt;
                color: #333333;
            }
            
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 2px;
            }
        """)

    def _setup_signals(self):
        """Connect internal signals"""
        super().valueChanged.connect(self.value_changed.emit)

    # Public API
    def set_value(self, value: int):
        """Sets progress value

        Args:
            value: Progress value (within min/max range)
        """
        self.setValue(value)

    def get_value(self) -> int:
        """Returns current progress value"""
        return self.value()

    def set_range(self, minimum: int, maximum: int):
        """Sets progress range

        Args:
            minimum: Minimum value
            maximum: Maximum value
        """
        self.setMinimum(minimum)
        self.setMaximum(maximum)

    def reset(self):
        """Resets progress to minimum value"""
        self.setValue(self.minimum())

    def set_text_visible(self, visible: bool):
        """Show or hide percentage text

        Args:
            visible: True to show percentage, False to hide
        """
        self.setTextVisible(visible)
