"""
Automated Reports Model - Data management for report library

Handles:
- Report metadata storage
- Search and filtering logic
- Report categorization
- Fake data generation for testing
"""
import random
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
    topics: List[str] = None  # Associated topic groups

    def __post_init__(self):
        if self.required_inputs is None:
            self.required_inputs = []
        if self.contained_reports is None:
            self.contained_reports = []
        if self.topics is None:
            self.topics = []


class AutomatedReportsModel:
    """Model for managing automated reports library"""

    def __init__(self):
        """Initialize with sample data"""
        self.reports = self._generate_fake_reports(15)
        self.filtered_reports = self.reports.copy()

    def _generate_fake_reports(self, count: int = 15) -> List[ReportMetadata]:
        """Generate fake report data for testing

        Args:
            count: Number of reports to generate

        Returns:
            List of fake report metadata
        """
        projects = ["Gamma", "Alpha", "Beta", "Delta", "Epsilon"]
        focus_areas = ["Team Velocity", "Resource Allocation", "Budget Reports",
                       "Quality Metrics", "Sprint Planning", "Risk Analysis"]
        report_types = ["Report", "Analysis",
                        "Graph", "Assessment"]  # Match card types
        report_templates = [
            ("Velocity Tracker",
             "Track team velocity across sprints with trend analysis", "Graph"),
            ("Resource Dashboard",
             "Monitor resource allocation and utilization rates", "Report"),
            ("Budget Overview", "Financial tracking and budget variance reporting", "Report"),
            ("Quality Score", "Code quality metrics and test coverage analysis", "Analysis"),
            ("Sprint Report",
             "Comprehensive sprint performance and completion rates", "Report"),
            ("Risk Assessment", "Risk identification and mitigation tracking", "Assessment"),
            ("Burndown Chart", "Visual sprint burndown with prediction modeling", "Graph"),
            ("Capacity Planning", "Team capacity and workload distribution", "Analysis"),
            ("Defect Tracking", "Bug trends and resolution time analysis", "Graph"),
            ("Performance Metrics",
             "System performance and response time monitoring", "Analysis"),
            ("Customer Satisfaction",
             "User feedback and satisfaction scoring", "Assessment"),
            ("Technical Debt", "Code debt tracking and remediation planning", "Assessment"),
            ("Release Notes", "Automated release documentation generation", "Report"),
            ("Dependency Map", "Project dependencies and integration points", "Graph"),
            ("Time Tracking", "Effort logging and time allocation analysis", "Analysis"),
        ]

        topics_pool = ["Project Management", "Team & Resources", "Financial",
                       "Quality Assurance", "Operations"]
        inputs_pool = ["Team ID", "Sprint Number", "Date Range", "Project Code",
                       "User Group", "Budget ID", "Release Version"]

        reports = []
        for i in range(count):
            template = report_templates[i % len(report_templates)]
            project = random.choice(projects)
            focus = random.choice(focus_areas)

            # Vary the data
            report_num = i + 1
            name = f"{template[0]} {report_num}"
            desc = f"{template[1]} - {project} specific implementation"
            report_type = template[2]  # Use the type from template

            # Random inputs (1-3)
            num_inputs = random.randint(1, 3)
            inputs = random.sample(inputs_pool, num_inputs)

            # Random topics (1-2) - use actual topic categories
            num_topics = random.randint(1, 2)
            topics = random.sample(topics_pool, num_topics)

            reports.append(ReportMetadata(
                id=f"report_{i + 1}",
                name=name,
                description=desc,
                project=project,
                focus_area=focus,
                report_type=report_type,
                scope="local",
                tags=[focus, project],
                required_inputs=inputs,
                topics=topics
            ))

        return reports
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
                       topics: Optional[List[str]] = None,
                       project: Optional[List[str]] = None,
                       focus_area: Optional[List[str]] = None,
                       report_type: Optional[List[str]] = None,
                       scope: Optional[List[str]] = None,
                       search_text: Optional[str] = None) -> List[ReportMetadata]:
        """Filter reports based on criteria

        Args:
            topics: List of topic names to include (OR logic)
            project: List of project names to include (OR logic)
            focus_area: List of focus areas to include (OR logic)
            report_type: List of report types to include (OR logic)
            scope: List of scopes to include (OR logic)
            search_text: Text to search in name and description

        Returns:
            Filtered list of reports
        """
        filtered = self.reports.copy()

        if topics:
            # Filter by topics - report must have at least one matching topic
            filtered = [r for r in filtered if any(
                topic in r.topics for topic in topics)]

        if project:
            filtered = [r for r in filtered if r.project in project]

        if focus_area:
            filtered = [r for r in filtered if r.focus_area in focus_area]

        if report_type:
            filtered = [r for r in filtered if r.report_type in report_type]

        if scope:
            # Case-insensitive scope matching
            scope_lower = [s.lower() for s in scope]
            filtered = [r for r in filtered if r.scope.lower() in scope_lower]

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

    def get_report_types(self) -> List[str]:
        """Get list of unique report types"""
        return sorted(list(set(r.report_type for r in self.reports)))

    def get_required_inputs(self) -> List[str]:
        """Get list of unique required inputs across all reports"""
        inputs_set = set()
        for report in self.reports:
            inputs_set.update(report.required_inputs)
        return sorted(list(inputs_set))

    def get_scopes(self) -> List[str]:
        """Get list of unique scopes"""
        return sorted(list(set(r.scope for r in self.reports)))

    def get_topic_hierarchy(self) -> List[tuple]:
        """Get topic hierarchy with actual counts from report data

        All topics are organized under folder groups. Topics without a natural
        parent are placed in "Other" folder.

        Returns:
            List of tuples: (topic_name, count, children)
            where children is None or List[(child_name, count)]
        """
        # Count reports per topic
        topic_counts = {}
        for report in self.reports:
            for topic in report.topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1

        # Count reports per project (for project subcategories)
        project_counts = {}
        for report in self.reports:
            project_counts[report.project] = project_counts.get(
                report.project, 0) + 1

        # Define folder structure - map topics to their parent folders
        folder_structure = {
            "Team & Resources": ["Team & Resources"],
            "Financial": ["Financial"],
            "Quality": ["Quality Assurance"],
            "Operations": ["Operations"],
        }

        # Assign topics to folders and collect orphans
        folder_topics = {folder: [] for folder in folder_structure.keys()}
        orphan_topics = []

        for topic in sorted(topic_counts.keys()):
            assigned = False
            for folder, keywords in folder_structure.items():
                if topic in keywords or any(kw in topic for kw in keywords):
                    folder_topics[folder].append(topic)
                    assigned = True
                    break
            if not assigned:
                orphan_topics.append(topic)

        # Build hierarchy
        hierarchy = [
            ("All Reports", len(self.reports), None),
        ]

        # Add folders with their topic children
        for folder in sorted(folder_structure.keys()):
            topics = folder_topics[folder]

            # Special case: Project Management has project children
            if topics:
                # Regular folder with topic children
                folder_count = sum(topic_counts.get(topic, 0)
                                   for topic in topics)
                topic_children = [(topic, topic_counts[topic])
                                  for topic in sorted(topics)]
                hierarchy.append((folder, folder_count, topic_children))

        # Add "Other" folder if there are orphan topics
        if orphan_topics:
            other_count = sum(topic_counts.get(topic, 0)
                              for topic in orphan_topics)
            other_children = [(topic, topic_counts[topic])
                              for topic in sorted(orphan_topics)]
            hierarchy.append(("Other", other_count, other_children))

        return hierarchy

    def update_topic_hierarchy_counts(self) -> List[tuple]:
        """Recalculate and return updated topic hierarchy

        Call this after filter changes to update counts based on filtered results.

        Returns:
            Updated topic hierarchy with current filter counts
        """
        return self.get_topic_hierarchy()

    def refresh_data(self):
        """Refresh all derived data (counts, hierarchies, etc.)

        Call this when reports are added, removed, or modified.
        """
        self.filtered_reports = self.reports.copy()

    def sort_reports(self, reports: List[ReportMetadata], sort_by: str = 'name', ascending: bool = True) -> List[ReportMetadata]:
        """Sort reports by specified field

        Args:
            reports: List of reports to sort
            sort_by: Field to sort by ('name', 'date', 'type', 'project')
            ascending: Sort direction

        Returns:
            Sorted list of reports
        """
        if sort_by == 'name':
            sorted_reports = sorted(reports, key=lambda r: r.name.lower())
        elif sort_by == 'date':
            # For now, sort by ID as proxy for creation date
            sorted_reports = sorted(reports, key=lambda r: r.id)
        elif sort_by == 'type':
            sorted_reports = sorted(reports, key=lambda r: (
                r.report_type, r.name.lower()))
        elif sort_by == 'project':
            sorted_reports = sorted(
                reports, key=lambda r: (r.project, r.name.lower()))
        else:
            # Default to name
            sorted_reports = sorted(reports, key=lambda r: r.name.lower())

        if not ascending:
            sorted_reports = list(reversed(sorted_reports))

        return sorted_reports
