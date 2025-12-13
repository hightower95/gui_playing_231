"""
Automated Reports Model - Data management for report library

Handles:
- Report metadata storage
- Search and filtering logic
- Report categorization
"""
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ReportMetadata:
    """Metadata for a single report"""
    id: str
    name: str
    description: str
    project: str
    focus_area: str
    report_type: str  # "single" or "group"
    scope: str  # "local" or "shared"
    tags: List[str]
    required_inputs: List[str] = None
    contained_reports: List[str] = None  # For report groups

    def __post_init__(self):
        if self.required_inputs is None:
            self.required_inputs = []
        if self.contained_reports is None:
            self.contained_reports = []


class AutomatedReportsModel:
    """Model for managing automated reports library"""

    def __init__(self):
        """Initialize with sample data"""
        self.reports = self._load_sample_reports()
        self.filtered_reports = self.reports.copy()

    def _load_sample_reports(self) -> List[ReportMetadata]:
        """Load sample report data matching the image"""
        return [
            ReportMetadata(
                id="sprint_velocity",
                name="Sprint Velocity Report",
                description="Team velocity trends and sprint completion rates",
                project="Gamma",
                focus_area="Agile",
                report_type="single",
                scope="local",
                tags=["Agile", "Team Management"],
                required_inputs=["Team ID", "Sprint Count"]
            ),
            ReportMetadata(
                id="team_performance_bundle",
                name="Team Performance Bundle",
                description="Comprehensive team analytics including velocity, resource allocation, and quality metrics",
                project="Gamma",
                focus_area="Agile",
                report_type="group",
                scope="local",
                tags=["Agile", "Team Management", "Quality"],
                contained_reports=[
                    "Resource Allocation...", "Quality Metrics Trac...", "Sprint Velocity Repo..."]
            ),
        ]

    def get_all_reports(self) -> List[ReportMetadata]:
        """Get all available reports"""
        return self.reports

    def filter_reports(self,
                       project: Optional[str] = None,
                       focus_area: Optional[str] = None,
                       report_type: Optional[str] = None,
                       scope: Optional[str] = None,
                       search_text: Optional[str] = None) -> List[ReportMetadata]:
        """Filter reports based on criteria"""
        filtered = self.reports.copy()

        if project:
            filtered = [r for r in filtered if r.project == project]

        if focus_area:
            filtered = [r for r in filtered if r.focus_area == focus_area]

        if report_type:
            filtered = [r for r in filtered if r.report_type == report_type]

        if scope:
            filtered = [r for r in filtered if r.scope == scope]

        if search_text:
            search_lower = search_text.lower()
            filtered = [r for r in filtered if
                        search_lower in r.name.lower() or
                        search_lower in r.description.lower()]

        self.filtered_reports = filtered
        return filtered

    def get_projects(self) -> List[str]:
        """Get list of unique projects"""
        return list(set(r.project for r in self.reports))

    def get_focus_areas(self) -> List[str]:
        """Get list of unique focus areas"""
        return list(set(r.focus_area for r in self.reports))
