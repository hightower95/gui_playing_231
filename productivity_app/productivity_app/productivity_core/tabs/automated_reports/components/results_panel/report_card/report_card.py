"""Report Card - Modular card for displaying report metadata"""
from typing import Optional, List
from PySide6.QtWidgets import QFrame, QVBoxLayout, QWidget
from PySide6.QtCore import QSize
from PySide6.QtGui import QResizeEvent


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
        icon: str = "📊",
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
            icon: Icon emoji
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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        header = CardHeader(
            card_type=self.card_type,
            location=self.location,
            icon=self.icon
        )
        layout.addWidget(header)

        # Report summary
        summary = ReportSummary(
            title=self.title,
            description=self.description
        )
        layout.addWidget(summary)

        # Tags (Project, Focus Area)
        tags = TagsSection(tags={
            "Project": self.project,
            "Focus Area": self.focus_area
        })
        layout.addWidget(tags)

        # Divider
        divider = QFrame()
        divider.setObjectName("cardDivider")
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFixedHeight(1)
        layout.addWidget(divider)

        # Required inputs
        if self.required_inputs:
            inputs = RequiredInputs(inputs=self.required_inputs)
            layout.addWidget(inputs)

        # Topic groups
        if self.topics:
            topic_groups = TopicGroups(topics=self.topics)
            layout.addWidget(topic_groups)

    def _apply_styles(self):
        """Apply stylesheet to card"""
        self.setStyleSheet(COMPLETE_CARD_STYLE)

    def sizeHint(self) -> QSize:
        """Provide size hint for layout"""
        return QSize(300, 250)

    def minimumSizeHint(self) -> QSize:
        """Provide minimum size hint"""
        return QSize(250, 200)
