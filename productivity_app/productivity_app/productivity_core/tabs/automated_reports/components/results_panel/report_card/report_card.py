"""Report Card - Modular card for displaying report metadata"""
from typing import Optional, List
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget, QSizePolicy
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QResizeEvent, QCursor


from .header import CardHeader
from .report_summary import ReportSummary
from .tags_section import TagsSection
from .required_inputs import RequiredInputs
from .topic_groups import TopicGroups
from .styles import COMPLETE_CARD_STYLE


class ReportCard(QFrame):
    """Modular report card with separate section components"""

    def __init__(
        self,
        title: str,
        description: str,
        project: str,
        focus_area: str,
        required_inputs: List[str],
        topics: List[str],
        location: str = "Local",
        card_type: str = "Report",
        icon: Optional[str] = None,
        parent: Optional[QWidget] = None
    ):
        """Initialize report card

        Args:
            title: Report title
            description: Report description
            project: Project name
            focus_area: Focus area name
            required_inputs: List of required input names
            topics: List of associated topics
            location: Location indicator
            card_type: Type badge text
            icon: Optional icon (defaults based on card_type if not provided)
            parent: Parent widget
        """
        super().__init__(parent)

        self.title = title
        self.description = description
        self.project = project
        self.focus_area = focus_area
        self.required_inputs = required_inputs
        self.topics = topics
        self.location = location
        self.card_type = card_type
        self.icon = icon

        self._build_ui()
        self._apply_styles()

    def _build_ui(self):
        """Build card UI from modular components"""
        self.setObjectName("reportCard")
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header (icon + pill badge + optional location)
        header = CardHeader(
            card_type=self.card_type,
            location=self.location,
            icon=self.icon
        )
        header.setSizePolicy(QSizePolicy.Policy.Expanding,
                             QSizePolicy.Policy.Fixed)
        layout.addWidget(header)

        # Report summary (title + description)
        summary = ReportSummary(
            title=self.title,
            description=self.description
        )
        summary.setSizePolicy(QSizePolicy.Policy.Expanding,
                              QSizePolicy.Policy.Fixed)
        layout.addWidget(summary)

        # Divider after summary
        summary_divider = QFrame()
        summary_divider.setObjectName("cardDivider")
        summary_divider.setFrameShape(QFrame.Shape.HLine)
        summary_divider.setFixedHeight(1)
        layout.addWidget(summary_divider)

        # Tags (Project only) - "Report Aspects" section
        tags = TagsSection(tags={
            "Project": self.project
        })
        layout.addWidget(tags)

        # Divider before required inputs
        if self.required_inputs:
            inputs_divider = QFrame()
            inputs_divider.setObjectName("cardDivider")
            inputs_divider.setFrameShape(QFrame.Shape.HLine)
            inputs_divider.setFixedHeight(1)
            layout.addWidget(inputs_divider)

            # Required inputs
            inputs = RequiredInputs(inputs=self.required_inputs)
            layout.addWidget(inputs)

        # Topic groups at bottom (includes its own divider)
        if self.topics:
            topic_groups = TopicGroups(topics=self.topics)
            layout.addWidget(topic_groups)

        # Add stretch at bottom to push content to top
        layout.addStretch()

    def _apply_styles(self):
        """Apply stylesheet to card"""
        self.setStyleSheet(COMPLETE_CARD_STYLE)

    def sizeHint(self) -> QSize:
        """Provide size hint for layout"""
        return QSize(300, 300)

    def minimumSizeHint(self) -> QSize:
        """Provide minimum size hint"""
        return QSize(250, 300)

    def maximumHeight(self) -> int:
        """Set maximum height to prevent expansion"""
        return 300
