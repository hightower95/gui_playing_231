"""
Report Tile - Individual report display card

Displays a single report with metadata, tags, and hover effects.
"""
from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, Signal
from ...model import ReportMetadata


class ReportTile(QFrame):
    """Tile widget for displaying a single report"""

    # Signals
    clicked = Signal(str)  # Emits report ID when clicked

    def __init__(self, report: ReportMetadata, parent: Optional[QWidget] = None):
        """Initialize report tile

        Args:
            report: Report metadata to display
            parent: Parent widget
        """
        super().__init__(parent)
        self.report = report
        self._setup_ui()

    def _setup_ui(self):
        """Setup tile UI"""
        self.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 12px;
                padding: 15px;
            }
            QFrame:hover {
                background-color: #353535;
                border: 1px solid #4a4a4a;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(120)
        self.setMaximumHeight(160)

        # Enable mouse tracking and set focus policy
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Header row with icon and scope badge
        header_layout = QHBoxLayout()

        # Report type icon
        icon = "📄" if self.report.report_type == "single" else "📚"
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(
            "font-size: 16pt; background: transparent; border: none;")
        icon_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        header_layout.addWidget(icon_label)

        # Title
        title = QLabel(self.report.name)
        title.setStyleSheet("""
            font-size: 12pt;
            font-weight: bold;
            color: #ffffff;
            background: transparent;
            border: none;
        """)
        title.setWordWrap(True)
        title.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        header_layout.addWidget(title, stretch=1)

        # Scope badge
        scope_badge = QLabel(f"📍 {self.report.scope.title()}")
        scope_badge.setStyleSheet("""
            font-size: 8pt;
            color: #b0b0b0;
            background: transparent;
            border: none;
        """)
        scope_badge.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        header_layout.addWidget(scope_badge)

        layout.addLayout(header_layout)

        # Description
        desc = QLabel(self.report.description)
        desc.setStyleSheet("""
            font-size: 9pt;
            color: #b0b0b0;
            background: transparent;
            border: none;
        """)
        desc.setWordWrap(True)
        desc.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout.addWidget(desc)

        # Metadata row
        meta_layout = QHBoxLayout()

        # Project
        project_label = QLabel(f"Project: {self.report.project}")
        project_label.setStyleSheet(
            "font-size: 8pt; color: #4fc3f7; background: transparent; border: none;")
        project_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        meta_layout.addWidget(project_label)

        # Focus Area
        focus_label = QLabel(f"Focus Area: {self.report.focus_area}")
        focus_label.setStyleSheet(
            "font-size: 8pt; color: #4fc3f7; background: transparent; border: none;")
        focus_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        meta_layout.addWidget(focus_label)

        meta_layout.addStretch()
        layout.addLayout(meta_layout)

        # Tags or contained reports
        if self.report.report_type == "group" and self.report.contained_reports:
            tags_layout = QHBoxLayout()
            tags_label = QLabel(
                f"Contains {len(self.report.contained_reports)} reports:")
            tags_label.setAttribute(
                Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            tags_layout.addWidget(tags_label)

            for contained in self.report.contained_reports[:3]:  # Show first 3
                tag = QLabel(contained)
                tag.setStyleSheet("""
                    font-size: 8pt;
                    color: #ffffff;
                    background-color: rgba(79, 195, 247, 0.2);
                    border: 1px solid rgba(79, 195, 247, 0.3);
                    border-radius: 3px;
                    padding: 2px 6px;
                """)
                tag.setAttribute(
                    Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                tags_layout.addWidget(tag)

            tags_layout.addStretch()
            layout.addLayout(tags_layout)
        elif self.report.tags:
            tags_layout = QHBoxLayout()
            for tag in self.report.tags[:3]:  # Show first 3 tags
                tag_label = QLabel(tag)
                tag_label.setStyleSheet("""
                    font-size: 8pt;
                    color: #90caf9;
                    background-color: rgba(100, 181, 246, 0.15);
                    border-radius: 3px;
                    padding: 2px 6px;
                    background: transparent;
                    border: none;
                """)
                tag_label.setAttribute(
                    Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                tags_layout.addWidget(tag_label)

            tags_layout.addStretch()
            layout.addLayout(tags_layout)

        layout.addStretch()

    def mousePressEvent(self, event):
        """Handle mouse click on tile"""
        if event.button() == Qt.MouseButton.LeftButton:
            print(
                f"[ReportTile] Mouse pressed on tile: {self.report.id} - {self.report.name}")
            self.clicked.emit(self.report.id)
        super().mousePressEvent(event)
