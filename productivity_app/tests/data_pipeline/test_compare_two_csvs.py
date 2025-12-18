"""
Quick Test: Can we compare two CSV parts lists?

This test verifies the full pipeline works for comparing CSVs.
"""
import pytest
import pandas as pd
from pathlib import Path


def test_compare_two_csv_parts_lists_end_to_end(tmp_path):
    """Verify we can compare two CSV files with parts"""

    # Import to register collectors and reports
    from productivity_app.data_pipeline.parameters.resolution import resolve_parts_list_from_file
    from productivity_app.data_pipeline.reports import compare_parts
    from productivity_app.data_pipeline.registry import registry

    # Create two test CSV files
    csv1 = tmp_path / "parts_v1.csv"
    csv2 = tmp_path / "parts_v2.csv"

    # Version 1: 3 parts
    df1 = pd.DataFrame({
        'part_number': ['P001', 'P002', 'P003'],
        'part_name': ['Resistor', 'Capacitor', 'Diode'],
        'quantity': [100, 50, 25]
    })
    df1.to_csv(csv1, index=False)

    # Version 2: Removed P002, Added P004, Modified P001 quantity
    df2 = pd.DataFrame({
        'part_number': ['P001', 'P003', 'P004'],
        'part_name': ['Resistor', 'Diode', 'Transistor'],
        'quantity': [150, 25, 75]  # P001 quantity changed
    })
    df2.to_csv(csv2, index=False)

    # Get the comparison report
    report = registry.get_report("Compare Two Parts Lists")

    assert report is not None, "Compare Two Parts Lists report not found"

    # Generate comparison using parameter resolution
    result = report.generate(
        old_parts=resolve_parts_list_from_file(str(csv1)),
        new_parts=resolve_parts_list_from_file(str(csv2))
    )

    # Verify results
    assert result['added_count'] == 1, "Should have 1 added part (P004)"
    assert result['removed_count'] == 1, "Should have 1 removed part (P002)"
    assert result['common_count'] == 2, "Should have 2 common parts (P001, P003)"

    # Check specific parts
    added_numbers = [p.part_number for p in result['added']]
    removed_numbers = [p.part_number for p in result['removed']]

    assert 'P004' in added_numbers, "P004 should be in added"
    assert 'P002' in removed_numbers, "P002 should be in removed"

    print("✅ CSV comparison test passed!")
    print(result['summary'])


def test_detailed_comparison_with_field_changes(tmp_path):
    """Test detailed comparison that detects field-level changes"""

    from productivity_app.data_pipeline.parameters.resolution import resolve_parts_list_from_file
    from productivity_app.data_pipeline.reports import compare_parts
    from productivity_app.data_pipeline.registry import registry

    csv1 = tmp_path / "baseline.csv"
    csv2 = tmp_path / "current.csv"

    # Baseline
    df1 = pd.DataFrame({
        'part_number': ['A001', 'A002'],
        'part_name': ['Widget', 'Gadget'],
        'quantity': [10, 20]
    })
    df1.to_csv(csv1, index=False)

    # Current - changed Widget name
    df2 = pd.DataFrame({
        'part_number': ['A001', 'A002'],
        'part_name': ['Super Widget', 'Gadget'],  # A001 name changed
        'quantity': [10, 30]  # A002 quantity changed
    })
    df2.to_csv(csv2, index=False)

    # Get detailed comparison report
    report = registry.get_report("Parts Comparison - Detailed")

    # Run comparison
    result = report['func'](
        baseline=resolve_parts_list_from_file(str(csv1)),
        current=resolve_parts_list_from_file(str(csv2))
    )

    # Should detect modifications
    assert len(result['modified']) > 0, "Should detect modified parts"

    # Check for A001 name change
    modified_a001 = [m for m in result['modified']
                     if m['part_number'] == 'A001']
    assert len(modified_a001) == 1, "A001 should be modified"
    assert 'part_name' in modified_a001[0]['changes'], "Should detect name change"

    print("✅ Detailed comparison test passed!")
    print(result['summary'])


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        print("Running basic comparison test...")
        test_compare_two_csv_parts_lists_end_to_end(tmp_path)

        print("\nRunning detailed comparison test...")
        test_detailed_comparison_with_field_changes(tmp_path)

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\n🎉 You CAN compare two CSV parts lists!")
        print("📝 See: productivity_app/data_pipeline/reports/compare_parts.py")
