"""
Report Decorator Design - Registry Pattern for Report Catalogue

This module demonstrates how to build a decorator-based report registry
that can be dynamically updated and queried.

Key Concepts:
1. Centralized registry to track all decorated reports
2. Metadata extraction from decorator parameters
3. Dynamic updates (add/remove/modify reports)
4. Query interface for the GUI to access reports
"""
from typing import Callable, Dict, List, Optional, Any
from dataclasses import dataclass, field
from functools import wraps
import inspect


# ============================================================================
# METADATA STRUCTURE
# ============================================================================

@dataclass
class ReportInput:
    """Define an input parameter for a report"""
    name: str
    type: str  # "string", "int", "date", "list", etc.
    description: str = ""
    required: bool = True
    default: Any = None


@dataclass
class ReportOutput:
    """Define an output from a report"""
    name: str
    type: str  # "dataframe", "chart", "file", "dict", etc.
    description: str = ""


@dataclass
class ReportMetadata:
    """Complete metadata for a registered report"""
    id: str
    name: str
    description: str
    function: Callable
    inputs: List[ReportInput] = field(default_factory=list)
    outputs: List[ReportOutput] = field(default_factory=list)
    category: str = "General"
    tags: List[str] = field(default_factory=list)
    author: str = ""
    version: str = "1.0"


# ============================================================================
# REGISTRY (Singleton Pattern)
# ============================================================================

class ReportRegistry:
    """
    Centralized registry for all reports.

    This is a singleton - only one instance exists in the application.
    All @report decorators register to this same instance.
    """
    _instance = None
    _reports: Dict[str, ReportMetadata] = {}

    def __new__(cls):
        """Ensure only one instance exists (Singleton)"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._reports = {}
        return cls._instance

    def register(self, metadata: ReportMetadata):
        """Add or update a report in the registry

        Args:
            metadata: Report metadata to register
        """
        self._reports[metadata.id] = metadata
        print(
            f"[Registry] Registered report: {metadata.name} (ID: {metadata.id})")

    def unregister(self, report_id: str):
        """Remove a report from the registry

        Args:
            report_id: ID of report to remove
        """
        if report_id in self._reports:
            del self._reports[report_id]
            print(f"[Registry] Unregistered report: {report_id}")

    def get(self, report_id: str) -> Optional[ReportMetadata]:
        """Get a specific report by ID

        Args:
            report_id: Report identifier

        Returns:
            Report metadata or None if not found
        """
        return self._reports.get(report_id)

    def get_all(self) -> List[ReportMetadata]:
        """Get all registered reports

        Returns:
            List of all report metadata
        """
        return list(self._reports.values())

    def filter_by_category(self, category: str) -> List[ReportMetadata]:
        """Get reports in a specific category

        Args:
            category: Category name

        Returns:
            List of matching reports
        """
        return [r for r in self._reports.values() if r.category == category]

    def filter_by_tags(self, tags: List[str]) -> List[ReportMetadata]:
        """Get reports matching any of the given tags

        Args:
            tags: List of tags to match

        Returns:
            List of matching reports
        """
        return [r for r in self._reports.values()
                if any(tag in r.tags for tag in tags)]

    def search(self, query: str) -> List[ReportMetadata]:
        """Search reports by name or description

        Args:
            query: Search text

        Returns:
            List of matching reports
        """
        query_lower = query.lower()
        return [r for r in self._reports.values()
                if query_lower in r.name.lower() or query_lower in r.description.lower()]

    def clear(self):
        """Remove all reports from registry"""
        self._reports.clear()
        print("[Registry] Cleared all reports")

    def count(self) -> int:
        """Get number of registered reports"""
        return len(self._reports)


# ============================================================================
# DECORATOR
# ============================================================================

def report(
    name: str,
    description: str = "",
    inputs: List[ReportInput] = None,
    outputs: List[ReportOutput] = None,
    category: str = "General",
    tags: List[str] = None,
    author: str = "",
    version: str = "1.0"
):
    """
    Decorator to register a function as a report in the catalogue.

    Usage:
        @report(
            name="Sales Report",
            description="Monthly sales analysis",
            inputs=[
                ReportInput("start_date", "date", "Start of period"),
                ReportInput("end_date", "date", "End of period"),
            ],
            outputs=[
                ReportOutput("summary", "dataframe", "Sales summary"),
                ReportOutput("chart", "chart", "Sales trend chart"),
            ],
            category="Financial",
            tags=["sales", "monthly"],
            author="John Doe"
        )
        def generate_sales_report(start_date, end_date):
            # Report logic here
            return summary_df, chart

    Args:
        name: Display name for the report
        description: Detailed description of what the report does
        inputs: List of input parameters
        outputs: List of output types
        category: Category for organization
        tags: Tags for filtering
        author: Report author
        version: Report version
    """
    def decorator(func: Callable) -> Callable:
        # Generate unique ID from function name and module
        report_id = f"{func.__module__}.{func.__name__}"

        # Create metadata
        metadata = ReportMetadata(
            id=report_id,
            name=name,
            description=description or func.__doc__ or "",
            function=func,
            inputs=inputs or [],
            outputs=outputs or [],
            category=category,
            tags=tags or [],
            author=author,
            version=version
        )

        # Register with the global registry
        registry = ReportRegistry()
        registry.register(metadata)

        # Wrap the function to preserve its behavior
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Attach metadata to the function for introspection
        wrapper._report_metadata = metadata

        return wrapper

    return decorator


# ============================================================================
# DYNAMIC UPDATE HELPERS
# ============================================================================

def update_report_metadata(
    report_id: str,
    name: str = None,
    description: str = None,
    category: str = None,
    tags: List[str] = None
):
    """
    Dynamically update report metadata without re-decorating.

    Args:
        report_id: ID of report to update
        name: New name (optional)
        description: New description (optional)
        category: New category (optional)
        tags: New tags (optional)
    """
    registry = ReportRegistry()
    metadata = registry.get(report_id)

    if not metadata:
        print(f"[Update] Report {report_id} not found")
        return False

    # Update fields
    if name is not None:
        metadata.name = name
    if description is not None:
        metadata.description = description
    if category is not None:
        metadata.category = category
    if tags is not None:
        metadata.tags = tags

    # Re-register (updates existing entry)
    registry.register(metadata)
    print(f"[Update] Updated report {report_id}")
    return True


def hot_reload_report(report_id: str, new_function: Callable):
    """
    Replace the function implementation without losing metadata.

    This allows "hot reloading" - updating report logic without restarting.

    Args:
        report_id: ID of report to update
        new_function: New function implementation
    """
    registry = ReportRegistry()
    metadata = registry.get(report_id)

    if not metadata:
        print(f"[HotReload] Report {report_id} not found")
        return False

    # Replace function but keep metadata
    metadata.function = new_function
    registry.register(metadata)
    print(f"[HotReload] Replaced function for {report_id}")
    return True


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    # Example 1: Basic report registration
    @report(
        name="Team Velocity Report",
        description="Analyze team velocity over sprints",
        inputs=[
            ReportInput("team_id", "string", "Team identifier", required=True),
            ReportInput("sprint_count", "int",
                        "Number of sprints to analyze", default=5),
        ],
        outputs=[
            ReportOutput("velocity_data", "dataframe", "Sprint velocity data"),
            ReportOutput("trend_chart", "chart",
                         "Velocity trend visualization"),
        ],
        category="Agile",
        tags=["velocity", "sprint", "agile"],
        author="Peter"
    )
    def generate_velocity_report(team_id: str, sprint_count: int = 5):
        """Generate velocity report for a team"""
        print(
            f"Generating velocity report for {team_id} over {sprint_count} sprints")
        return {"velocity": [10, 12, 15]}, "chart_data"

    # Example 2: Another report

    @report(
        name="Budget Overview",
        description="Financial summary and budget tracking",
        inputs=[
            ReportInput("budget_id", "string", "Budget ID"),
            ReportInput("date_range", "daterange", "Period to analyze"),
        ],
        outputs=[
            ReportOutput("summary", "dict", "Budget summary"),
        ],
        category="Financial",
        tags=["budget", "financial"]
    )
    def generate_budget_report(budget_id: str, date_range):
        """Generate budget report"""
        print(f"Generating budget report for {budget_id}")
        return {"total": 100000, "spent": 75000}

    # Example 3: Access the registry
    print("\n" + "="*60)
    print("ACCESSING THE REGISTRY")
    print("="*60)

    registry = ReportRegistry()

    print(f"\nTotal reports registered: {registry.count()}")

    print("\nAll reports:")
    for report_meta in registry.get_all():
        print(f"  - {report_meta.name} (ID: {report_meta.id})")
        print(f"    Category: {report_meta.category}")
        print(f"    Inputs: {len(report_meta.inputs)}")
        print(f"    Outputs: {len(report_meta.outputs)}")
        print(f"    Tags: {', '.join(report_meta.tags)}")

    # Example 4: Filter reports
    print("\n" + "="*60)
    print("FILTERING REPORTS")
    print("="*60)

    print("\nAgile reports:")
    for report_meta in registry.filter_by_category("Agile"):
        print(f"  - {report_meta.name}")

    print("\nReports with 'budget' tag:")
    for report_meta in registry.filter_by_tags(["budget"]):
        print(f"  - {report_meta.name}")

    print("\nSearch for 'velocity':")
    for report_meta in registry.search("velocity"):
        print(f"  - {report_meta.name}")

    # Example 5: Dynamic updates
    print("\n" + "="*60)
    print("DYNAMIC UPDATES")
    print("="*60)

    # Update metadata
    update_report_metadata(
        report_id="__main__.generate_velocity_report",
        name="Team Velocity Report (Updated)",
        tags=["velocity", "sprint", "agile", "updated"]
    )

    # Verify update
    updated_report = registry.get("__main__.generate_velocity_report")
    print(f"\nUpdated report name: {updated_report.name}")
    print(f"Updated tags: {', '.join(updated_report.tags)}")

    # Example 6: Hot reload function
    print("\n" + "="*60)
    print("HOT RELOAD")
    print("="*60)

    def new_velocity_implementation(team_id: str, sprint_count: int = 5):
        """New improved velocity calculation"""
        print(
            f"[NEW VERSION] Generating improved velocity report for {team_id}")
        return {"velocity": [15, 18, 20]}, "improved_chart"

    hot_reload_report(
        "__main__.generate_velocity_report",
        new_velocity_implementation
    )

    # Test the hot-reloaded function
    print("\nCalling hot-reloaded function:")
    result = generate_velocity_report("team-123")

    # Example 7: Execute a report from the registry
    print("\n" + "="*60)
    print("EXECUTING REPORTS FROM REGISTRY")
    print("="*60)

    report_meta = registry.get("__main__.generate_budget_report")
    if report_meta:
        print(f"\nExecuting: {report_meta.name}")
        print(
            f"Required inputs: {[inp.name for inp in report_meta.inputs if inp.required]}")

        # Execute the function
        result = report_meta.function(
            budget_id="B-2024-001", date_range="2024-01-01:2024-12-31")
        print(f"Result: {result}")

    # Example 8: Integration with GUI
    print("\n" + "="*60)
    print("GUI INTEGRATION EXAMPLE")
    print("="*60)

    print("\nData structure for GUI:")
    for report_meta in registry.get_all():
        gui_data = {
            "id": report_meta.id,
            "display_name": report_meta.name,
            "description": report_meta.description,
            "category": report_meta.category,
            "tags": report_meta.tags,
            "required_inputs": [
                {"name": inp.name, "type": inp.type,
                    "description": inp.description}
                for inp in report_meta.inputs if inp.required
            ],
            "optional_inputs": [
                {"name": inp.name, "type": inp.type, "default": inp.default}
                for inp in report_meta.inputs if not inp.required
            ],
            "outputs": [
                {"name": out.name, "type": out.type}
                for out in report_meta.outputs
            ]
        }
        print(f"\n{gui_data}")
