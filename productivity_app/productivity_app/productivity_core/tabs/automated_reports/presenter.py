"""
Automated Reports Presenter - Business logic coordination

Handles:
- User interactions from view
- Model updates and queries
- Signal emissions for UI updates
- Async data loading via worker threads
"""
from typing import Optional, Set, Dict, List
from PySide6.QtCore import QObject, Signal, QThread, QRunnable, QThreadPool
from .model import AutomatedReportsModel, ReportMetadata
from .filter_state import FilterState


class LoadReportsWorker(QRunnable):
    """Worker for loading reports in background thread"""

    class Signals(QObject):
        finished = Signal(list)  # Emits list of ReportMetadata
        error = Signal(str)

    def __init__(self, model: AutomatedReportsModel):
        super().__init__()
        self.model = model
        self.signals = self.Signals()

    def run(self):
        """Load reports in background"""
        try:
            reports = self.model.get_all_reports()
            self.signals.finished.emit(reports)
        except Exception as e:
            self.signals.error.emit(str(e))


class AutomatedReportsPresenter(QObject):
    """Presenter for automated reports module"""

    # Signals
    reports_updated = Signal(list)  # Emits list of ReportMetadata
    result_count_updated = Signal(int, int)  # Emits (shown, total)
    topic_selection_changed = Signal(set)  # Emits set of selected topic names
    # Emits list of (name, count, children) tuples
    topic_groups_updated = Signal(list)
    filter_values_updated = Signal(dict)  # Emits dict of {dimension: [values]}
    # Emits list of {id, label, ascending, icon} dicts
    sort_methods_updated = Signal(list)

    def __init__(self, parent=None):
        """Initialize presenter with model and filter state"""
        super().__init__(parent)
        self.model = AutomatedReportsModel()
        self.filter_state = FilterState()
        self.thread_pool = QThreadPool()

    def initialize(self):
        """Initialize and load initial data"""
        self._load_topic_groups()
        self._load_filter_values()
        self._load_sort_methods()
        self._load_reports_async()

    def _load_reports_async(self):
        """Load reports in background thread"""
        worker = LoadReportsWorker(self.model)
        worker.signals.finished.connect(self._on_reports_loaded)
        worker.signals.error.connect(self._on_reports_load_error)
        self.thread_pool.start(worker)

    def _on_reports_loaded(self, reports: List[ReportMetadata]):
        """Handle reports loaded from worker

        Args:
            reports: List of loaded reports
        """
        self.reports_updated.emit(reports)
        self.update_result_count()

    def _on_reports_load_error(self, error: str):
        """Handle error loading reports

        Args:
            error: Error message
        """
        print(f"[Presenter] Error loading reports: {error}")

    def _load_topic_groups(self):
        """Load topic groups from model and emit signal"""
        # TODO: Get from model - for now using hardcoded structure
        topic_data = [
            ("All Reports", 10, None),
            ("Project Management", 6, [
                ("Gamma", 3),
                ("Alpha", 2),
                ("Beta", 1)
            ]),
            ("Team & Resources", 6, [
                ("Team Velocity", 3),
                ("Resource Allocation", 3)
            ]),
            ("Financial", 3, [
                ("Budget Reports", 2),
                ("Cost Analysis", 1)
            ]),
        ]
        self.topic_groups_updated.emit(topic_data)

    def _load_filter_values(self):
        """Load available filter values from model and emit signal"""
        # Get unique values from model
        filter_values = {
            'project': self.model.get_projects(),
            'focus_area': self.model.get_focus_areas(),
            'report_type': ['Single Report', 'Report Group'],
            'scope': ['Local', 'Shared']
        }
        self.filter_values_updated.emit(filter_values)

    def _load_sort_methods(self):
        """Load available sort methods and emit signal"""
        sort_methods = [
            {'id': 'name', 'label': 'Name (A-Z)', 'ascending': True,
             'icon': 'sort_by_alpha_28dp_E3E3E3_FILL0_wght200_GRAD0_opsz24.svg'},
            {'id': 'name', 'label': 'Name (Z-A)', 'ascending': False,
             'icon': 'sort_by_alpha_28dp_E3E3E3_FILL0_wght200_GRAD0_opsz24.svg'},
            {'id': 'date', 'label': 'Date Modified (Newest)', 'ascending': False,
             'icon': 'calendar_today_28dp_E3E3E3_FILL0_wght200_GRAD0_opsz24.svg'},
            {'id': 'date', 'label': 'Date Modified (Oldest)', 'ascending': True,
             'icon': 'calendar_today_28dp_E3E3E3_FILL0_wght200_GRAD0_opsz24.svg'},
            {'id': 'usage', 'label': 'Most Used', 'ascending': False, 'icon': None}
        ]
        self.sort_methods_updated.emit(sort_methods)

    def on_topic_clicked(self, name: str, ctrl_pressed: bool):
        """Handle topic selection with multi-select support

        Args:
            name: Topic name
            ctrl_pressed: Whether ctrl key was held
        """
        # Update filter state
        self.filter_state.select_topic(name, is_multi_select=ctrl_pressed)

        # Apply filters and update UI
        self._apply_current_filters()
        self._update_ui_selection_state()

        # Debug output
        print(f"[Presenter] Topic clicked: '{name}' (ctrl={ctrl_pressed})")
        print(
            f"[Presenter] Filter state: {self.filter_state.get_state_summary()}")

    def on_clear_topics_selected(self):
        """Handle All Reports click - clear all topic selections"""
        self.filter_state.deselect_all_topics()
        self._apply_current_filters()
        self._update_ui_selection_state()

        print("[Presenter] All topics cleared (All Reports clicked)")
        print(
            f"[Presenter] Filter state: {self.filter_state.get_state_summary()}")

    def on_filter_changed(self, dimension: str, items: Set[str]):
        """Handle filter dimension change

        Args:
            dimension: Filter dimension name (project, focus_area, report_type, scope)
            items: Set of selected items for this dimension
        """
        self.filter_state.set_filter(dimension, items)
        self._apply_current_filters()

        # Debug output
        print(f"[Presenter] Filter changed: {dimension} = {items}")
        print(
            f"[Presenter] Filter state: {self.filter_state.get_state_summary()}")

    def on_search_changed(self, text: str):
        """Handle search text change

        Args:
            text: Search text
        """
        self.filter_state.set_search(text if text else None)
        self._apply_current_filters()

        # Debug output
        if text:
            print(f"[Presenter] Search changed: '{text}'")

    def on_sort_changed(self, sort_id: str, ascending: bool):
        """Handle sort parameter change

        Args:
            sort_id: Sort field ID (name, date, usage)
            ascending: Sort direction
        """
        self.filter_state.set_sort(sort_id, ascending)
        self._apply_current_filters()

        # Debug output
        print(f"[Presenter] Sort changed: {sort_id} (ascending={ascending})")

    def on_filters_cleared(self):
        """Handle clear all filters request"""
        self.filter_state.clear_all()
        self._apply_current_filters()
        self._update_ui_selection_state()

        print("[Presenter] All filters cleared")

    def _apply_current_filters(self):
        """Query model with current filter state and emit results"""
        query = self.filter_state.to_query_dict()

        # Query model (for now, use existing filter_reports method)
        # TODO: Update model to handle topic filtering
        filtered = self.model.filter_reports(
            project=query['project'][0] if query['project'] else None,
            focus_area=query['focus_area'][0] if query['focus_area'] else None,
            report_type=query['report_type'][0] if query['report_type'] else None,
            scope=query['scope'][0] if query['scope'] else None,
            search_text=query['search_text']
        )

        self.reports_updated.emit(filtered)
        self.update_result_count()

    def _update_ui_selection_state(self):
        """Push topic selection state to view"""
        selected = self.filter_state.selected_topics
        self.topic_selection_changed.emit(selected)

    def update_result_count(self):
        """Update result count based on current filters"""
        query = self.filter_state.to_query_dict()

        # Get total count
        total = len(self.model.get_all_reports())

        # Get filtered count
        filtered = self.model.filter_reports(
            project=query['project'][0] if query['project'] else None,
            focus_area=query['focus_area'][0] if query['focus_area'] else None,
            report_type=query['report_type'][0] if query['report_type'] else None,
            scope=query['scope'][0] if query['scope'] else None,
            search_text=query['search_text']
        )
        shown = len(filtered)

        self.result_count_updated.emit(shown, total)

    # Legacy methods - keeping for backward compatibility
    def apply_filters(self,
                      project: Optional[str] = None,
                      focus_area: Optional[str] = None,
                      report_type: Optional[str] = None,
                      scope: Optional[str] = None,
                      search_text: Optional[str] = None):
        """Apply filters and update view (legacy method)"""
        filtered = self.model.filter_reports(
            project=project,
            focus_area=focus_area,
            report_type=report_type,
            scope=scope,
            search_text=search_text
        )
        self.reports_updated.emit(filtered)

    def clear_filters(self):
        """Clear all filters and show all reports (legacy method)"""
        self.on_filters_cleared()

    def get_available_projects(self):
        """Get list of projects for filter dropdown"""
        return self.model.get_projects()

    def get_available_focus_areas(self):
        """Get list of focus areas for filter dropdown"""
        return self.model.get_focus_areas()

    def open_report(self, report_id: str):
        """Handle report opening (placeholder)"""
        print(f"[AutomatedReportsPresenter] Opening report: {report_id}")
        # TODO: Implement report opening logic
