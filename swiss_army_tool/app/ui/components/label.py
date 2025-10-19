"""
StandardLabel Component

A standardized text label with consistent styling.

Parameters:
    text (str): Label text
    style (TextStyle): Text style variant
        - TITLE: 14pt bold, black - Page titles
        - SECTION: 12pt bold, black - Section headers
        - SUBSECTION: 11pt bold, dark gray - Subsection headers
        - LABEL: 10pt normal, black - Standard labels
        - NOTES: 9pt italic, light gray - Helper text
        - STATUS: 10pt normal, gray - Status messages
    color (str, optional): Custom color override (hex or name)
    parent (QWidget, optional): Parent widget

Methods:
    set_color(color: str): Update label color dynamically

Example:
    >>> title = StandardLabel("Document Scanner", style=TextStyle.TITLE)
    >>> section = StandardLabel("Configuration", style=TextStyle.SECTION)
    >>> notes = StandardLabel("This is optional", style=TextStyle.NOTES)
    >>> status = StandardLabel("Ready", style=TextStyle.STATUS)
    >>> status.set_color("green")  # Change color dynamically
"""
from PySide6.QtWidgets import QLabel, QWidget
from typing import Optional
from .enums import TextStyle


class StandardLabel(QLabel):
    """Standardized text label with consistent styling"""

    STYLE_CONFIG = {
        TextStyle.TITLE: {
            "font_size": "14pt",
            "font_weight": "bold",
            "color": "#E0E0E0",
        },
        TextStyle.SECTION: {
            "font_size": "12pt",
            "font_weight": "bold",
            "color": "#E0E0E0",
        },
        TextStyle.SUBSECTION: {
            "font_size": "11pt",
            "font_weight": "bold",
            "color": "#E0E0E0",
        },
        TextStyle.LABEL: {
            "font_size": "10pt",
            "font_weight": "normal",
            "color": "#E0E0E0",
        },
        TextStyle.NOTES: {
            "font_size": "9pt",
            "font_weight": "normal",
            "color": "#888888",
            "font_style": "italic",
        },
        TextStyle.STATUS: {
            "font_size": "10pt",
            "font_weight": "normal",
            "color": "#666666",
        },
    }

    def __init__(
        self,
        text: str,
        style: TextStyle = TextStyle.LABEL,
        color: Optional[str] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(text, parent)
        self.text_style = style
        self._apply_style(color)

    def _apply_style(self, custom_color: Optional[str] = None):
        """Apply text styling"""
        config = self.STYLE_CONFIG[self.text_style]

        color = custom_color if custom_color else config["color"]
        font_style = config.get("font_style", "normal")

        style_parts = [
            f"font-size: {config['font_size']};",
            f"font-weight: {config['font_weight']};",
            f"color: {color};",
        ]

        if font_style != "normal":
            style_parts.append(f"font-style: {font_style};")

        self.setStyleSheet(" ".join(style_parts))

    def set_color(self, color: str):
        """Update label color dynamically

        Args:
            color: Color string (hex or name)

        Example:
            >>> label.set_color("green")
            >>> label.set_color("#ff0000")
        """
        self._apply_style(color)
