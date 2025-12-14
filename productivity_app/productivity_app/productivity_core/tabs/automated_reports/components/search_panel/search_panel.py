"""
Search Panel - Complete search and filter controls

Combines title, search input, filter buttons, and active filter pills.
"""
from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Signal
from .text_input import SearchInput
from .filter_buttons import FilterButtons
from .active_filter_pills import ActiveFilterPills


class SearchPanel(QFrame):
    """Search and filter controls panel"""

    # Signals
    search_changed = Signal(str)  # Emits search text
    filters_changed = Signal(dict)  # Emits filter dict
    filters_cleared = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize search panel"""
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Setup search panel UI"""
        self.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-bottom: 1px solid #363535;
            }
        """)
        self.setMinimumHeight(120)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(12)

        # Title
        title = QLabel("Report Library")
        title.setStyleSheet("""
            font-size: 20pt;
            color: #4fc3f7;
            border: none;
        """)
        layout.addWidget(title)

        # Results count (below title, hidden by default)
        self.results_count = QLabel("")
        self.results_count.setStyleSheet("""
            font-size: 9pt;
            color: #909090;
            border: none;
        """)
        self.results_count.hide()
        layout.addWidget(self.results_count)

        # Search input
        search_layout = QHBoxLayout()
        self.search_input = SearchInput()
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Filter buttons
        self.filter_buttons = FilterButtons()
        layout.addWidget(self.filter_buttons)

        # Active filter pills (hidden by default)
        self.active_pills = ActiveFilterPills()
        layout.addWidget(self.active_pills)

    def _connect_signals(self):
        """Connect internal component signals"""
        self.search_input.textChanged.connect(self.search_changed.emit)
        self.filter_buttons.filters_changed.connect(self._on_filters_changed)
        self.filter_buttons.filters_cleared.connect(self._on_filters_cleared)
        self.active_pills.filter_removed.connect(self._on_filter_removed)
        self.active_pills.clear_all_clicked.connect(self._on_filters_cleared)

    def _on_filters_changed(self, filters: dict):
        """Handle filter changes

        Args:
            filters: Dict of current filter values
        """
        self.active_pills.update_filters(filters)
        self.filters_changed.emit(filters)

    def _on_filters_cleared(self):
        """Handle clear filters request"""
        self.search_input.clear()
        self.active_pills.update_filters({})
        self.filters_cleared.emit()

    def _on_filter_removed(self, filter_key: str, filter_value: str):
        """Handle individual filter removal

        Args:
            filter_key: Key of filter (e.g., 'project')
            filter_value: Specific value to remove (e.g., 'Project 1')
        """
        # Remove the specific value from the filter button
        if filter_key in self.filter_buttons.filter_buttons:
            filter_btn = self.filter_buttons.filter_buttons[filter_key]
            current_selected = filter_btn.get_selected()
            if filter_value in current_selected:
                current_selected.remove(filter_value)
                # Update the button's selection
                filter_btn.selected_items = current_selected
                filter_btn._update_button_text()
                filter_btn.dropdown.set_options(filter_btn.options, current_selected)
                # Emit filters changed
                self.filter_buttons._on_filter_changed(filter_key, current_selected)

    def show_count(self, count: int, total: int):
        """Show results count with specific values

        Args:
            count: Number of results currently shown
            total: Total number of results
        """
        self.results_count.setText(f"Showing {count} of {total}")
        self.results_count.show()

    def display_count(self):
        """Show the results count (if previously set)"""
        self.results_count.show()

    def hide_count(self):
        """Hide the results count"""
        self.results_count.hide()

    def show_clear_all_filters(self):
        """Show the clear all filters button"""
        self.active_pills.show_clear_all_filters()

    def hide_clear_all_filters(self):
        """Hide the clear all filters button"""
        self.active_pills.hide_clear_all_filters()

    def clear_all(self):
        """Clear search and all filters"""
        self.search_input.clear()
        self.filter_buttons._on_clear_clicked()
