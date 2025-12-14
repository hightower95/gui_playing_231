"""
Results Panel - Scrollable area displaying report tiles

Displays search/filter results as a grid of report tiles or cards.
"""
from typing import Optional, List, Dict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal
from ...model import ReportMetadata
from .tile import ReportTile
from .report_card import ReportCard


class ResultsGrid(QWidget):
    """Grid container for cards with responsive layout"""

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize results grid"""
        super().__init__(parent)
        self.cards: List[QWidget] = []
        self.cards_per_row = 4  # Default 4 cards per row
        self.card_spacing = 16
        self._setup_ui()

    def _setup_ui(self):
        """Setup grid UI"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(self.card_spacing)

        # Row container
        self.current_row: Optional[QHBoxLayout] = None
        self.cards_in_current_row = 0

    def add_card(self, card: QWidget):
        """Add a card to the grid

        Args:
            card: Widget to add
        """
        # Start new row if needed
        if self.current_row is None or self.cards_in_current_row >= self.cards_per_row:
            self._start_new_row()

        # Add card to current row
        self.current_row.addWidget(card)
        self.cards.append(card)
        self.cards_in_current_row += 1

    def _start_new_row(self):
        """Start a new row in the grid"""
        # Create row container
        row_widget = QWidget()
        self.current_row = QHBoxLayout(row_widget)
        self.current_row.setContentsMargins(0, 0, 0, 0)
        self.current_row.setSpacing(self.card_spacing)

        # Add to main layout
        self.main_layout.addWidget(row_widget)
        self.cards_in_current_row = 0

    def clear_cards(self):
        """Remove all cards from the grid"""
        # Clear all widgets
        while self.main_layout.count() > 0:
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.cards.clear()
        self.current_row = None
        self.cards_in_current_row = 0

    def set_cards_per_row(self, count: int):
        """Set number of cards per row and rebuild layout

        Args:
            count: Number of cards per row
        """
        if count != self.cards_per_row:
            self.cards_per_row = count
            self._rebuild_layout()

    def _rebuild_layout(self):
        """Rebuild the grid layout with current cards"""
        # Save current cards
        saved_cards = self.cards.copy()

        # Clear layout
        self.clear_cards()

        # Re-add cards with new layout
        for card in saved_cards:
            self.add_card(card)


class ResultsPanel(QWidget):
    """Scrollable results area with report tiles or cards"""

    # Signals
    report_clicked = Signal(str)  # Emits report ID when tile clicked
    card_clicked = Signal(object)  # Emits card data (future)

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize results panel"""
        super().__init__(parent)
        self.use_grid_layout = False  # Toggle between list and grid
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
        self.scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1e1e1e;
            }
            QScrollBar:vertical {
                border: none;
                background: #1e1e1e;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #3a3a3a;
                min-height: 30px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #4a4a4a;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        # Scroll content container
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        scroll_layout.setSpacing(0)

        # Grid for cards
        self.grid = ResultsGrid()
        scroll_layout.addWidget(self.grid)
        scroll_layout.addStretch()

        self.scroll.setWidget(scroll_content)
        layout.addWidget(self.scroll)

        # Legacy: results_layout for backwards compatibility with update_results()
        self.results_layout = scroll_layout
        self.results_container = scroll_content

    def add_report_card(
        self,
        title: str,
        description: str,
        project: str,
        focus_area: str,
        required_inputs: List[str],
        topics: List[str],
        location: Optional[str] = None,
        card_type: str = "Report",
        icon: Optional[str] = None
    ):
        """Add a report card to the panel

        Args:
            title: Report title
            description: Report description
            project: Project name
            focus_area: Focus area name
            required_inputs: List of required inputs
            topics: List of associated topics
            location: Optional location indicator
            card_type: Type badge text (not displayed in current design)
            icon: Optional icon (defaults based on card_type if not provided)
        """
        card = ReportCard(
            title=title,
            description=description,
            project=project,
            focus_area=focus_area,
            required_inputs=required_inputs,
            topics=topics,
            location=location,
            card_type=card_type,
            icon=icon
        )
        self.grid.add_card(card)

    def add_tile(self, metadata: ReportMetadata):
        """Add a report tile (existing functionality preserved)

        Args:
            metadata: Report metadata
        """
        tile = ReportTile(metadata)
        tile.clicked.connect(lambda: self.report_clicked.emit(metadata.id))
        self.grid.add_card(tile)

    def clear_results(self):
        """Clear all results from the panel"""
        self.grid.clear_cards()

    def set_cards_per_row(self, count: int):
        """Set number of cards per row

        Args:
            count: Number of cards per row (1-4 recommended)
        """
        self.grid.set_cards_per_row(count)

    def resizeEvent(self, event):
        """Handle resize events to adjust grid layout

        Args:
            event: QResizeEvent
        """
        super().resizeEvent(event)

        # Calculate optimal cards per row based on width
        available_width = self.scroll.width() - 40  # Account for margins
        min_card_width = 300
        spacing = 16

        # Calculate how many cards can fit
        cards_per_row = max(1, (available_width + spacing) //
                            (min_card_width + spacing))
        cards_per_row = min(cards_per_row, 4)  # Cap at 4

    def update_results(self, reports: List[ReportMetadata]):
        """Update displayed reports (legacy method for backwards compatibility)

        Args:
            reports: List of report metadata to display
        """
        # Clear grid
        self.grid.clear_cards()

        # Add report cards using grid
        for report in reports:
            # Only show location for local reports
            location = report.scope.title() if report.scope.lower() == "local" else None

            card = ReportCard(
                title=report.name,
                description=report.description,
                project=report.project,
                focus_area=report.focus_area,
                required_inputs=report.required_inputs,
                topics=report.topics,
                location=location,
                card_type="Report Group" if report.report_type == "group" else "Report",
                icon="📚" if report.report_type == "group" else "📊"
            )
            self.grid.add_card(card)
