"""
StandardSpinBox - Consistent numeric input component

A spin box widget for numeric input with consistent styling.

Parameters:
    min_value (int): Minimum value (default: 0)
    max_value (int): Maximum value (default: 100)
    default_value (int): Initial value (default: 0)
    suffix (str): Text suffix (e.g., " px", " %") (default: "")
    width (Optional[int]): Fixed width in pixels (default: 100px)
    parent (Optional[QWidget]): Parent widget

Signals:
    value_changed(int): Emitted when value changes

Methods:
    get_value() -> int: Returns current value
    set_value(value: int): Sets value
    set_range(min_value: int, max_value: int): Sets min/max range
    set_suffix(suffix: str): Sets suffix text

Example:
    >>> # Basic spin box
    >>> spinbox = StandardSpinBox(min_value=0, max_value=100, default_value=50)
    >>> spinbox.value_changed.connect(lambda v: print(f"Value: {v}"))
    >>> 
    >>> # With suffix
    >>> size_spin = StandardSpinBox(min_value=8, max_value=72, default_value=12, suffix=" pt")
"""

from PySide6.QtWidgets import QSpinBox
from PySide6.QtCore import Signal
from typing import Optional
from .constants import COMPONENT_SIZES


class StandardSpinBox(QSpinBox):
    """A spin box widget for numeric input with consistent styling"""

    # Re-expose signal for clarity
    value_changed = Signal(int)

    def __init__(
        self,
        min_value: int = 0,
        max_value: int = 100,
        default_value: int = 0,
        suffix: str = "",
        width: Optional[int] = None,
        parent: Optional[QSpinBox] = None
    ):
        super().__init__(parent)
        self._setup_spinbox(min_value, max_value, default_value, suffix, width)
        self._setup_styling()
        self._setup_signals()

    def _setup_spinbox(self, min_value: int, max_value: int, default_value: int, suffix: str, width: Optional[int]):
        """Configure spin box properties"""
        self.setMinimum(min_value)
        self.setMaximum(max_value)
        self.setValue(default_value)

        if suffix:
            self.setSuffix(suffix)

        # Set width
        if width:
            self.setFixedWidth(width)
        else:
            self.setFixedWidth(COMPONENT_SIZES["spinbox_standard_width"])

        self.setFixedHeight(COMPONENT_SIZES["spinbox_height"])

    def _setup_styling(self):
        """Apply consistent styling"""
        self.setStyleSheet("""
            QSpinBox {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 4px 8px;
                background-color: white;
                font-size: 10pt;
                color: #333333;
            }
            
            QSpinBox:focus {
                border-color: #0078d4;
                outline: none;
            }
            
            QSpinBox:disabled {
                background-color: #f0f0f0;
                color: #999999;
                border-color: #cccccc;
            }
            
            QSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 16px;
                border-left: 1px solid #cccccc;
                border-top-right-radius: 3px;
                background-color: #f8f8f8;
            }
            
            QSpinBox::up-button:hover {
                background-color: #e8e8e8;
            }
            
            QSpinBox::up-button:pressed {
                background-color: #d8d8d8;
            }
            
            QSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 16px;
                border-left: 1px solid #cccccc;
                border-bottom-right-radius: 3px;
                background-color: #f8f8f8;
            }
            
            QSpinBox::down-button:hover {
                background-color: #e8e8e8;
            }
            
            QSpinBox::down-button:pressed {
                background-color: #d8d8d8;
            }
        """)

    def _setup_signals(self):
        """Connect internal signals"""
        super().valueChanged.connect(self.value_changed.emit)

    # Public API
    def get_value(self) -> int:
        """Returns current value"""
        return self.value()

    def set_value(self, value: int):
        """Sets value

        Args:
            value: Value to set (within min/max range)
        """
        self.setValue(value)

    def set_range(self, min_value: int, max_value: int):
        """Sets value range

        Args:
            min_value: Minimum value
            max_value: Maximum value
        """
        self.setMinimum(min_value)
        self.setMaximum(max_value)

    def set_suffix(self, suffix: str):
        """Sets suffix text

        Args:
            suffix: Suffix text (e.g., " px", " %")
        """
        self.setSuffix(suffix)
