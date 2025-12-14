"""Required inputs section - displays input requirements"""
from typing import Optional, List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel


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
        
        # Section label
        if self.inputs:
            label = QLabel(f"Requires {len(self.inputs)} input{'s' if len(self.inputs) != 1 else ''}")
            label.setObjectName("sectionLabel")
            layout.addWidget(label)
            
            # Badges container
            badges_container = QWidget()
            badges_layout = QHBoxLayout(badges_container)
            badges_layout.setContentsMargins(0, 0, 0, 0)
            badges_layout.setSpacing(8)
            
            for input_name in self.inputs:
                badge = self._create_badge(input_name)
                badges_layout.addWidget(badge)
            
            badges_layout.addStretch()
            layout.addWidget(badges_container)
    
    def _create_badge(self, text: str) -> QLabel:
        """Create an input badge
        
        Args:
            text: Badge text
            
        Returns:
            QLabel configured as badge
        """
        badge = QLabel(text)
        badge.setObjectName("badge_highlight")
        badge.setMaximumWidth(150)
        return badge
