"""
StandardGroupBox - Consistent group box component

A group box widget for grouping related controls with consistent styling.

Parameters:
    title (str): Group box title (default: "")
    parent (Optional[QWidget]): Parent widget

Methods:
    set_title(title: str): Sets group box title
    get_title() -> str: Returns current title

Example:
    >>> group = StandardGroupBox("Advanced Options")
    >>> layout = QVBoxLayout()
    >>> layout.addWidget(StandardCheckBox("Option 1"))
    >>> layout.addWidget(StandardCheckBox("Option 2"))
    >>> group.setLayout(layout)
"""

from PySide6.QtWidgets import QGroupBox
from typing import Optional


class StandardGroupBox(QGroupBox):
    """A group box widget with consistent styling"""

    def __init__(
        self,
        title: str = "",
        parent: Optional[QGroupBox] = None
    ):
        super().__init__(title, parent)
        self._setup_styling()
        # Ensure the group box has a minimum height to display content
        self.setMinimumHeight(50)

    def _setup_styling(self):
        """Apply consistent styling"""
        self.setStyleSheet("""
            QGroupBox {
                font-size: 10pt;
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 4px;
                margin-top: 16px;
                padding-top: 20px;
                background-color: transparent;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px;
                color: #333333;
                background-color: #f0f0f0;
            }
            
            QGroupBox:disabled {
                border-color: #cccccc;
            }
            
            QGroupBox:disabled::title {
                color: #999999;
            }
        """)

    # Public API
    def set_title(self, title: str):
        """Sets group box title

        Args:
            title: Title text
        """
        self.setTitle(title)

    def get_title(self) -> str:
        """Returns current title"""
        return self.title()
