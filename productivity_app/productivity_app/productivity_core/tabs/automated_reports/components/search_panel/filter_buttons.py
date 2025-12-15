"""
Filter Buttons - Modern filter buttons with checkbox dropdowns

Provides filter buttons for Project, Input Required, Report Type, and Scope.
"""
from typing import Optional, List, Dict, Set
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal
from .filter_button import FilterButton


class FilterButtons(QWidget):
    """Container for filter buttons and clear filters button"""

    # Signals
    filters_changed = Signal(dict)  # Emits dict with filter values
    filters_cleared = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize filter buttons"""
        super().__init__(parent)
        self.filter_buttons: Dict[str, FilterButton] = {}
        self._setup_ui()

    def _setup_ui(self):
        """Setup filter buttons UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Create filter buttons
        self.project_filter = FilterButton(
            # 20 items to test scrolling
            "Project", [f"Project {i}" for i in range(1, 21)])
        self.project_filter.selection_changed.connect(self._on_filter_changed)
        layout.addWidget(self.project_filter)
        self.filter_buttons['project'] = self.project_filter

        self.input_filter = FilterButton(
            "Input", ["Team ID", "Sprint Number", "Date Range", "Project Code", "Budget ID"])
        self.input_filter.setToolTip("Input Required")
        self.input_filter.selection_changed.connect(
            self._on_filter_changed)
        layout.addWidget(self.input_filter)
        self.filter_buttons['input'] = self.input_filter

        self.report_type_filter = FilterButton(
            "Report Type", ["Single Report", "Report Bundle"])
        self.report_type_filter.selection_changed.connect(
            self._on_filter_changed)
        layout.addWidget(self.report_type_filter)
        self.filter_buttons['report_type'] = self.report_type_filter

        self.scope_filter = FilterButton(
            "Scope", ["Team", "Department", "Organization"])
        self.scope_filter.selection_changed.connect(self._on_filter_changed)
        layout.addWidget(self.scope_filter)
        self.filter_buttons['scope'] = self.scope_filter

        layout.addStretch()

    def _on_filter_changed(self, filter_name: str, selected_items: Set[str]):
        """Handle filter change and emit signal

        Args:
            filter_name: Name of the filter that changed
            selected_items: Set of selected items
        """
        filters = self.get_current_filters()
        self.filters_changed.emit(filters)

    def _on_clear_clicked(self):
        """Clear all filters"""
        for filter_btn in self.filter_buttons.values():
            filter_btn.clear_selection()
        self.filters_cleared.emit()

    def clear_all(self):
        """Clear all filter selections"""
        self._on_clear_clicked()

    def get_current_filters(self) -> Dict[str, Set[str]]:
        """Get current filter values

        Returns:
            Dict with filter keys and sets of selected values
        """
        return {
            'project': self.project_filter.get_selected(),
            'input': self.input_filter.get_selected(),
            'report_type': self.report_type_filter.get_selected(),
            'scope': self.scope_filter.get_selected(),
        }

    def populate_options(self, projects: List[str] = None, inputs: List[str] = None):
        """Populate dropdown options

        Args:
            projects: List of project names
            inputs: List of required input names
        """
        if projects:
            self.project_filter.set_options(projects)

        if inputs:
            self.input_filter.set_options(inputs)
