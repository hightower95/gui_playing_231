

from productivity_app.data_pipeline.models.part import Part
from productivity_app.data_pipeline.reports.decorator import report
from productivity_app.data_pipeline.parameters.input_parameters import DataSource
# Alternative import: from productivity_app.data_pipeline.parameters import ParameterEnum


@report(
    title="CSV Columns Report",
    description="Generates a report of the columns in a CSV file.",
    inputs=[DataSource.FilePath],  # or ParameterEnum.FilePath - both work!
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
    inputs=[DataSource.InputPath, DataSource.OutputPath],
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
    description="Generates a report of the columns in a CSV file with optional output file.",
    inputs=[DataSource.PartsList],
)
def parts_list_with_output_path(parts: list[Part]) -> str:
    """Generate a report of CSV columns

    This report does not read a filepath, rather it says it requires a list of Part objects, and does 
    not care how they got there (could be from CSV, Excel, database, etc).

    Args:
        parts: List of Part objects

    Returns:
        A string report of the columns in the CSV file
    """

    part_count = len(parts)
    print("report generated:")
    print(f"Number of parts: {part_count}")

    return part_count
