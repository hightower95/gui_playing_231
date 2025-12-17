"""
Integration Test: Compare Two CSV Parts Lists

Tests the full end-to-end flow:
1. Create two CSV files with parts
2. Load the comparison report
3. Generate comparison results
4. Verify differences are detected correctly
"""
import pytest
import pandas as pd
from pathlib import Path


@pytest.fixture
def sample_csv_files(tmp_path):
    """Create two CSV files with different parts for testing"""

    # CSV 1: Original parts list
    csv1 = tmp_path / "parts_v1.csv"
    df1 = pd.DataFrame({
        'part_number': ['R001', 'C001', 'D001', 'T001'],
        'part_name': ['Resistor 1K', 'Capacitor 10uF', 'Diode 1N4148', 'Transistor BC547'],
        'quantity': [100, 50, 75, 30]
    })
    df1.to_csv(csv1, index=False)

    # CSV 2: Updated parts list
    # - Removed: D001 (Diode)
    # - Added: L001 (LED)
    # - Modified: R001 quantity changed from 100 to 150
    csv2 = tmp_path / "parts_v2.csv"
    df2 = pd.DataFrame({
        'part_number': ['R001', 'C001', 'T001', 'L001'],
        'part_name': ['Resistor 1K', 'Capacitor 10uF', 'Transistor BC547', 'LED Red 5mm'],
        'quantity': [150, 50, 30, 200]  # R001 quantity changed
    })
    df2.to_csv(csv2, index=False)

    return csv1, csv2


def test_compare_two_csvs_basic(sample_csv_files):
    """Test basic comparison of two CSV parts lists"""

    # Import schema registration (must happen before collectors)
    from productivity_app.data_pipeline.data_sources import parts_list as parts_list_schema

    # Import collectors and reports to register them
    from productivity_app.data_pipeline.data_collectors import csv_to_parts_list
    from productivity_app.data_pipeline.reports import compare_parts
    from productivity_app.data_pipeline.registry import registry

    csv1, csv2 = sample_csv_files

    # Get the comparison report
    report = registry.get_report("Compare Two Parts Lists")
    assert report is not None, "Compare Two Parts Lists report not found"

    # Load both CSVs as Part objects
    old_parts = csv_to_parts_list.csv_to_parts_list_collector(str(csv1))
    new_parts = csv_to_parts_list.csv_to_parts_list_collector(str(csv2))

    # Run the comparison
    result = report.generate(old_parts=old_parts, new_parts=new_parts)

    # Verify results
    assert 'added' in result
    assert 'removed' in result
    assert 'common' in result

    # Check counts
    assert result['added_count'] == 1, "Should have 1 added part (L001)"
    assert result['removed_count'] == 1, "Should have 1 removed part (D001)"
    assert result['common_count'] == 3, "Should have 3 common parts (R001, C001, T001)"

    # Check specific parts
    added_numbers = {p.part_number for p in result['added']}
    removed_numbers = {p.part_number for p in result['removed']}
    common_numbers = {p.part_number for p in result['common']}

    assert 'L001' in added_numbers, "L001 (LED) should be added"
    assert 'D001' in removed_numbers, "D001 (Diode) should be removed"
    assert {'R001', 'C001',
            'T001'} == common_numbers, "R001, C001, T001 should be common"

    print("\n✅ Basic comparison test passed!")
    print(result['summary'])


def test_compare_csvs_with_field_changes(sample_csv_files):
    """Test detailed comparison that detects field-level changes"""

    # Import schema registration
    from productivity_app.data_pipeline.data_sources import parts_list as parts_list_schema

    from productivity_app.data_pipeline.data_collectors import csv_to_parts_list
    from productivity_app.data_pipeline.reports import compare_parts
    from productivity_app.data_pipeline.registry import registry

    csv1, csv2 = sample_csv_files

    # Get detailed comparison report
    report = registry.get_report("Parts Comparison - Detailed")
    assert report is not None, "Parts Comparison - Detailed report not found"

    # Load CSVs
    baseline = csv_to_parts_list.csv_to_parts_list_collector(str(csv1))
    current = csv_to_parts_list.csv_to_parts_list_collector(str(csv2))

    # Run comparison
    result = report.generate(baseline=baseline, current=current)

    # Verify structure
    assert 'added' in result
    assert 'removed' in result
    assert 'modified' in result
    assert 'summary' in result

    # Check modifications (R001 quantity changed)
    modified_part_numbers = [m['part_number'] for m in result['modified']]
    assert 'R001' in modified_part_numbers, "R001 should be modified (quantity changed)"

    # Check specific change in R001
    r001_changes = next(
        (m for m in result['modified'] if m['part_number'] == 'R001'), None)
    assert r001_changes is not None, "Should find R001 in modifications"
    assert 'quantity' in r001_changes['changes'], "Should detect quantity change"

    print("\n✅ Detailed comparison test passed!")
    print(result['summary'])


def test_compare_identical_csvs(tmp_path):
    """Test comparison of identical files shows no differences"""

    # Import schema registration
    from productivity_app.data_pipeline.data_sources import parts_list as parts_list_schema

    from productivity_app.data_pipeline.data_collectors import csv_to_parts_list
    from productivity_app.data_pipeline.reports import compare_parts
    from productivity_app.data_pipeline.registry import registry

    # Create identical CSVs
    df = pd.DataFrame({
        'part_number': ['P001', 'P002'],
        'part_name': ['Part One', 'Part Two'],
        'quantity': [10, 20]
    })

    csv1 = tmp_path / "identical1.csv"
    csv2 = tmp_path / "identical2.csv"
    df.to_csv(csv1, index=False)
    df.to_csv(csv2, index=False)

    # Load and compare
    report = registry.get_report("Compare Two Parts Lists")
    old_parts = csv_to_parts_list.csv_to_parts_list_collector(str(csv1))
    new_parts = csv_to_parts_list.csv_to_parts_list_collector(str(csv2))

    result = report.generate(old_parts=old_parts, new_parts=new_parts)

    # Should have no changes
    assert result['added_count'] == 0, "Identical files should have no additions"
    assert result['removed_count'] == 0, "Identical files should have no removals"
    assert result['common_count'] == 2, "Both parts should be common"

    print("\n✅ Identical files test passed!")


def test_compare_completely_different_csvs(tmp_path):
    """Test comparison where files have no parts in common"""

    # Import schema registration
    from productivity_app.data_pipeline.data_sources import parts_list as parts_list_schema

    from productivity_app.data_pipeline.data_collectors import csv_to_parts_list
    from productivity_app.data_pipeline.reports import compare_parts
    from productivity_app.data_pipeline.registry import registry

    # CSV 1: Set A parts
    csv1 = tmp_path / "set_a.csv"
    df1 = pd.DataFrame({
        'part_number': ['A001', 'A002', 'A003'],
        'part_name': ['Part A1', 'Part A2', 'Part A3']
    })
    df1.to_csv(csv1, index=False)

    # CSV 2: Set B parts (completely different)
    csv2 = tmp_path / "set_b.csv"
    df2 = pd.DataFrame({
        'part_number': ['B001', 'B002'],
        'part_name': ['Part B1', 'Part B2']
    })
    df2.to_csv(csv2, index=False)

    # Load and compare
    report = registry.get_report("Compare Two Parts Lists")
    old_parts = csv_to_parts_list.csv_to_parts_list_collector(str(csv1))
    new_parts = csv_to_parts_list.csv_to_parts_list_collector(str(csv2))

    result = report.generate(old_parts=old_parts, new_parts=new_parts)

    # Should have all parts as added/removed, none common
    assert result['added_count'] == 2, "All parts from CSV2 should be added"
    assert result['removed_count'] == 3, "All parts from CSV1 should be removed"
    assert result['common_count'] == 0, "No parts should be common"

    print("\n✅ Completely different files test passed!")


if __name__ == "__main__":
    # Run tests manually
    import tempfile

    print("="*70)
    print("INTEGRATION TEST: Compare Two CSV Parts Lists")
    print("="*70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create fixtures
        csv1 = tmp_path / "parts_v1.csv"
        df1 = pd.DataFrame({
            'part_number': ['R001', 'C001', 'D001', 'T001'],
            'part_name': ['Resistor 1K', 'Capacitor 10uF', 'Diode 1N4148', 'Transistor BC547'],
            'quantity': [100, 50, 75, 30]
        })
        df1.to_csv(csv1, index=False)

        csv2 = tmp_path / "parts_v2.csv"
        df2 = pd.DataFrame({
            'part_number': ['R001', 'C001', 'T001', 'L001'],
            'part_name': ['Resistor 1K', 'Capacitor 10uF', 'Transistor BC547', 'LED Red 5mm'],
            'quantity': [150, 50, 30, 200]
        })
        df2.to_csv(csv2, index=False)

        sample_files = (csv1, csv2)

        print("\n1. Testing basic comparison...")
        test_compare_two_csvs_basic(sample_files)

        print("\n2. Testing detailed comparison with field changes...")
        test_compare_csvs_with_field_changes(sample_files)

        print("\n3. Testing identical files...")
        test_compare_identical_csvs(tmp_path)

        print("\n4. Testing completely different files...")
        test_compare_completely_different_csvs(tmp_path)

    print("\n" + "="*70)
    print("✅ ALL INTEGRATION TESTS PASSED!")
    print("="*70)
    print("\n🎉 You CAN compare two CSV parts lists!")
    print("📝 See: productivity_app/data_pipeline/reports/compare_parts.py")
