"""
Automated Reports Presenter - Business logic coordination

Handles:
- User interactions from view
- Model updates and queries
- Signal emissions for UI updates
"""
from typing import Optional
from PySide6.QtCore import QObject, Signal
from .model import AutomatedReportsModel, ReportMetadata


class AutomatedReportsPresenter(QObject):
    """Presenter for automated reports module"""

    # Signals
    reports_updated = Signal(list)  # Emits list of ReportMetadata
    filter_changed = Signal(dict)  # Emits filter criteria

    def __init__(self, parent=None):
        """Initialize presenter with model"""
        super().__init__(parent)
        self.model = AutomatedReportsModel()

    def initialize(self):
        """Initialize and load initial data"""
        reports = self.model.get_all_reports()
        self.reports_updated.emit(reports)

    def apply_filters(self,
                      project: Optional[str] = None,
                      focus_area: Optional[str] = None,
                      report_type: Optional[str] = None,
                      scope: Optional[str] = None,
                      search_text: Optional[str] = None):
        """Apply filters and update view"""
        filtered = self.model.filter_reports(
            project=project,
            focus_area=focus_area,
            report_type=report_type,
            scope=scope,
            search_text=search_text
        )
        self.reports_updated.emit(filtered)

        # Emit filter state
        self.filter_changed.emit({
            'project': project,
            'focus_area': focus_area,
            'report_type': report_type,
            'scope': scope,
            'search_text': search_text
        })

    def clear_filters(self):
        """Clear all filters and show all reports"""
        reports = self.model.get_all_reports()
        self.reports_updated.emit(reports)
        self.filter_changed.emit({})

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
