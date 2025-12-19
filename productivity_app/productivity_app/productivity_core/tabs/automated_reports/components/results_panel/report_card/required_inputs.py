"""Required inputs section - displays input requirements"""
from typing import Optional, List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt


class RequiredInputs(QWidget):
    """Section displaying required inputs as badges"""

    def __init__(
        self,
        inputs: List[str],
        parent: Optional[QWidget] = None
    ):
        """Initialize required inputs section

        Args:
            inputs: List of required input names
            parent: Parent widget
        """
        super().__init__(parent)
        self.inputs = inputs
        self._build_ui()

    def _build_ui(self):
        """Build required inputs UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        if self.inputs:
            # Badges container (no label, just badges)
            badges_container = QWidget()
            badges_container.setAttribute(
                Qt.WidgetAttribute.WA_TranslucentBackground)
            badges_layout = QHBoxLayout(badges_container)
            badges_layout.setContentsMargins(0, 0, 0, 0)
            badges_layout.setSpacing(8)

            for input_param in self.inputs:
                # Extract name from Parameter object or use as-is if string
                input_name = input_param.name if hasattr(input_param, 'name') else str(input_param)
                badge = self._create_badge(input_name)
                badges_layout.addWidget(badge)

            badges_layout.addStretch()
            layout.addWidget(badges_container)
        else:
            # Hide widget when no inputs to avoid spacing
            self.hide()

    def _create_badge(self, text: str) -> QLabel:
        """Create an input badge

        Args:
            text: Badge text

        Returns:
            QLabel configured as badge
        """
        badge = QLabel(text)
        badge.setObjectName("badge_orange")
        badge.setMaximumWidth(150)
        badge.setToolTip(text)  # Show full text on hover
        return badge
