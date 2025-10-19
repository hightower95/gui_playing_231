"""
StandardRadioButton - Consistent radio button component

A radio button widget with consistent styling and helper for groups.

Parameters:
    text (str): Radio button label text
    checked (bool): Initial checked state (default: False)
    parent (Optional[QWidget]): Parent widget

Signals:
    toggled(bool): Emitted when radio button is toggled

Methods:
    is_checked() -> bool: Returns True if checked
    set_checked(checked: bool): Sets radio button state

Helper Functions:
    create_radio_group(*buttons, default_index=0) -> QButtonGroup:
        Creates a button group from multiple radio buttons

Example:
    >>> radio1 = StandardRadioButton("Option 1", checked=True)
    >>> radio2 = StandardRadioButton("Option 2")
    >>> radio3 = StandardRadioButton("Option 3")
    >>> 
    >>> # Create group
    >>> group = create_radio_group(radio1, radio2, radio3, default_index=0)
    >>> 
    >>> # Connect signals
    >>> radio1.toggled.connect(lambda checked: print(f"Option 1: {checked}"))
"""

from PySide6.QtWidgets import QRadioButton, QButtonGroup
from PySide6.QtCore import Signal
from typing import Optional


class StandardRadioButton(QRadioButton):
    """A radio button widget with consistent styling"""

    # Re-expose signal for clarity
    toggled = Signal(bool)

    def __init__(
        self,
        text: str = "",
        checked: bool = False,
        parent: Optional[QRadioButton] = None
    ):
        super().__init__(text, parent)
        self._setup_radio_button(checked)
        self._setup_styling()
        self._setup_signals()

    def _setup_radio_button(self, checked: bool):
        """Configure radio button properties"""
        self.setChecked(checked)

    def _setup_styling(self):
        """Apply consistent styling"""
        self.setStyleSheet("""
            QRadioButton {
                font-size: 10pt;
                spacing: 6px;
            }
            
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #999999;
                border-radius: 8px;
                background-color: white;
            }
            
            QRadioButton::indicator:hover {
                border-color: #0078d4;
                background-color: #f0f0f0;
            }
            
            QRadioButton::indicator:checked {
                border-color: #0078d4;
                background-color: white;
            }
            
            QRadioButton::indicator:checked::after {
                width: 8px;
                height: 8px;
                border-radius: 4px;
                background-color: #0078d4;
            }
            
            QRadioButton::indicator:disabled {
                background-color: #f0f0f0;
                border-color: #cccccc;
            }
            
            QRadioButton:disabled {
                color: #999999;
            }
        """)

    def _setup_signals(self):
        """Connect internal signals"""
        super().toggled.connect(self.toggled.emit)

    # Public API
    def is_checked(self) -> bool:
        """Returns True if radio button is checked"""
        return self.isChecked()

    def set_checked(self, checked: bool):
        """Sets radio button checked state

        Args:
            checked: True to check, False to uncheck
        """
        self.setChecked(checked)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_radio_group(*buttons: StandardRadioButton, default_index: int = 0) -> QButtonGroup:
    """Creates a button group from radio buttons

    Args:
        *buttons: Radio button instances to group
        default_index: Index of button to check by default (default: 0)

    Returns:
        QButtonGroup: Button group containing the radio buttons

    Example:
        >>> radio1 = StandardRadioButton("Option 1")
        >>> radio2 = StandardRadioButton("Option 2")
        >>> group = create_radio_group(radio1, radio2, default_index=0)
    """
    group = QButtonGroup()
    group.setExclusive(True)

    for i, button in enumerate(buttons):
        group.addButton(button, i)
        if i == default_index:
            button.set_checked(True)

    return group
