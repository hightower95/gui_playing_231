"""
StandardGroupBox - Consistent group box component

A group box widget for grouping related controls with consistent styling.
Optionally supports collapsible sections with blue gradient headers.

Parameters:
    title (str): Group box title (default: "")
    collapsible (bool): Whether the group box can be collapsed (default: False)
    parent (Optional[QWidget]): Parent widget

Methods:
    set_title(title: str): Sets group box title
    get_title() -> str: Returns current title
    set_collapsed(collapsed: bool): Collapse or expand the group (collapsible only)
    is_collapsed() -> bool: Check if group is collapsed (collapsible only)

Example:
    >>> # Standard group box
    >>> group = StandardGroupBox("Advanced Options")
    >>> layout = QVBoxLayout()
    >>> layout.addWidget(StandardCheckBox("Option 1"))
    >>> group.setLayout(layout)
    
    >>> # Collapsible group box
    >>> group = StandardGroupBox("Details", collapsible=True)
    >>> group.set_collapsed(True)  # Start collapsed
"""

from PySide6.QtWidgets import QGroupBox, QWidget, QVBoxLayout, QPushButton, QFrame
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor
from typing import Optional
from app.core.config import UI_COLORS


class StandardGroupBox(QGroupBox):
    """A group box widget with consistent styling and optional collapse functionality"""

    collapsed_changed = Signal(bool)  # Emitted when collapse state changes

    def __init__(
        self,
        title: str = "",
        collapsible: bool = False,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self._collapsible = collapsible
        self._collapsed = False
        self._content_widget = None
        self._header_button = None

        if collapsible:
            self._setup_collapsible(title)
        else:
            self.setTitle(title)
            self._setup_styling()
            self.setMinimumHeight(50)

    def _setup_collapsible(self, title: str):
        """Setup collapsible group box with custom header"""
        # Remove default title
        self.setTitle("")

        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create header button
        self._header_button = QPushButton()
        self._header_button.setFlat(True)
        self._header_button.setCursor(QCursor(Qt.PointingHandCursor))
        self._header_button.clicked.connect(self._toggle_collapsed)
        self._update_header_text(title)
        self._header_button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {UI_COLORS['section_highlight_primary']},
                    stop:1 {UI_COLORS['section_highlight_secondary']});
                color: white;
                border: none;
                border-radius: 3px 3px 0px 0px;
                padding: 4px 8px;
                text-align: left;
                font-weight: bold;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {UI_COLORS['section_highlight_secondary']},
                    stop:1 {UI_COLORS['section_highlight_primary']});
            }}
        """)

        # Create content widget
        self._content_widget = QWidget()
        self._content_widget.setStyleSheet("background-color: transparent;")

        # Add to main layout
        main_layout.addWidget(self._header_button)
        main_layout.addWidget(self._content_widget)

        # Style the group box itself
        self.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid {UI_COLORS['section_border']};
                border-radius: 3px;
                padding: 0px;
                background-color: transparent;
            }}
        """)

    def _setup_styling(self):
        """Apply consistent styling for non-collapsible group box"""
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
            }
            
            QGroupBox:disabled {
                border-color: #cccccc;
            }
            
            QGroupBox:disabled::title {
                color: #999999;
            }
        """)

    def _update_header_text(self, title: str):
        """Update header text with collapse indicator"""
        if not self._collapsible or not self._header_button:
            return
        arrow = "▶" if self._collapsed else "▼"
        self._header_button.setText(f"{arrow} {title}")

    def _toggle_collapsed(self):
        """Toggle the collapsed state"""
        self.set_collapsed(not self._collapsed)

    def setLayout(self, layout):
        """Override setLayout to put content in the right place"""
        if self._collapsible and self._content_widget:
            self._content_widget.setLayout(layout)
        else:
            super().setLayout(layout)

    # Public API
    def set_title(self, title: str):
        """Sets group box title

        Args:
            title: Title text
        """
        if self._collapsible:
            self._update_header_text(title)
        else:
            self.setTitle(title)

    def get_title(self) -> str:
        """Returns current title"""
        if self._collapsible and self._header_button:
            text = self._header_button.text()
            # Remove arrow indicator
            return text.replace("▼ ", "").replace("▶ ", "")
        return self.title()

    def set_collapsed(self, collapsed: bool):
        """Collapse or expand the group box (collapsible only)

        Args:
            collapsed: True to collapse, False to expand
        """
        if not self._collapsible or not self._content_widget:
            return

        self._collapsed = collapsed
        self._content_widget.setVisible(not collapsed)
        self._update_header_text(self.get_title())
        self.collapsed_changed.emit(collapsed)

    def is_collapsed(self) -> bool:
        """Check if group box is collapsed (collapsible only)

        Returns:
            True if collapsed, False otherwise
        """
        return self._collapsed if self._collapsible else False

    def is_collapsible(self) -> bool:
        """Check if this group box is collapsible

        Returns:
            True if collapsible, False otherwise
        """
        return self._collapsible
