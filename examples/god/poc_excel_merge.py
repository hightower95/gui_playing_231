"""
Proof of Concept: Excel file combining pipeline

This demonstrates the data pipeline system by:
1. Registering data providers to load Excel files
2. Registering a reporter to merge them
3. Executing the pipeline to create a combined output
"""

import pandas as pd
from pathlib import Path
from god_module import data_provider, reporter, param, Pipeline, DataFormat


# Data Provider: Load first Excel file
@data_provider(
    provides=[DataFormat.EXCEL_DATAFRAME],
    requires=[
        param('file_path', str, description='Path to first Excel file'),
        param('sheet_name', str, default='Sheet1',
              description='Sheet name to load')
    ],
    description="Load data from the first Excel file"
)
def load_excel_file_1(file_path: str, sheet_name: str):
    """Load first Excel file into a DataFrame"""
    print(f"Loading Excel file 1 from: {file_path}")
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    print(f"Loaded {len(df)} rows from file 1")
    return df


# Data Provider: Load second Excel file
@data_provider(
    provides=[DataFormat.EXCEL_DATAFRAME],
    requires=[
        param('file_path', str, description='Path to second Excel file'),
        param('sheet_name', str, default='Sheet1',
              description='Sheet name to load')
    ],
    description="Load data from the second Excel file"
)
def load_excel_file_2(file_path: str, sheet_name: str):
    """Load second Excel file into a DataFrame"""
    print(f"Loading Excel file 2 from: {file_path}")
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    print(f"Loaded {len(df)} rows from file 2")
    return df


# Reporter: Merge Excel files
@reporter(
    inputs=[DataFormat.EXCEL_DATAFRAME, DataFormat.EXCEL_DATAFRAME],
    outputs=[DataFormat.EXCEL_REPORT],
    parameters=[
        param('output_path', str, description='Path for combined output file'),
        param('merge_type', str, default='concat',
              description='Merge type: concat or join'),
        param('join_key', str, default=None,
              description='Column to join on (if merge_type=join)')
    ],
    description="Merge two Excel DataFrames into a single output file"
)
def merge_excel_files(df1: pd.DataFrame, df2: pd.DataFrame,
                      output_path: str, merge_type: str, join_key: str):
    """
    Merge two DataFrames and save to Excel.

    Supports:
    - concat: Stack DataFrames vertically
    - join: Inner join on specified key column
    """
    print(f"\nMerging Excel files using method: {merge_type}")

    if merge_type == 'concat':
        # Simple concatenation (stacking)
        merged = pd.concat([df1, df2], ignore_index=True)
        print(f"Concatenated {len(df1)} + {len(df2)} = {len(merged)} rows")

    elif merge_type == 'join' and join_key:
        # Join on common column
        merged = pd.merge(df1, df2, on=join_key, how='inner')
        print(f"Joined on '{join_key}': {len(merged)} matching rows")

    else:
        raise ValueError(
            f"Invalid merge_type '{merge_type}' or missing join_key")

    # Save to Excel
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    merged.to_excel(output_path, index=False, sheet_name='Merged Data')
    print(f"✓ Saved merged data to: {output_path}")

    return str(output_path)


def run_poc():
    """
    Run the proof of concept pipeline.

    This creates two sample Excel files, then combines them using the pipeline.
    """
    print("=" * 60)
    print("PROOF OF CONCEPT: Excel Combining Pipeline")
    print("=" * 60)

    # Create sample data
    print("\n1. Creating sample Excel files...")

    sample_dir = Path(__file__).parent / "sample_data"
    sample_dir.mkdir(exist_ok=True)

    # Sample file 1: Employee data
    file1_path = sample_dir / "employees_dept_a.xlsx"
    df1 = pd.DataFrame({
        'Employee_ID': [1, 2, 3],
        'Name': ['Alice', 'Bob', 'Charlie'],
        'Department': ['Engineering', 'Engineering', 'Engineering'],
        'Salary': [75000, 80000, 70000]
    })
    df1.to_excel(file1_path, index=False)
    print(f"   Created: {file1_path}")

    # Sample file 2: More employee data
    file2_path = sample_dir / "employees_dept_b.xlsx"
    df2 = pd.DataFrame({
        'Employee_ID': [4, 5, 6],
        'Name': ['Diana', 'Eve', 'Frank'],
        'Department': ['Sales', 'Sales', 'Sales'],
        'Salary': [65000, 72000, 68000]
    })
    df2.to_excel(file2_path, index=False)
    print(f"   Created: {file2_path}")

    # Set up pipeline
    print("\n2. Setting up pipeline...")
    pipeline = Pipeline()

    # Run providers to load data
    print("\n3. Running data providers...")
    pipeline.run_provider('load_excel_file_1',
                          file_path=str(file1_path))
    pipeline.run_provider('load_excel_file_2',
                          file_path=str(file2_path))

    # Run reporter to merge
    print("\n4. Running reporter to merge files...")
    output_path = sample_dir / "combined_employees.xlsx"
    result = pipeline.run_reporter('merge_excel_files',
                                   output_path=str(output_path),
                                   merge_type='concat')

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\nOutput file: {result}")

    # Show logs
    print("\n📋 Pipeline Logs:")
    for log in pipeline.context.get_logs():
        print(f"   [{log['level']}] {log['message']}")

    return result


if __name__ == '__main__':
    run_poc()
