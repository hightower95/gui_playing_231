"""Report Group Card - Display card for report groups

Presentation-only card showing report group metadata, reports, and tags.
"""
from typing import Optional, List
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap


class FlowLayout(QHBoxLayout):
    """Simple flow layout for wrapping badges"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setSpacing(8)
        self.setContentsMargins(0, 0, 0, 0)


class ReportGroupCard(QFrame):
    """Report group display card with metadata, reports, and tags"""
    
    def __init__(
        self,
        title: str,
        description: str,
        project: str,
        focus_area: str,
        reports: List[str],
        tags: List[str],
        location: str = "Local",
        parent: Optional[QWidget] = None
    ):
        """Initialize report group card
        
        Args:
            title: Primary title text
            description: Supporting descriptive text
            project: Project name
            focus_area: Focus area name
            reports: List of report names
            tags: List of category tags
            location: Location indicator (default: "Local")
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Store data
        self.title = title
        self.description = description
        self.project = project
        self.focus_area = focus_area
        self.reports = reports
        self.tags = tags
        self.location = location
        
        # Build UI
        self._build_ui()
        self._apply_styles()
    
    def _build_ui(self):
        """Build the card UI structure"""
        # Set card properties
        self.setObjectName("reportGroupCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # Header row
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        # Left group: icon + badge
        left_group = QHBoxLayout()
        left_group.setSpacing(8)
        
        # Icon placeholder (text fallback)
        icon_label = QLabel("📊")
        icon_label.setObjectName("cardIcon")
        icon_label.setFixedSize(24, 24)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_group.addWidget(icon_label)
        
        # Type badge
        type_badge = self._create_badge("Report Group", "highlight")
        left_group.addWidget(type_badge)
        left_group.addStretch()
        
        header_layout.addLayout(left_group)
        header_layout.addStretch()
        
        # Right group: location
        right_group = QHBoxLayout()
        right_group.setSpacing(4)
        
        location_icon = QLabel("📍")
        location_icon.setObjectName("locationIcon")
        right_group.addWidget(location_icon)
        
        location_label = QLabel(self.location)
        location_label.setObjectName("locationText")
        right_group.addWidget(location_label)
        
        header_layout.addLayout(right_group)
        main_layout.addLayout(header_layout)
        
        # Title section
        title_label = QLabel(self.title)
        title_label.setObjectName("cardTitle")
        title_label.setWordWrap(True)
        title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        main_layout.addWidget(title_label)
        
        # Description section
        desc_label = QLabel(self.description)
        desc_label.setObjectName("cardDescription")
        desc_label.setWordWrap(True)
        desc_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        main_layout.addWidget(desc_label)
        
        # Metadata rows container
        metadata_layout = QVBoxLayout()
        metadata_layout.setSpacing(8)
        
        # Project row
        project_row = self._create_metadata_row("Project", self.project)
        metadata_layout.addLayout(project_row)
        
        # Focus area row
        focus_row = self._create_metadata_row("Focus Area", self.focus_area)
        metadata_layout.addLayout(focus_row)
        
        main_layout.addLayout(metadata_layout)
        
        # Divider
        divider = QFrame()
        divider.setObjectName("cardDivider")
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFixedHeight(1)
        main_layout.addWidget(divider)
        
        # Reports section
        reports_label = QLabel(f"Contains {len(self.reports)} report{'s' if len(self.reports) != 1 else ''}")
        reports_label.setObjectName("sectionLabel")
        main_layout.addWidget(reports_label)
        
        # Reports badges container
        reports_container = QWidget()
        reports_layout = FlowLayout(reports_container)
        
        for report_name in self.reports:
            report_badge = self._create_badge(report_name, "highlight", max_width=200)
            reports_layout.addWidget(report_badge)
        
        reports_layout.addStretch()
        main_layout.addWidget(reports_container)
        
        # Tags section
        if self.tags:
            tags_container = QWidget()
            tags_layout = QHBoxLayout(tags_container)
            tags_layout.setContentsMargins(0, 0, 0, 0)
            tags_layout.setSpacing(6)
            
            for tag in self.tags:
                tag_badge = self._create_badge(tag, "secondaryHighlight", small=True)
                tags_layout.addWidget(tag_badge)
            
            tags_layout.addStretch()
            main_layout.addWidget(tags_container)
    
    def _create_metadata_row(self, label: str, value: str) -> QHBoxLayout:
        """Create a metadata key/value row
        
        Args:
            label: Left-side label text
            value: Right-side value text
            
        Returns:
            QHBoxLayout with label and value badge
        """
        row = QHBoxLayout()
        row.setSpacing(12)
        
        # Label (fixed width for alignment)
        key_label = QLabel(label)
        key_label.setObjectName("metadataLabel")
        key_label.setFixedWidth(80)
        row.addWidget(key_label)
        
        # Value badge
        value_badge = self._create_badge(value, "highlight")
        row.addWidget(value_badge)
        row.addStretch()
        
        return row
    
    def _create_badge(
        self, 
        text: str, 
        role: str = "highlight",
        small: bool = False,
        max_width: Optional[int] = None
    ) -> QLabel:
        """Create a rounded badge label
        
        Args:
            text: Badge text
            role: Semantic role (highlight, secondaryHighlight)
            small: Whether to use smaller font
            max_width: Optional maximum width (enables ellipsis)
            
        Returns:
            QLabel configured as a badge
        """
        badge = QLabel(text)
        badge.setObjectName(f"badge_{role}")
        
        if small:
            badge.setProperty("badgeSize", "small")
        
        if max_width:
            badge.setMaximumWidth(max_width)
            # Enable ellipsis for overflow
            badge.setTextFormat(Qt.TextFormat.PlainText)
            from PySide6.QtGui import QFontMetrics
            metrics = QFontMetrics(badge.font())
            elided = metrics.elidedText(text, Qt.TextElideMode.ElideRight, max_width - 16)
            badge.setText(elided)
            badge.setToolTip(text)  # Show full text on hover
        
        return badge
    
    def _apply_styles(self):
        """Apply semantic styling to the card"""
        self.setStyleSheet("""
            /* Card container - surface with accent border */
            QFrame#reportGroupCard {
                background-color: #2a2a2a;  /* surface */
                border: 1px solid #4fc3f7;  /* accent */
                border-radius: 12px;
            }
            
            /* Icon styling */
            QLabel#cardIcon {
                font-size: 16pt;
                background: transparent;
                border: none;
            }
            
            /* Title - primary text */
            QLabel#cardTitle {
                color: #E0E0E0;  /* primaryText */
                font-size: 14pt;
                font-weight: 600;
                background: transparent;
                border: none;
            }
            
            /* Description - muted text */
            QLabel#cardDescription {
                color: #909090;  /* mutedText */
                font-size: 10pt;
                background: transparent;
                border: none;
            }
            
            /* Metadata label */
            QLabel#metadataLabel {
                color: #909090;  /* mutedText */
                font-size: 9pt;
                background: transparent;
                border: none;
            }
            
            /* Divider */
            QFrame#cardDivider {
                background-color: #3a3a3a;  /* muted */
                border: none;
            }
            
            /* Section label */
            QLabel#sectionLabel {
                color: #B0B0B0;
                font-size: 9pt;
                background: transparent;
                border: none;
            }
            
            /* Location text */
            QLabel#locationText, QLabel#locationIcon {
                color: #909090;  /* mutedText */
                font-size: 9pt;
                background: transparent;
                border: none;
            }
            
            /* Highlight badge - primary */
            QLabel[objectName^="badge_highlight"] {
                background-color: rgba(79, 195, 247, 0.15);  /* highlight */
                color: #90caf9;
                border-radius: 8px;
                padding: 4px 12px;
                font-size: 9pt;
                border: none;
            }
            
            /* Secondary highlight badge */
            QLabel[objectName^="badge_secondaryHighlight"] {
                background-color: rgba(79, 195, 247, 0.08);  /* secondaryHighlight */
                color: #7fb3d5;
                border-radius: 6px;
                padding: 2px 8px;
                font-size: 8pt;
                border: none;
            }
            
            /* Small badge variant */
            QLabel[badgeSize="small"] {
                font-size: 8pt;
                padding: 2px 8px;
            }
        """)
    
    def sizeHint(self) -> QSize:
        """Provide size hint for layout calculations"""
        # Card should have a reasonable minimum width
        return QSize(300, 200)
    
    def minimumSizeHint(self) -> QSize:
        """Provide minimum size hint"""
        return QSize(250, 150)
