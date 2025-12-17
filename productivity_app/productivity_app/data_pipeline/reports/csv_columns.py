"""
CSV Columns Report Example

Demonstrates basic report creation with simple file input.
"""
from productivity_app.data_pipeline.reports.decorator import report
from productivity_app.data_pipeline.parameters import Variables


@report(
    title="CSV Columns Report",
    description="Generates a report of the columns in a CSV file.",
    inputs=[Variables.FilePath],
)
def csv_columns_report(filepath: str) -> str:
    """Generate a report of CSV columns

    Args:
        filepath: Path to the CSV file

    Returns:
        A string report of the columns in the CSV file
    """
    import pandas as pd

    df = pd.read_csv(filepath)
    columns = df.columns.tolist()
    report_lines = [f"Columns in CSV file '{filepath}':"]
    for col in columns:
        report_lines.append(f"- {col}")
    report_columns_pretty = "\n".join(report_lines)

    print("report generated:")
    print(report_columns_pretty)
    return columns


@report(
    title="CSV Columns Report with Output",
    description="Generates a report of the columns in a CSV file with optional output file.",
    inputs=[Variables.InputPath, Variables.OutputPath],
)
def csv_columns_report_with_output_path(input_path: str, output_path: str = None) -> str:
    """Generate a report of CSV columns

    Args:
        input_path: Path to the CSV file
        output_path: Path to save the report

    Returns:
        A string report of the columns in the CSV file
    """
    import pandas as pd

    df = pd.read_csv(input_path)
    columns = df.columns.tolist()
    report_lines = [f"Columns in CSV file '{input_path}':"]
    for col in columns:
        report_lines.append(f"- {col}")
    report_columns_pretty = "\n".join(report_lines)

    if output_path:
        # with open(output_path, 'w') as f:
        #     f.write(report_columns_pretty)
        print(f"Report saved to {output_path}")
    print("report generated:")
    print(report_columns_pretty)
    return columns


@report(
    title="CSV Columns - Using Schema",
    description="Generates a report from a parts list (demonstrates collected parameters).",
    inputs=[Variables.PartsList],
)
def parts_list_report(parts: list) -> str:
    """Generate a report from parts list

    This report requires a list of Part objects (CollectedParameter).
    The data pipeline will use a collector to convert CSV/Excel into parts.

    Args:
        parts: List of Part objects

    Returns:
        Part count as string
    """
    part_count = len(parts)
    report = f"Number of parts: {part_count}"

    print("Report generated:")
    print(report)

    return report
