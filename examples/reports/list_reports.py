"""
List all registered reports

Example showing how to discover and inspect available reports.
"""
from productivity_app.data_pipeline import reports

# Get all registered reports
all_reports = reports.get_all_reports()

print("=" * 80)
print("AVAILABLE REPORTS")
print("=" * 80)

if not all_reports:
    print("\nNo reports registered yet.")
    print("Import report modules to register them.")
else:
    for i, report in enumerate(all_reports, 1):
        print(f"\n{i}. {report.title}")
        print(f"   Description: {report.description}")

        # Get parameters
        params = report.get_parameters()
        required_params = report.get_required_parameters()
        optional_params = report.get_optional_parameters()

        print(f"\n   This report requires:")
        if required_params:
            for param in required_params:
                param_name = getattr(param, 'name', str(param))
                param_title = getattr(param, 'title', param_name)
                param_type = type(param).__name__
                print(f"     • {param_title} ({param_name}) - {param_type}")
        else:
            print("     • No required parameters")

        if optional_params:
            print(f"\n   Optional parameters:")
            for param in optional_params:
                param_name = getattr(param, 'name', str(param))
                param_title = getattr(param, 'title', param_name)
                param_type = type(param).__name__
                print(f"     • {param_title} ({param_name}) - {param_type}")

        # Check if report can be generated
        issues = report.get_issues()
        if issues:
            print(f"\n   ⚠️  Issues:")
            for issue in issues:
                print(f"     • {issue}")
        else:
            print(f"\n   ✅ Ready to generate")

        # Show dependency tree
        print(f"\n   Dependency tree:")
        tree = report.get_dependency_tree()
        for line in tree.split('\n'):
            print(f"     {line}")

print("\n" + "=" * 80)
print(f"Total Reports: {len(all_reports)}")
print("=" * 80)
