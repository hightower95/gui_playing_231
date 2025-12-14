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
        
        return reports
    
    def _load_sample_reports(self) -> List[ReportMetadata]:
        Args:
            count: Number of reports to generate
            
        Returns:
            List of fake report metadata
        """
        projects = ["Gamma", "Alpha", "Beta", "Delta", "Epsilon"]
        focus_areas = ["Team Velocity", "Resource Allocation", "Budget Reports", 
                       "Quality Metrics", "Sprint Planning", "Risk Analysis"]
        report_templates = [
            ("Velocity Tracker", "Track team velocity across sprints with trend analysis"),
            ("Resource Dashboard", "Monitor resource allocation and utilization rates"),
            ("Budget Overview", "Financial tracking and budget variance reporting"),
            ("Quality Score", "Code quality metrics and test coverage analysis"),
            ("Sprint Report", "Comprehensive sprint performance and completion rates"),
            ("Risk Assessment", "Risk identification and mitigation tracking"),
            ("Burndown Chart", "Visual sprint burndown with prediction modeling"),
            ("Capacity Planning", "Team capacity and workload distribution"),
            ("Defect Tracking", "Bug trends and resolution time analysis"),
            ("Performance Metrics", "System performance and response time monitoring"),
            ("Customer Satisfaction", "User feedback and satisfaction scoring"),
            ("Technical Debt", "Code debt tracking and remediation planning"),
            ("Release Notes", "Automated release documentation generation"),
            ("Dependency Map", "Project dependencies and integration points"),
            ("Time Tracking", "Effort logging and time allocation analysis"),
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
            
            # Random inputs (1-3)
            num_inputs = random.randint(1, 3)
            inputs = random.sample(inputs_pool, num_inputs)
            
            # Random topics (1-2)
            num_topics = random.randint(1, 2)
            topics = random.sample(topics_pool, num_topics)
            
            reports.append(ReportMetadata(
                id=f"report_{i + 1}",
                name=name,
                description=desc,
                project=project,
                focus_area=focus,
                report_type="single",
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
