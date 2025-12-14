"""Topic groups section - displays associated topic groups"""
from typing import Optional, List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel


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
            # Section label
            label = QLabel(f"In {len(self.topics)} topic{'s' if len(self.topics) != 1 else ''}")
            label.setObjectName("sectionLabel")
            layout.addWidget(label)
            
            # Topic badges container
            badges_container = QWidget()
            badges_layout = QHBoxLayout(badges_container)
            badges_layout.setContentsMargins(0, 0, 0, 0)
            badges_layout.setSpacing(6)
            
            for topic in self.topics:
                badge = self._create_badge(topic)
                badges_layout.addWidget(badge)
            
            badges_layout.addStretch()
            layout.addWidget(badges_container)
    
    def _create_badge(self, text: str) -> QLabel:
        """Create a topic badge
        
        Args:
            text: Badge text
            
        Returns:
            QLabel configured as badge
        """
        badge = QLabel(text)
        badge.setObjectName("badge_secondaryHighlight")
        badge.setProperty("badgeSize", "small")
        return badge
