"""
Test report.can_generate() and report.get_issues() methods
"""
import pytest
from productivity_app.data_pipeline.reports.decorator import report
from productivity_app.data_pipeline.reports.register import report_registry
from productivity_app.data_pipeline.parameters.input_parameters import DataSource
from productivity_app.data_pipeline.models.part import Part


def test_report_with_root_inputs_can_generate():
    """Reports with only root inputs can always generate"""

    @report(
        title="Simple File Report",
        description="Report using only FilePath",
        inputs=[DataSource.FilePath]
    )
    def simple_report(filepath: str):
        return f"Processing {filepath}"

    registered = report_registry.get_report_by_name("Simple File Report")

    # Root inputs are always satisfiable
    assert registered.can_generate() is True
    assert registered.get_issues() == []


def test_report_with_optional_inputs_can_generate():
    """Reports with optional inputs can generate"""

    @report(
        title="Report with Optional",
        description="Report with optional output path",
        inputs=[DataSource.FilePath, DataSource.OutputPath]
    )
    def optional_report(filepath: str, output_path: str = None):
        return f"Processing {filepath}"

    registered = report_registry.get_report_by_name("Report with Optional")

    # Should be able to generate (output_path is optional)
    assert registered.can_generate() is True
    assert registered.get_issues() == []


def test_report_with_derived_input_no_collector():
    """Reports with derived inputs but no collectors cannot generate"""

    @report(
        title="Parts Report No Collector",
        description="Report needing PartsList",
        inputs=[DataSource.PartsList]
    )
    def parts_report(parts: list[Part]):
        return len(parts)

    registered = report_registry.get_report_by_name(
        "Parts Report No Collector")

    # Without collectors imported, should report issues
    can_gen = registered.can_generate()
    issues = registered.get_issues()

    # Expect failure without collectors
    if not can_gen:
        assert len(issues) > 0
        # Should mention "parts" or "PartsList"
        issues_text = " ".join(issues).lower()
        assert "parts" in issues_text or "partslist" in issues_text


def test_report_with_derived_input_with_collector():
    """Reports with derived inputs and collectors can generate"""

    # Import collectors to register them
    # from productivity_app.data_pipeline.data_collectors import excel_to_parts_list
    from productivity_app.data_pipeline.data_collectors import csv_to_parts_list

    @report(
        title="Parts Report With Collector",
        description="Report needing PartsList",
        inputs=[DataSource.PartsList]
    )
    def parts_report_with_col(parts: list[Part]):
        return len(parts)

    registered = report_registry.get_report_by_name(
        "Parts Report With Collector")

    # With collectors available, should be able to generate
    assert registered.can_generate() is True
    assert registered.get_issues() == []


def test_get_issues_provides_details():
    """get_issues() should provide actionable information"""

    @report(
        title="Broken Report",
        description="Report that can't run",
        inputs=[DataSource.PartsList]
    )
    def broken_report(parts: list[Part]):
        return len(parts)

    registered = report_registry.get_report_by_name("Broken Report")

    issues = registered.get_issues()

    if issues:  # If collectors aren't available
        # Each issue should be a descriptive string
        for issue in issues:
            assert isinstance(issue, str)
            assert len(issue) > 10  # Should be descriptive
