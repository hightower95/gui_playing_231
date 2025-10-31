"""
StandardButton Component

A standardized button with consistent sizing and role-based coloring.

Parameters:
    text (str): Button text
    role (ButtonRole): Button role determining color scheme
        - PRIMARY: Blue (#0078d4) - Main actions
        - SECONDARY: Gray (#6c757d) - Cancel, Close
        - SUCCESS: Green (#28a745) - Positive actions
        - DANGER: Red (#dc3545) - Destructive actions
        - WARNING: Orange (#ffc107) - Warning actions
        - INFO: Light blue (#17a2b8) - Informational
    size (ButtonSize): Size variant
        - FULL: Auto width × 36px height
        - HALF_WIDTH: 150px × 36px
        - HALF_HEIGHT: Auto × 24px
        - COMPACT: 100px × 24px
    icon (str, optional): Icon text (emoji or unicode)
    parent (QWidget, optional): Parent widget

Example:
    >>> btn = StandardButton("Save", role=ButtonRole.PRIMARY)
    >>> btn = StandardButton("Delete", role=ButtonRole.DANGER, size=ButtonSize.HALF_WIDTH)
    >>> btn = StandardButton("🔍 Search", role=ButtonRole.PRIMARY)
"""
from PySide6.QtWidgets import QPushButton, QWidget
from typing import Optional
from .enums import ButtonRole, ButtonSize
from .constants import COMPONENT_SIZES, BUTTON_COLORS


class StandardButton(QPushButton):
    """Standardized button with consistent sizing and role-based coloring"""

    def __init__(
        self,
        text: str,
        role: ButtonRole = ButtonRole.PRIMARY,
        size: ButtonSize = ButtonSize.FULL,
        icon: Optional[str] = None,
        parent: Optional[QWidget] = None
    ):
        full_text = f"{icon} {text}" if icon else text
        super().__init__(full_text, parent)

        self.role = role
        self.size = size

        self._apply_size()
        self._apply_style()

    def _apply_size(self):
        """Apply size constraints based on size variant"""
        if self.size == ButtonSize.HALF_WIDTH:
            self.setFixedWidth(COMPONENT_SIZES["button_half_width"])
            self.setFixedHeight(COMPONENT_SIZES["button_full_height"])
        elif self.size == ButtonSize.HALF_HEIGHT:
            self.setFixedHeight(COMPONENT_SIZES["button_half_height"])
        elif self.size == ButtonSize.COMPACT:
            self.setFixedWidth(COMPONENT_SIZES["button_compact_width"])
            self.setFixedHeight(COMPONENT_SIZES["button_compact_height"])
        else:  # FULL
            self.setMinimumHeight(COMPONENT_SIZES["button_full_height"])

    def _apply_style(self):
        """Apply color scheme based on role"""
        colors = BUTTON_COLORS[self.role]

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['background']};
                color: {colors['text']};
                padding: 6px 16px;
                padding-left: 15px;
                font-size: 11pt;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {colors['hover']};
            }}
            QPushButton:pressed {{
                background-color: {colors['pressed']};
            }}
            QPushButton:disabled {{
                background-color: {colors['disabled']};
                color: {colors['text_disabled']};
            }}
        """)
