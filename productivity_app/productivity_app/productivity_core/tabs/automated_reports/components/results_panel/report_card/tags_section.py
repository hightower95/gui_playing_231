"""Tags section component - project, focus area, etc."""
from typing import Optional, List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel


class TagsSection(QWidget):
    """Tags section displaying key-value metadata"""
    
    def __init__(
        self,
        tags: dict,
        parent: Optional[QWidget] = None
    ):
        """Initialize tags section
        
        Args:
            tags: Dictionary of key-value pairs (e.g., {'Project': 'Alpha', 'Focus Area': 'Team'})
            parent: Parent widget
        """
        super().__init__(parent)
        self.tags = tags
        self._build_ui()
    
    def _build_ui(self):
        """Build tags UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        for key, value in self.tags.items():
            row = self._create_tag_row(key, value)
            layout.addLayout(row)
    
    def _create_tag_row(self, label: str, value: str) -> QHBoxLayout:
        """Create a tag key-value row
        
        Args:
            label: Tag label
            value: Tag value
            
        Returns:
            QHBoxLayout with label and value
        """
        row = QHBoxLayout()
        row.setSpacing(12)
        
        # Label
        key_label = QLabel(label)
        key_label.setObjectName("metadataLabel")
        key_label.setFixedWidth(80)
        row.addWidget(key_label)
        
        # Value badge
        value_badge = QLabel(value)
        value_badge.setObjectName("badge_highlight")
        row.addWidget(value_badge)
        row.addStretch()
        
        return row
