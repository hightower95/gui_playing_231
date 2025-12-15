"""Topic groups section - displays associated topic groups"""
from typing import Optional, List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt


class TopicGroups(QWidget):
    """Section displaying topic group associations"""

    def __init__(
        self,
        topics: List[str],
        parent: Optional[QWidget] = None
    ):
        """Initialize topic groups section

        Args:
            topics: List of topic names
            parent: Parent widget
        """
        super().__init__(parent)
        self.topics = topics
        self._build_ui()

    def _build_ui(self):
        """Build topic groups UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        if self.topics:
            # Divider instead of text label
            divider = QFrame()
            divider.setObjectName("cardDivider")
            divider.setFrameShape(QFrame.Shape.HLine)
            divider.setFixedHeight(1)
            layout.addWidget(divider)

            # Topic badges container - use flow layout for wrapping
            badges_container = QWidget()
            badges_container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            badges_layout = QHBoxLayout(badges_container)
            badges_layout.setContentsMargins(0, 0, 0, 0)
            badges_layout.setSpacing(4)  # Tighter spacing for compact look

            for topic in self.topics:
                badge = self._create_badge(topic)
                badges_layout.addWidget(badge)

            badges_layout.addStretch()
            layout.addWidget(badges_container)
        else:
            # When no topics, hide this widget completely to avoid spacing
            self.hide()

    def _create_badge(self, text: str) -> QLabel:
        """Create a topic badge

        Args:
            text: Badge text

        Returns:
            QLabel configured as badge
        """
        badge = QLabel(text)
        badge.setObjectName("badge_green")
        badge.setProperty("badgeSize", "small")
        return badge
