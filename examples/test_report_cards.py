"""Test GUI for Report Cards

Simple test window to display and interact with report cards.
"""
from productivity_app.productivity_core.tabs.automated_reports.components.results_panel import ResultsPanel
from PySide6.QtWidgets import QApplication
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    """Run test GUI"""
    app = QApplication(sys.argv)

    # Create results panel
    panel = ResultsPanel()
    panel.setMinimumSize(1200, 800)
    panel.setWindowTitle("Report Card Test")

    # Add sample cards
    sample_cards = [
        {
            "title": "Sprint Velocity Report",
            "description": "Track team velocity across sprints with trend analysis and prediction modeling",
            "project": "Gamma",
            "focus_area": "Team Velocity",
            "required_inputs": ["Team ID", "Sprint Number"],
            "topics": ["Project Management", "Team & Resources"],
            "location": "Local",
            "card_type": "Analysis",
        },
        {
            "title": "Resource Dashboard",
            "description": "Monitor resource allocation and utilization rates across all projects",
            "project": "Alpha",
            "focus_area": "Resource Allocation",
            "required_inputs": ["Date Range", "Project Code", "User Group"],
            "topics": ["Team & Resources"],
            "location": None,  # No location
            "card_type": "Report",
        },
        {
            "title": "Budget Overview",
            "description": "Financial tracking and budget variance reporting with forecasting",
            "project": "Beta",
            "focus_area": "Budget Reports",
            "required_inputs": ["Budget ID"],
            "topics": ["Financial"],
            "location": "Local",
            "card_type": "Report",
        },
        {
            "title": "Quality Score Tracker",
            "description": "Code quality metrics and test coverage analysis with trends",
            "project": "Gamma",
            "focus_area": "Quality Metrics",
            "required_inputs": ["Team ID", "Date Range"],
            "topics": ["Quality Assurance"],
            "location": "Local",
            "card_type": "Graph",
        },
        {
            "title": "Sprint Planning Report",
            "description": "Comprehensive sprint planning with capacity analysis and workload distribution",
            "project": "Delta",
            "focus_area": "Sprint Planning",
            "required_inputs": ["Sprint Number", "Team ID"],
            "topics": ["Project Management"],
            "location": None,
            "card_type": "Assessment",
        },
        {
            "title": "Risk Assessment Dashboard",
            "description": "Risk identification and mitigation tracking across all active projects",
            "project": "Epsilon",
            "focus_area": "Risk Analysis",
            "required_inputs": ["Project Code"],
            "topics": ["Project Management", "Operations"],
            "location": "Local",
            "card_type": "Assessment",
        },
        {
            "title": "Burndown Chart Generator",
            "description": "Visual sprint burndown with prediction modeling and completion estimates",
            "project": "Gamma",
            "focus_area": "Sprint Planning",
            "required_inputs": [],
            "topics": ["Project Management"],
            "location": None,
            "card_type": "Graph",
        },
        {
            "title": "Capacity Planning Tool",
            "description": "Team capacity and workload distribution analysis with recommendations",
            "project": "Alpha",
            "focus_area": "Resource Allocation",
            "required_inputs": ["Team ID", "Date Range", "Project Code"],
            "topics": [],
            "location": "Local",
            "card_type": "Analysis",
        },
    ]

    for card_data in sample_cards:
        panel.add_report_card(
            title=card_data["title"],
            description=card_data["description"],
            project=card_data["project"],
            focus_area=card_data["focus_area"],
            required_inputs=card_data["required_inputs"],
            topics=card_data["topics"],
            location=card_data.get("location"),
            card_type=card_data.get("card_type", "Report")
        )

    panel.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
