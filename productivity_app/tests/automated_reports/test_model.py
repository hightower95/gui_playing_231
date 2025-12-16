"""
Tests for AutomatedReportsModel

Tests:
- Report generation
- Filter operations (single and multi-dimension)
- Search functionality
- Sort operations
- Data extraction (projects, types, etc.)
- Topic hierarchy generation
"""
import pytest
from productivity_app.productivity_core.tabs.automated_reports.model import AutomatedReportsModel, ReportMetadata


class TestReportGeneration:
    """Test report data generation"""

    def test_generates_correct_count(self):
        """Model should generate requested number of reports"""
        model = AutomatedReportsModel()
        # Default is 15 reports
        assert len(model.get_all_reports()) == 15

    def test_generates_valid_metadata(self):
        """Each generated report should have valid metadata"""
        model = AutomatedReportsModel()
        reports = model.get_all_reports()

        for report in reports:
            assert report.id, "Report must have ID"
            assert report.name, "Report must have name"
            assert report.description, "Report must have description"
            assert report.project, "Report must have project"
            assert report.report_type, "Report must have type"
            assert report.scope, "Report must have scope"
            assert isinstance(report.required_inputs,
                              list), "Inputs must be list"
            assert isinstance(report.topics, list), "Topics must be list"

    def test_reports_have_unique_ids(self):
        """All reports should have unique IDs"""
        model = AutomatedReportsModel()
        reports = model.get_all_reports()
        ids = [r.id for r in reports]
        assert len(ids) == len(set(ids)), "Report IDs must be unique"


class TestFilterOperations:
    """Test filtering functionality"""

    def test_filter_by_project_single(self):
        """Filter by single project should reduce results"""
        model = AutomatedReportsModel()
        all_reports = model.get_all_reports()

        # Get a project that exists
        test_project = all_reports[0].project

        filtered = model.filter_reports(project=[test_project])

        assert len(filtered) < len(
            all_reports) or len(filtered) == len(all_reports)
        assert all(r.project == test_project for r in filtered)

    def test_filter_by_project_multiple(self):
        """Filter by multiple projects uses OR logic"""
        model = AutomatedReportsModel()
        all_reports = model.get_all_reports()

        # Get two different projects
        projects = list(set(r.project for r in all_reports))[:2]

        filtered = model.filter_reports(project=projects)

        assert all(r.project in projects for r in filtered)
        # Should have reports from both projects
        assert len(filtered) > 0

    def test_filter_by_report_type(self):
        """Filter by report type should only return matching types"""
        model = AutomatedReportsModel()
        all_reports = model.get_all_reports()

        # Get a report type that exists
        test_type = all_reports[0].report_type

        filtered = model.filter_reports(report_type=[test_type])

        assert all(r.report_type == test_type for r in filtered)
        assert len(filtered) > 0

    def test_filter_by_scope_case_insensitive(self):
        """Scope filter should be case-insensitive"""
        model = AutomatedReportsModel()

        filtered_lower = model.filter_reports(scope=["local"])
        filtered_upper = model.filter_reports(scope=["LOCAL"])
        filtered_mixed = model.filter_reports(scope=["Local"])

        assert len(filtered_lower) == len(
            filtered_upper) == len(filtered_mixed)

    def test_filter_by_topics(self):
        """Filter by topics should return reports with matching topics"""
        model = AutomatedReportsModel()
        all_reports = model.get_all_reports()

        # Get a topic that exists
        test_topic = None
        for report in all_reports:
            if report.topics:
                test_topic = report.topics[0]
                break

        if test_topic:
            filtered = model.filter_reports(topics=[test_topic])

            assert all(test_topic in r.topics for r in filtered)
            assert len(filtered) > 0

    def test_filter_by_multiple_dimensions(self):
        """Multiple filters should use AND logic between dimensions"""
        model = AutomatedReportsModel()
        all_reports = model.get_all_reports()

        # Get test values
        test_project = all_reports[0].project
        test_type = all_reports[0].report_type

        # Filter by both
        filtered = model.filter_reports(
            project=[test_project],
            report_type=[test_type]
        )

        # All results must match BOTH filters
        assert all(r.project == test_project and r.report_type ==
                   test_type for r in filtered)

    def test_filter_reduces_count_appropriately(self):
        """With 15 reports, specific filters should reduce count"""
        model = AutomatedReportsModel()
        all_reports = model.get_all_reports()

        # Get project with fewer reports
        project_counts = {}
        for r in all_reports:
            project_counts[r.project] = project_counts.get(r.project, 0) + 1

        # Pick project that doesn't have all reports
        test_project = min(project_counts.keys(),
                           key=lambda k: project_counts[k])

        filtered = model.filter_reports(project=[test_project])

        assert len(filtered) < len(all_reports)
        assert len(filtered) == project_counts[test_project]

    def test_filter_with_no_matches_returns_empty(self):
        """Filter with impossible criteria should return empty list"""
        model = AutomatedReportsModel()

        # Use a project that doesn't exist
        filtered = model.filter_reports(project=["NonexistentProject9999"])

        assert len(filtered) == 0
        assert filtered == []


class TestSearchFunctionality:
    """Test search text filtering"""

    def test_search_by_name(self):
        """Search should match report names"""
        model = AutomatedReportsModel()
        all_reports = model.get_all_reports()

        # Get a word from a report name
        test_name = all_reports[0].name
        search_term = test_name.split()[0]  # First word

        filtered = model.filter_reports(search_text=search_term)

        assert len(filtered) > 0
        assert any(search_term.lower() in r.name.lower() for r in filtered)

    def test_search_by_description(self):
        """Search should match report descriptions"""
        model = AutomatedReportsModel()
        all_reports = model.get_all_reports()

        # Get a word from a description
        test_desc = all_reports[0].description
        search_term = test_desc.split()[0]  # First word

        filtered = model.filter_reports(search_text=search_term)

        assert len(filtered) > 0
        assert any(search_term.lower() in r.description.lower()
                   for r in filtered)

    def test_search_case_insensitive(self):
        """Search should be case-insensitive"""
        model = AutomatedReportsModel()
        all_reports = model.get_all_reports()

        search_term = all_reports[0].name.split()[0]

        filtered_lower = model.filter_reports(search_text=search_term.lower())
        filtered_upper = model.filter_reports(search_text=search_term.upper())

        assert len(filtered_lower) == len(filtered_upper)

    def test_search_with_filters(self):
        """Search can be combined with other filters"""
        model = AutomatedReportsModel()
        all_reports = model.get_all_reports()

        test_project = all_reports[0].project
        search_term = "Report"

        filtered = model.filter_reports(
            project=[test_project],
            search_text=search_term
        )

        # All results must match both project AND search
        assert all(r.project == test_project for r in filtered)
        assert all(search_term.lower() in r.name.lower() or
                   search_term.lower() in r.description.lower()
                   for r in filtered)


class TestSortOperations:
    """Test sorting functionality"""

    def test_sort_by_name_ascending(self):
        """Sort by name should order alphabetically"""
        model = AutomatedReportsModel()
        reports = model.get_all_reports()

        sorted_reports = model.sort_reports(reports, sort_by='name')

        names = [r.name.lower() for r in sorted_reports]
        assert names == sorted(names)

    def test_sort_by_name_descending(self):
        """Sort by name descending should reverse order"""
        model = AutomatedReportsModel()
        reports = model.get_all_reports()

        sorted_reports = model.sort_reports(
            reports, sort_by='name', ascending=False)

        names = [r.name.lower() for r in sorted_reports]
        assert names == sorted(names, reverse=True)

    def test_sort_by_type(self):
        """Sort by type should group same types together"""
        model = AutomatedReportsModel()
        reports = model.get_all_reports()

        sorted_reports = model.sort_reports(reports, sort_by='type')

        types = [r.report_type for r in sorted_reports]
        # Check that same types are grouped together
        for i in range(len(types) - 1):
            if types[i] == types[i + 1]:
                continue
            # If type changed, all subsequent should be >= current
            assert all(t >= types[i] for t in types[i + 1:])

    def test_sort_by_project(self):
        """Sort by project should group same projects together"""
        model = AutomatedReportsModel()
        reports = model.get_all_reports()

        sorted_reports = model.sort_reports(reports, sort_by='project')

        projects = [r.project for r in sorted_reports]
        # Check that same projects are grouped together
        for i in range(len(projects) - 1):
            if projects[i] == projects[i + 1]:
                continue
            # If project changed, all subsequent should be >= current
            assert all(p >= projects[i] for p in projects[i + 1:])

    def test_sort_preserves_count(self):
        """Sorting should not change number of reports"""
        model = AutomatedReportsModel()
        reports = model.get_all_reports()

        sorted_reports = model.sort_reports(reports, sort_by='name')

        assert len(sorted_reports) == len(reports)


class TestDataExtraction:
    """Test getter methods for unique values"""

    def test_get_projects_returns_unique(self):
        """Should return list of unique projects"""
        model = AutomatedReportsModel()
        projects = model.get_projects()

        assert len(projects) == len(set(projects))
        assert all(isinstance(p, str) for p in projects)

    def test_get_report_types_returns_unique(self):
        """Should return sorted list of unique report types"""
        model = AutomatedReportsModel()
        types = model.get_report_types()

        assert len(types) == len(set(types))
        assert types == sorted(types)

    def test_get_scopes_returns_unique(self):
        """Should return sorted list of unique scopes"""
        model = AutomatedReportsModel()
        scopes = model.get_scopes()

        assert len(scopes) == len(set(scopes))
        assert scopes == sorted(scopes)

    def test_get_required_inputs_returns_unique(self):
        """Should return sorted list of all unique inputs"""
        model = AutomatedReportsModel()
        inputs = model.get_required_inputs()

        assert len(inputs) == len(set(inputs))
        assert inputs == sorted(inputs)
        assert all(isinstance(i, str) for i in inputs)


class TestTopicHierarchy:
    """Test topic hierarchy generation"""

    def test_hierarchy_includes_all_reports(self):
        """'All Reports' should have count of all reports"""
        model = AutomatedReportsModel()
        hierarchy = model.get_topic_hierarchy()

        all_reports_entry = hierarchy[0]
        assert all_reports_entry[0] == "All Reports"
        assert all_reports_entry[1] == len(model.get_all_reports())

    def test_hierarchy_structure_format(self):
        """Each hierarchy entry should be (name, count, children)"""
        model = AutomatedReportsModel()
        hierarchy = model.get_topic_hierarchy()

        for entry in hierarchy:
            assert len(entry) == 3
            name, count, children = entry
            assert isinstance(name, str)
            assert isinstance(count, int)
            assert children is None or isinstance(children, list)

    def test_folder_counts_match_children(self):
        """Folder counts should sum their children"""
        model = AutomatedReportsModel()
        hierarchy = model.get_topic_hierarchy()

        for entry in hierarchy[1:]:  # Skip "All Reports"
            name, count, children = entry
            if children:
                child_sum = sum(child[1] for child in children)
                # Folder count should be >= sum of children
                # (reports can have multiple topics)
                assert count >= child_sum or count == child_sum


class TestIntegrationScenarios:
    """Test realistic usage scenarios"""

    def test_filter_then_sort(self):
        """Should be able to filter then sort results"""
        model = AutomatedReportsModel()
        all_reports = model.get_all_reports()

        test_project = all_reports[0].project

        # Filter first
        filtered = model.filter_reports(project=[test_project])

        # Then sort
        sorted_filtered = model.sort_reports(filtered, sort_by='name')

        # Should have same count
        assert len(sorted_filtered) == len(filtered)

        # Should be sorted
        names = [r.name.lower() for r in sorted_filtered]
        assert names == sorted(names)

        # Should still be filtered
        assert all(r.project == test_project for r in sorted_filtered)

    def test_multiple_filters_reduce_count_correctly(self):
        """Multiple filters should progressively reduce results"""
        model = AutomatedReportsModel()
        all_reports = model.get_all_reports()

        # No filter
        assert len(all_reports) == 15

        # One filter
        test_project = all_reports[0].project
        filtered_one = model.filter_reports(project=[test_project])
        assert len(filtered_one) <= len(all_reports)

        # Two filters
        test_type = all_reports[0].report_type
        filtered_two = model.filter_reports(
            project=[test_project],
            report_type=[test_type]
        )
        assert len(filtered_two) <= len(filtered_one)

    def test_ten_reports_with_filters(self):
        """With generated reports, specific filters reduce count appropriately"""
        # Create model with exactly 10 reports
        model = AutomatedReportsModel()
        model.reports = model._generate_fake_reports(10)

        all_reports = model.get_all_reports()
        assert len(all_reports) == 10

        # Count by project
        project_counts = {}
        for r in all_reports:
            project_counts[r.project] = project_counts.get(r.project, 0) + 1

        # Filter by specific project
        for project, expected_count in project_counts.items():
            filtered = model.filter_reports(project=[project])
            assert len(filtered) == expected_count
            assert all(r.project == project for r in filtered)

        # Count by type
        type_counts = {}
        for r in all_reports:
            type_counts[r.report_type] = type_counts.get(r.report_type, 0) + 1

        # Filter by specific type
        for report_type, expected_count in type_counts.items():
            filtered = model.filter_reports(report_type=[report_type])
            assert len(filtered) == expected_count
            assert all(r.report_type == report_type for r in filtered)

    def test_progressive_filtering_scenario(self):
        """Real-world scenario: user progressively adds filters"""
        model = AutomatedReportsModel()
        all_reports = model.get_all_reports()
        initial_count = len(all_reports)

        # Step 1: User selects a project
        projects = model.get_projects()
        filtered_1 = model.filter_reports(project=[projects[0]])
        assert len(filtered_1) <= initial_count

        # Step 2: User adds a type filter
        types = model.get_report_types()
        filtered_2 = model.filter_reports(
            project=[projects[0]],
            report_type=[types[0]]
        )
        assert len(filtered_2) <= len(filtered_1)

        # Step 3: User adds search text
        filtered_3 = model.filter_reports(
            project=[projects[0]],
            report_type=[types[0]],
            search_text="Report"
        )
        assert len(filtered_3) <= len(filtered_2)

        # Final results should still match all criteria
        for report in filtered_3:
            assert report.project == projects[0]
            assert report.report_type == types[0]
            assert ("report" in report.name.lower() or
                    "report" in report.description.lower())
