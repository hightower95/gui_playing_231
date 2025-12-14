"""Card header component - icon, type badge, and location"""
from typing import Optional
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt


class CardHeader(QWidget):
    """Header section with icon, type badge, and location"""
    
    def __init__(
        self,
        card_type: str = "Report",
        location: str = "Local",
        icon: str = "📊",
        parent: Optional[QWidget] = None
    ):
        """Initialize card header
        
        Args:
            card_type: Type label (e.g., "Report", "Report Group")
            location: Location indicator
            icon: Icon emoji or text
            parent: Parent widget
        """
        super().__init__(parent)
        self.card_type = card_type
        self.location = location
        self.icon = icon
        self._build_ui()
    
    def _build_ui(self):
        """Build header UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Left group: icon + badge
        left_group = QHBoxLayout()
        left_group.setSpacing(8)
        
        # Icon
        icon_label = QLabel(self.icon)
        icon_label.setObjectName("cardIcon")
        icon_label.setFixedSize(24, 24)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_group.addWidget(icon_label)
        
        # Type badge
        type_badge = self._create_badge(self.card_type, "highlight")
        left_group.addWidget(type_badge)
        left_group.addStretch()
        
        layout.addLayout(left_group)
        layout.addStretch()
        
        # Right group: location
        right_group = QHBoxLayout()
        right_group.setSpacing(4)
        
        location_icon = QLabel("📍")
        location_icon.setObjectName("locationIcon")
        right_group.addWidget(location_icon)
        
        location_label = QLabel(self.location)
        location_label.setObjectName("locationText")
        right_group.addWidget(location_label)
        
        layout.addLayout(right_group)
    
    def _create_badge(self, text: str, role: str = "highlight") -> QLabel:
        """Create a badge label
        
        Args:
            text: Badge text
            role: Semantic role
            
        Returns:
            QLabel configured as badge
        """
        badge = QLabel(text)
        badge.setObjectName(f"badge_{role}")
        return badge
