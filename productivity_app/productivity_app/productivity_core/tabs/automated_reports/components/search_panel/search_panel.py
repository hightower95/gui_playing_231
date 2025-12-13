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
        self.setMaximumHeight(180)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("Report Library")
        title.setStyleSheet("""
            font-size: 14pt;
            font-weight: bold;
            color: #4fc3f7;
        """)
        layout.addWidget(title)

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

    def _on_filter_removed(self, filter_key: str):
        """Handle individual filter removal

        Args:
            filter_key: Key of filter to remove
        """
        # Update the corresponding combobox to default
        if filter_key == 'project':
            self.filter_buttons.project_combo.setCurrentIndex(0)
        elif filter_key == 'focus_area':
            self.filter_buttons.focus_area_combo.setCurrentIndex(0)
        elif filter_key == 'report_type':
            self.filter_buttons.report_type_combo.setCurrentIndex(0)
        elif filter_key == 'scope':
            self.filter_buttons.scope_combo.setCurrentIndex(0)

        # The combobox change will trigger filters_changed signal

    def clear_all(self):
        """Clear search and all filters"""
        self.search_input.clear()
        self.filter_buttons._on_clear_clicked()
