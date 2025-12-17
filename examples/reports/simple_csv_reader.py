from productivity_app.data_pipeline import reports


report = reports.get_report_by_name("CSV Columns Report")

report.generate(
    filepath="examples\\reports\\data\\simple_data.csv"
)


# Print dependency tree
print(report.get_dependency_tree())
# Output:
# CSV Columns Report
#       Input: filepath

# Get parameters list
params = report.get_parameters()
print(params)  # [DataSource.FilePath]
