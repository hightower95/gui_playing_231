"""
Automated Reports View - Main UI for report library

Layout:
- Left panel (10% width): Topic/category navigation
- Right area (90% width):
  - Top: Search and filter controls
  - Bottom: Scrollable results displayed as tiles
"""
from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QPushButton
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from .presenter import AutomatedReportsPresenter
from .components import LeftPanel, SearchPanel, ResultsPanel


class AutomatedReportsView(QWidget):
    """Main view for automated reports library"""

    TAB_TITLE = "📊 Automated Reports"
    MODULE_ID = "automated_reports"

    def __init__(self, parent: Optional[QWidget] = None, debug_mode: bool = False):
        """Initialize the automated reports view

        Args:
            parent: Parent widget
            debug_mode: Enable debug commands
        """
        super().__init__(parent)
        self.debug_mode = debug_mode
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
        self.left_panel = LeftPanel(debug_mode=self.debug_mode)
        self.left_panel_visible = True

        # Right area (90% width) - Search + Results
        self.right_area = self._create_right_area()

        # Use splitter for resizable panels
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.right_area)
        self.splitter.setStretchFactor(0, 15)  # Left: ~15%
        self.splitter.setStretchFactor(1, 85)  # Right: ~85%
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #3a3a3a;
                width: 1px;
            }
        """)

        main_layout.addWidget(self.splitter)

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

        # Results panel (middle - takes remaining space)
        self.results_panel = ResultsPanel()
        layout.addWidget(self.results_panel, stretch=1)

        # Toggle button for left panel at bottom
        self.toggle_panel_btn = QPushButton("◀")
        self.toggle_panel_btn.setFixedSize(32, 32)
        self.toggle_panel_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                color: #e3e3e3;
                font-size: 14px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #252525;
            }
        """)
        self.toggle_panel_btn.setToolTip("Toggle Topics Panel")
        self.toggle_panel_btn.clicked.connect(self._toggle_left_panel)

        # Add toggle button to bottom-left
        toggle_container = QWidget()
        toggle_layout = QHBoxLayout(toggle_container)
        toggle_layout.setContentsMargins(8, 8, 8, 8)
        toggle_layout.setSpacing(0)
        toggle_layout.addWidget(self.toggle_panel_btn)
        toggle_layout.addStretch()

        layout.addWidget(toggle_container)

        return container

    def _connect_signals(self):
        """Connect component signals to handlers"""
        # Presenter signals
        self.presenter.reports_updated.connect(
            self.results_panel.update_results)
        self.presenter.result_count_updated.connect(
            self._on_result_count_updated)
        self.presenter.topic_selection_changed.connect(
            self._on_topic_selection_changed)
        self.presenter.topic_groups_updated.connect(
            self.left_panel.set_topic_groups)
        self.presenter.filter_values_updated.connect(
            self._on_filter_values_updated)
        self.presenter.sort_methods_updated.connect(
            self._on_sort_methods_updated)

        # Search panel signals
        self.search_panel.search_changed.connect(self._on_search_changed)
        self.search_panel.filters_changed.connect(self._on_filters_changed)
        self.search_panel.filters_cleared.connect(self._on_filters_cleared)
        self.search_panel.sort_changed.connect(self._on_sort_changed)

        # Left panel signals
        self.left_panel.topic_selected.connect(self._on_topic_selected)
        self.left_panel.clear_topics_selected.connect(
            self._on_clear_topics_selected)

        # Debug signals (if debug mode enabled)
        if self.debug_mode:
            self.left_panel.show_count_requested.connect(
                self.search_panel.show_count)
            self.left_panel.hide_count_requested.connect(
                self.search_panel.hide_count)
            self.left_panel.debug_topic_selected.connect(
                self._on_debug_topic_selected)

        # Results panel signals
        self.results_panel.report_clicked.connect(self._on_report_clicked)

    def _on_search_changed(self, text: str):
        """Handle search text changes"""
        self.presenter.on_search_changed(text)

    def _on_filters_changed(self, filters: dict):
        """Handle filter changes"""
        # filters dict has keys like 'project', 'report_type', etc.
        # Need to update all dimensions, including empty ones (to clear)
        for dimension, items in filters.items():
            self.presenter.on_filter_changed(dimension, items)

    def _on_filters_cleared(self):
        """Handle clear all filters"""
        self.presenter.on_filters_cleared()

    def _on_sort_changed(self, sort_id: str, ascending: bool):
        """Handle sort parameter change"""
        self.presenter.on_sort_changed(sort_id, ascending)

    def _on_topic_selected(self, topic: str, ctrl_pressed: bool):
        """Handle topic selection from left panel

        Args:
            topic: Topic name
            ctrl_pressed: Whether ctrl key was held
        """
        self.presenter.on_topic_clicked(topic, ctrl_pressed)

    def _on_clear_topics_selected(self):
        """Handle All Reports click"""
        self.presenter.on_clear_topics_selected()

    def _on_filter_values_updated(self, filter_values: dict):
        """Handle filter values update from presenter

        Args:
            filter_values: Dict of {dimension: [values]}
        """
        # Update filter button options with actual data from model
        if 'project' in filter_values:
            self.search_panel.filter_buttons.project_filter.set_options(filter_values['project'])
        
        if 'input' in filter_values:
            self.search_panel.filter_buttons.input_filter.set_options(filter_values['input'])
        
        if 'report_type' in filter_values:
            self.search_panel.filter_buttons.report_type_filter.set_options(filter_values['report_type'])
        
        if 'scope' in filter_values:
            self.search_panel.filter_buttons.scope_filter.set_options(filter_values['scope'])

    def _on_sort_methods_updated(self, sort_methods: list):
        """Handle sort methods update from presenter

        Args:
            sort_methods: List of sort method dicts
        """
        # Update sort button with these methods
        self.search_panel.sort_button.dropdown.set_options(
            sort_methods,
            self.presenter.filter_state._sort_field,
            self.presenter.filter_state._sort_ascending
        )

    def _on_result_count_updated(self, shown: int, total: int):
        """Handle result count update from presenter

        Args:
            shown: Number of results shown
            total: Total number of results
        """
        self.search_panel.show_count(shown, total)

    def _on_topic_selection_changed(self, selected_topics: set):
        """Handle topic selection state change from presenter

        Args:
            selected_topics: Set of selected topic names
        """
        # Get all topic names
        all_topics = self.left_panel._get_all_topic_names()

        # Update selection state for each topic
        for topic_name in all_topics:
            if topic_name != "All Reports":  # Skip special item
                should_select = topic_name in selected_topics
                self.left_panel.set_topic_selected(topic_name, should_select)

    def _on_debug_topic_selected(self, topic: str):
        """Handle debug topic selection"""
        print(
            f"[AutomatedReportsView] DEBUG: Topic selected via debug menu: {topic}")
        # Trigger normal topic selection
        self.presenter.on_topic_clicked(topic, ctrl_pressed=False)

    def _on_report_clicked(self, report_id: str):
        """Handle report tile click"""
        self.presenter.open_report(report_id)

    def _toggle_left_panel(self):
        """Toggle the visibility of the left panel with animation"""
        if self.left_panel_visible:
            # Hide panel
            self.animation = QPropertyAnimation(
                self.left_panel, b"maximumWidth")
            self.animation.setDuration(250)
            self.animation.setStartValue(self.left_panel.width())
            self.animation.setEndValue(0)
            self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.animation.finished.connect(lambda: self.left_panel.hide())
            self.animation.start()
            self.toggle_panel_btn.setText("▶")
            self.toggle_panel_btn.setToolTip("Show Topics Panel")
        else:
            # Show panel
            self.left_panel.show()
            self.left_panel.setMaximumWidth(16777215)  # Reset to default max
            self.animation = QPropertyAnimation(
                self.left_panel, b"minimumWidth")
            self.animation.setDuration(250)
            self.animation.setStartValue(0)
            self.animation.setEndValue(280)
            self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.animation.start()
            self.toggle_panel_btn.setText("◀")
            self.toggle_panel_btn.setToolTip("Hide Topics Panel")

        self.left_panel_visible = not self.left_panel_visible
