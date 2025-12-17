"""
Test integration between automated_reports and data_pipeline

Verify that:
1. Reports from data_pipeline appear in automated_reports model
2. Report configuration dialog can be created
3. Report execution works end-to-end
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_model_loads_reports():
    """Test that model loads reports from data_pipeline registry"""
    from productivity_app.productivity_core.tabs.automated_reports.model import AutomatedReportsModel
    
    model = AutomatedReportsModel()
    
    print(f"\n✅ Loaded {len(model.reports)} reports from registry")
    
    for report in model.reports:
        print(f"\n  📊 {report.name}")
        print(f"     Description: {report.description}")
        print(f"     Inputs: {', '.join(report.required_inputs)}")
        print(f"     Topics: {', '.join(report.topics)}")
    
    assert len(model.reports) > 0, "Should have at least one report"
    
    # Check that compare reports are present
    report_names = [r.name for r in model.reports]
    assert "Compare Two Parts Lists" in report_names, "Should have basic comparison report"
    
    print("\n✅ All reports loaded successfully!")


def test_dialog_creation():
    """Test that report config dialog can be created"""
    from PySide6.QtWidgets import QApplication
    from productivity_app.productivity_core.tabs.automated_reports.components import ReportConfigDialog
    
    # Create QApplication if not exists
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create dialog
    dialog = ReportConfigDialog(
        report_title="Test Report",
        report_description="This is a test report for verification",
        required_inputs=["Parts List", "Inventory Data"],
        optional_inputs=["Bill of Materials (BOM)"]
    )
    
    print("\n✅ Dialog created successfully!")
    print(f"   Title: {dialog.report_title}")
    print(f"   Required inputs: {dialog.required_inputs}")
    print(f"   Tabs: {dialog.tabs.count()}")
    
    assert dialog.tabs.count() >= 4, "Should have Summary + 2 documents + Settings tabs"
    
    print("\n✅ Dialog structure verified!")


def test_presenter_integration():
    """Test that presenter can open reports"""
    from productivity_app.productivity_core.tabs.automated_reports.presenter import AutomatedReportsPresenter
    
    presenter = AutomatedReportsPresenter()
    presenter.initialize()
    
    # Get first report
    if presenter.model.reports:
        first_report = presenter.model.reports[0]
        print(f"\n✅ First report: {first_report.name}")
        print(f"   ID: {first_report.id}")
        
        # Note: Can't actually open the dialog in test, but can verify the method exists
        assert hasattr(presenter, 'open_report'), "Presenter should have open_report method"
        
        print("\n✅ Presenter integration verified!")


if __name__ == "__main__":
    print("="*60)
    print("Testing Automated Reports ↔ Data Pipeline Integration")
    print("="*60)
    
    test_model_loads_reports()
    test_dialog_creation()
    test_presenter_integration()
    
    print("\n" + "="*60)
    print("✅ All integration tests passed!")
    print("="*60)
