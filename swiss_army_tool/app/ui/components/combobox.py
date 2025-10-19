"""
StandardComboBox Component

A standardized combo box with consistent sizing.

Parameters:
    size (ComboSize): Size variant
        - SINGLE: Standard width (200px × 30px)
        - DOUBLE: Double width (400px × 30px)
        - FULL: Full available width (auto × 30px)
    items (list, optional): List of items to populate
    parent (QWidget, optional): Parent widget

Example:
    >>> combo = StandardComboBox(size=ComboSize.SINGLE)
    >>> combo = StandardComboBox(size=ComboSize.DOUBLE, items=["v1.0", "v2.0"])
    >>> combo.addItems(["Option 1", "Option 2"])
    >>> selected = combo.currentText()
"""
from PySide6.QtWidgets import QComboBox, QWidget
from typing import Optional
from .enums import ComboSize
from .constants import COMPONENT_SIZES


class StandardComboBox(QComboBox):
    """Standardized combo box with consistent sizing"""

    def __init__(
        self,
        size: ComboSize = ComboSize.SINGLE,
        items: Optional[list] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.combo_size = size

        if items:
            self.addItems(items)

        self._apply_size()
        self._apply_style()

    def _apply_size(self):
        """Apply size constraints"""
        self.setFixedHeight(COMPONENT_SIZES["combo_height"])

        if self.combo_size == ComboSize.SINGLE:
            self.setFixedWidth(COMPONENT_SIZES["combo_single_width"])
        elif self.combo_size == ComboSize.DOUBLE:
            self.setFixedWidth(COMPONENT_SIZES["combo_double_width"])
        # FULL size: no width constraint, uses layout

    def _apply_style(self):
        """Apply consistent styling"""
        self.setStyleSheet("""
            QComboBox {
                padding: 4px 8px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                font-size: 10pt;
            }
            QComboBox:hover {
                border-color: #7E7E7E;
            }
            QComboBox:focus {
                border-color: #7E7E7E;
                border-width: 2px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #666;
                width: 0;
                height: 0;
                margin-right: 5px;
            }
        """)
