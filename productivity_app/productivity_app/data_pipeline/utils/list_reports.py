"""
Utility: List all registered reports and their parameters

Run directly from IDE or command line to see all available reports.
"""
from productivity_app.data_pipeline.registry import registry


def list_reports():
    """List all registered reports with their parameters"""
    print("=" * 80)
    print("REGISTERED REPORTS")
    print("=" * 80)

    reports = registry.get_all_reports()

    if not reports:
        print("\n⚠️  No reports registered yet.")
        print("\nTip: Import report modules to register them:")
        print("  from productivity_app.data_pipeline.reports import csv_columns")
        return

    for i, (title, report_info) in enumerate(reports.items(), 1):
        print(f"\n{i}. {title}")
        print(f"   Description: {report_info.get('description', 'N/A')}")

        inputs = report_info.get('inputs', [])
        if inputs:
            print(f"   Parameters ({len(inputs)}):")
            for param in inputs:
                if hasattr(param, 'name'):
                    param_type = type(param).__name__
                    required = "required" if getattr(
                        param, 'required', True) else "optional"
                    description = getattr(param, 'description', '')
                    print(f"     • {param.name} ({param_type}, {required})")
                    if description:
                        print(f"       {description}")
                else:
                    print(f"     • {param}")
        else:
            print("   Parameters: None")

    print("\n" + "=" * 80)
    print(f"Total Reports: {len(reports)}")
    print("=" * 80)


if __name__ == "__main__":
    # Auto-import common reports
    try:
        from productivity_app.data_pipeline.reports import csv_columns
        print("✓ Loaded: csv_columns")
    except ImportError as e:
        print(f"⚠️  Could not load csv_columns: {e}")

    try:
        from productivity_app.data_pipeline.reports import parts_summary_example
        print("✓ Loaded: parts_summary_example")
    except ImportError as e:
        print(f"⚠️  Could not load parts_summary_example: {e}")

    print()
    list_reports()
