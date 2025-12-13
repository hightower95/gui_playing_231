"""
Automated Reports View - Main UI for report library

Layout:
- Left panel (10% width): Topic/category navigation
- Right area (90% width):
  - Top: Search and filter controls
  - Bottom: Scrollable results displayed as tiles
"""
from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSplitter
from PySide6.QtCore import Qt
from .presenter import AutomatedReportsPresenter
from .components import LeftPanel, SearchPanel, ResultsPanel


class AutomatedReportsView(QWidget):
    """Main view for automated reports library"""

    TAB_TITLE = "📊 Automated Reports"
    MODULE_ID = "automated_reports"

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the automated reports view"""
        super().__init__(parent)
        self.presenter = AutomatedReportsPresenter(self)
        self._setup_ui()
        self._connect_signals()

        # Initialize data
        self.presenter.initialize()

    def _setup_ui(self):
        """Setup the three-panel layout"""
        self.setStyleSheet("background-color: #1e1e1e;")

        # Main horizontal layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left panel (10% width) - Topics/Categories
        self.left_panel = LeftPanel()

        # Right area (90% width) - Search + Results
        self.right_area = self._create_right_area()

        # Use splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.left_panel)
        splitter.addWidget(self.right_area)
        splitter.setStretchFactor(0, 15)  # Left: ~15%
        splitter.setStretchFactor(1, 85)  # Right: ~85%
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #3a3a3a;
                width: 1px;
            }
        """)

        main_layout.addWidget(splitter)

    def _create_right_area(self) -> QWidget:
        """Create right area with search panel and results panel"""
        container = QWidget()
        container.setStyleSheet("background-color: #1e1e1e;")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Search panel (top)
        self.search_panel = SearchPanel()
        layout.addWidget(self.search_panel)

        # Results panel (bottom - takes remaining space)
        self.results_panel = ResultsPanel()
        layout.addWidget(self.results_panel, stretch=1)

        return container

    def _connect_signals(self):
        """Connect component signals to handlers"""
        # Presenter signals
        self.presenter.reports_updated.connect(
            self.results_panel.update_results)

        # Search panel signals
        self.search_panel.search_changed.connect(self._on_search_changed)
        self.search_panel.filters_changed.connect(self._on_filters_changed)
        self.search_panel.filters_cleared.connect(self._on_filters_cleared)

        # Left panel signals
        self.left_panel.topic_selected.connect(self._on_topic_selected)

        # Results panel signals
        self.results_panel.report_clicked.connect(self._on_report_clicked)

    def _on_search_changed(self, text: str):
        """Handle search text changes"""
        filters = self.search_panel.filter_buttons.get_current_filters()
        self.presenter.apply_filters(
            search_text=text if text else None, **filters)

    def _on_filters_changed(self, filters: dict):
        """Handle filter changes"""
        search_text = self.search_panel.search_input.text()
        self.presenter.apply_filters(
            search_text=search_text if search_text else None,
            **filters
        )

    def _on_filters_cleared(self):
        """Handle clear all filters"""
        self.presenter.clear_filters()

    def _on_topic_selected(self, topic: str):
        """Handle topic selection from left panel"""
        print(f"[AutomatedReportsView] Topic selected: {topic}")
        # TODO: Implement topic filtering

    def _on_report_clicked(self, report_id: str):
        """Handle report tile click"""
        self.presenter.open_report(report_id)
