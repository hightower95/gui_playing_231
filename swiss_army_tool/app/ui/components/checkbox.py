"""
StandardCheckBox - Consistent checkbox component

A checkbox widget with consistent styling and behavior.

Parameters:
    text (str): Checkbox label text
    checked (bool): Initial checked state (default: False)
    tristate (bool): Enable three-state checkbox (default: False)
    parent (Optional[QWidget]): Parent widget

Signals:
    state_changed(int): Emitted when checkbox state changes
        Qt.Unchecked (0), Qt.PartiallyChecked (1), Qt.Checked (2)
    toggled(bool): Emitted when checkbox is toggled (True=checked, False=unchecked)

Methods:
    is_checked() -> bool: Returns True if checked
    set_checked(checked: bool): Sets checkbox state
    set_tristate(enable: bool): Enable/disable tristate
    get_state() -> Qt.CheckState: Returns current check state
    set_state(state: Qt.CheckState): Sets check state

Example:
    >>> checkbox = StandardCheckBox("Enable feature")
    >>> checkbox.state_changed.connect(lambda state: print(f"State: {state}"))
    >>> checkbox.set_checked(True)
    >>> if checkbox.is_checked():
    ...     print("Feature enabled")
"""

from PySide6.QtWidgets import QCheckBox
from PySide6.QtCore import Signal, Qt
from typing import Optional


class StandardCheckBox(QCheckBox):
    """A checkbox widget with consistent styling and behavior"""

    # Re-expose signals for clarity
    state_changed = Signal(int)
    toggled = Signal(bool)

    def __init__(
        self,
        text: str = "",
        checked: bool = False,
        tristate: bool = False,
        parent: Optional[QCheckBox] = None
    ):
        super().__init__(text, parent)
        self._setup_checkbox(checked, tristate)
        self._setup_styling()
        self._setup_signals()

    def _setup_checkbox(self, checked: bool, tristate: bool):
        """Configure checkbox properties"""
        self.setTristate(tristate)
        self.setChecked(checked)

    def _setup_styling(self):
        """Apply consistent styling"""
        self.setStyleSheet("""
            QCheckBox {
                font-size: 10pt;
                spacing: 6px;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #999999;
                border-radius: 3px;
                background-color: white;
            }
            
            QCheckBox::indicator:hover {
                border-color: #0078d4;
                background-color: #f0f0f0;
            }
            
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border-color: #0078d4;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTAgMkw0IDhMMiA2IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPjwvc3ZnPg==);
            }
            
            QCheckBox::indicator:indeterminate {
                background-color: #0078d4;
                border-color: #0078d4;
            }
            
            QCheckBox::indicator:disabled {
                background-color: #f0f0f0;
                border-color: #cccccc;
            }
            
            QCheckBox:disabled {
                color: #999999;
            }
        """)

    def _setup_signals(self):
        """Connect internal signals"""
        super().stateChanged.connect(self.state_changed.emit)
        super().toggled.connect(self.toggled.emit)

    # Public API
    def is_checked(self) -> bool:
        """Returns True if checkbox is checked"""
        return self.checkState() == Qt.Checked

    def set_checked(self, checked: bool):
        """Sets checkbox checked state

        Args:
            checked: True to check, False to uncheck
        """
        self.setChecked(checked)

    def set_tristate(self, enable: bool):
        """Enable or disable tristate mode

        Args:
            enable: True to enable tristate, False to disable
        """
        self.setTristate(enable)

    def get_state(self) -> Qt.CheckState:
        """Returns current check state

        Returns:
            Qt.CheckState: Unchecked, PartiallyChecked, or Checked
        """
        return self.checkState()

    def set_state(self, state: Qt.CheckState):
        """Sets check state

        Args:
            state: Qt.Unchecked, Qt.PartiallyChecked, or Qt.Checked
        """
        self.setCheckState(state)
