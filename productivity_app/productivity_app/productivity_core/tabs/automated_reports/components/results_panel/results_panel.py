"""
Results Panel - Scrollable area displaying report tiles

Displays search/filter results as a grid of report tiles.
"""
from typing import Optional, List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PySide6.QtCore import Qt, Signal
from ...model import ReportMetadata
from .tile import ReportTile


class ResultsPanel(QWidget):
    """Scrollable results area with report tiles"""

    # Signals
    report_clicked = Signal(str)  # Emits report ID when tile clicked

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize results panel"""
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup results panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #1e1e1e;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #3a3a3a;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #4a4a4a;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

        # Container for tiles
        self.results_container = QWidget()
        self.results_container.setStyleSheet("background-color: transparent;")

        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setContentsMargins(25, 20, 25, 20)
        self.results_layout.setSpacing(15)
        self.results_layout.addStretch()

        self.scroll.setWidget(self.results_container)
        layout.addWidget(self.scroll)

    def update_results(self, reports: List[ReportMetadata]):
        """Update displayed reports

        Args:
            reports: List of report metadata to display
        """
        # Clear existing tiles
        while self.results_layout.count() > 1:  # Keep the stretch
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add new tiles
        for report in reports:
            tile = ReportTile(report)
            tile.clicked.connect(self.report_clicked.emit)
            self.results_layout.insertWidget(
                self.results_layout.count() - 1, tile)

    def clear_results(self):
        """Clear all displayed results"""
        self.update_results([])
