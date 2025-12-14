"""Card header component - icon, type badge, and location"""
from typing import Optional
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt


class CardHeader(QWidget):
    """Header section with icon, type badge, and optional location"""

    def __init__(
        self,
        card_type: str = "Report",
        location: Optional[str] = None,
        icon: Optional[str] = None,
        parent: Optional[QWidget] = None
    ):
        """Initialize card header

        Args:
            card_type: Report type (e.g., "Analysis", "Report", "Graph", "Assessment")
            location: Optional location indicator
            icon: Optional icon text/emoji (defaults based on card_type if not provided)
            parent: Parent widget
        """
        super().__init__(parent)
        self.card_type = card_type
        self.location = location
        self.icon = icon if icon else self._get_default_icon(card_type)
        self._build_ui()

    def _build_ui(self):
        """Build header UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Left group: icon + type badge
        left_group = QHBoxLayout()
        left_group.setSpacing(8)

        # Icon
        icon_label = QLabel(self.icon)
        icon_label.setObjectName("cardIcon")
        icon_label.setFixedSize(24, 24)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_group.addWidget(icon_label)

        # Type badge
        type_badge = QLabel(self.card_type)
        type_badge.setObjectName("badge_muted")
        left_group.addWidget(type_badge)
        left_group.addStretch()

        layout.addLayout(left_group)
        layout.addStretch()

        # Right group: location (optional)
        if self.location:
            right_group = QHBoxLayout()
            right_group.setSpacing(4)

            location_icon = QLabel("📍")
            location_icon.setObjectName("locationIcon")
            right_group.addWidget(location_icon)

            location_label = QLabel(self.location)
            location_label.setObjectName("locationText")
            right_group.addWidget(location_label)

            layout.addLayout(right_group)

    def _get_default_icon(self, card_type: str) -> str:
        """Get default icon for card type

        Args:
            card_type: Report type

        Returns:
            Icon text/emoji
        """
        icon_map = {
            "Analysis": "📄",
            "Graph": "📊",
            "Assessment": "⚠️",
            "Report": "📋",
            "Group": "📚",
        }
        return icon_map.get(card_type, "📋")
