from productivity_app.data_pipeline import reports


all_reports = reports.get_all_reports()
print("Available Reports:")
for report in all_reports:
    print(f"- {report.title}: {report.description}")

    # Print dependency tree
    print(report.get_dependency_tree())

    # Get parameters list
    params = report.get_parameters()
    print(params)  # [DataSource.FilePath]
