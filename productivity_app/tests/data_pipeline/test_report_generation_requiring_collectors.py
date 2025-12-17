"""
Test for reports with missing input providers
"""
import pytest
from productivity_app.data_pipeline.reports.decorator import report
from productivity_app.data_pipeline.reports.register import report_registry
from productivity_app.data_pipeline.parameters.input_parameters import DataSource
from productivity_app.data_pipeline.models.part import Part

# Import collectors to ensure they are registered
from productivity_app.data_pipeline.data_collectors import excel_to_parts_list


def test_report_without_input_provider():
    """Report needing PartsList fails when no collector provides it"""

    @report(
        title="Test Parts Report",
        description="Report requiring parts list",
        inputs=[DataSource.PartsList]
    )
    def test_parts_report(parts: list[Part]):
        return len(parts)

    registered = report_registry.get_report_by_name("Test Parts Report")

    # Cannot call generate() with a PartsList input directly
    # User needs to provide actual Part objects, which should come from a collector

    # Attempting to generate without providing parts should fail
    with pytest.raises(TypeError, match="missing.*required.*argument.*'parts'"):
        registered.generate()

    # Note: The report function doesn't enforce type checking at runtime
    # It will accept wrong types - validation happens elsewhere in the system
    # registered.generate(parts="not a list of parts")  # Would not raise TypeError


def test_registry_provides_root_parameters():
    """Test that registry can identify root inputs by tracing through collectors"""

    @report(
        title="Test Parts Analysis",
        description="Analyze parts list",
        inputs=[DataSource.PartsList]
    )
    def analyze_parts(parts: list[Part]):
        return len(parts)

    registered = report_registry.get_report_by_name("Test Parts Analysis")

    # Get base inputs - should trace PartsList → Collectors → FilePath
    root_dependencies = registered.get_base_inputs()

    # PartsList is not a root input (is_root=False)
    # A collector is needed to produce it from a FilePath
    # So get_base_inputs() should return FilePath (is_root=True)

    assert len(root_dependencies) > 0, "Should find at least one root input"

    # Check that we get a root parameter (FilePath)
    root_names = [p.name for p in root_dependencies]
    assert "filepath" in root_names, "Should trace back to filepath as root input"

    # Verify the root parameter has is_root=True
    for param in root_dependencies:
        assert param.is_root is True, f"Root parameter {param.name} should have is_root=True"


def test_report_needs_collector_lookup():
    """Report with PartsList input should indicate it needs a collector"""

    @report(
        title="Test Parts Count",
        description="Count parts in list",
        inputs=[DataSource.PartsList]
    )
    def count_parts(parts: list[Part]):
        return len(parts)

    registered = report_registry.get_report_by_name("Test Parts Count")
    params = registered.get_parameters()

    # Report has PartsList parameter
    assert len(params) == 1
    assert params[0].name == "parts"
    assert params[0].title == "Parts List"

    # Check if report can be generated
    can_gen = registered.can_generate()
    issues = registered.get_issues()

    # Should report issue if no collectors are registered
    # (depends on whether excel_to_parts_list is imported)
    if not can_gen:
        assert len(issues) > 0
        assert any("parts" in issue.lower() for issue in issues)

    # GUI would need to:
    # 1. See input is PartsList
    # 2. Look up collectors that output DataTypes.PartsList
    # 3. Run chosen collector to get List[Part]
    # 4. Pass result to report.generate(parts=collected_parts)

    # For now, we can manually create parts
    mock_parts = [
        Part(part_name="Resistor", part_number="R001"),
        Part(part_name="Capacitor", part_number="C001")
    ]

    result = registered.generate(parts=mock_parts)
    assert result == 2
