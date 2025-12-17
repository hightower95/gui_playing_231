"""
Test Report Configuration Interstitial Dialog

This example demonstrates:
1. Creating a report configuration dialog
2. Setting up inputs and parameters
3. Handling report execution
"""
from productivity_app.productivity_core.tabs.automated_reports.components import ReportConfigDialog
from PySide6.QtWidgets import QApplication
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_simple_dialog():
    """Test a simple report dialog with 2 inputs"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Create dialog matching the Compare Two Parts Lists report
    dialog = ReportConfigDialog(
        report_title="Inventory Reconciliation Report",
        report_description="Compare parts list, inventory data, and BOM to identify discrepancies",
        required_inputs=["Parts List", "Inventory Data"],
        optional_inputs=["Bill of Materials (BOM)"]
    )

    # Connect to report execution signal
    def on_report_executed(title, parameters):
        print(f"\n{'='*60}")
        print(f"✅ Report Executed: {title}")
        print(f"{'='*60}")
        print("\nParameters:")
        for key, value in parameters.items():
            print(f"  {key}: {value}")
        print(f"\n{'='*60}")

    dialog.report_executed.connect(on_report_executed)

    # Show dialog
    dialog.exec()

    print("\nDialog closed")


def test_from_registry():
    """Test opening a dialog for an actual report from the registry"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Import registry and load reports
    from productivity_app.data_pipeline.registry import registry
    from productivity_app.data_pipeline.reports import compare_parts  # Trigger registration

    # Get a report
    report_wrapper = registry.get_report("Compare Two Parts Lists")

    if not report_wrapper:
        print("❌ Report not found in registry")
        return

    print(f"✅ Found report: {report_wrapper.title}")
    print(f"   Description: {report_wrapper.description}")
    print(f"   Inputs: {[str(inp) for inp in report_wrapper.inputs]}")

    # Extract input names for dialog
    required_inputs = []
    for inp in report_wrapper.inputs:
        required_inputs.append(inp.name)

    # Create dialog
    dialog = ReportConfigDialog(
        report_title=report_wrapper.title,
        report_description=report_wrapper.description,
        required_inputs=required_inputs,
        optional_inputs=[]
    )

    # Connect signal
    def on_report_executed(title, parameters):
        print(f"\n{'='*60}")
        print(f"✅ Report Executed: {title}")
        print(f"{'='*60}")
        print("\nParameters:")
        for key, value in parameters.items():
            print(f"  {key}: {value}")

        # Try to actually run the report (would need valid files)
        print(f"\n{'='*60}")
        print("Note: To actually run the report, you need to:")
        print("  1. Select valid CSV files in the dialog")
        print("  2. Click 'Run Report'")
        print("  3. The report.generate() will be called with your inputs")
        print(f"{'='*60}\n")

    dialog.report_executed.connect(on_report_executed)

    # Show dialog
    result = dialog.exec()

    print(f"\nDialog result: {'Accepted' if result else 'Cancelled'}")


def test_all_registry_reports():
    """Show all reports available in the registry"""
    from productivity_app.data_pipeline.registry import registry
    from productivity_app.data_pipeline.reports import compare_parts  # Trigger registration

    all_reports = registry.get_all_reports()

    print(f"\n{'='*60}")
    print(f"Available Reports in Registry: {len(all_reports)}")
    print(f"{'='*60}\n")

    for title, info in all_reports.items():
        print(f"📊 {title}")
        print(f"   Description: {info.get('description', 'N/A')}")
        inputs = info.get('inputs', [])
        if inputs:
            print(f"   Inputs: {', '.join(str(i) for i in inputs)}")
        print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Test Report Configuration Interstitial")
    parser.add_argument('--mode', choices=['simple', 'registry', 'list'],
                        default='simple',
                        help='Test mode: simple (basic dialog), registry (from data_pipeline), list (show all reports)')

    args = parser.parse_args()

    print("\n" + "="*60)
    print("Report Configuration Interstitial Test")
    print("="*60 + "\n")

    if args.mode == 'simple':
        print("Testing simple dialog with mock data...\n")
        test_simple_dialog()
    elif args.mode == 'registry':
        print("Testing dialog with real report from registry...\n")
        test_from_registry()
    elif args.mode == 'list':
        print("Listing all reports in registry...\n")
        test_all_registry_reports()

    print("\n" + "="*60)
    print("Test Complete")
    print("="*60 + "\n")
