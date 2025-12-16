"""
Example: FileSource with Schema Validation

Shows how to create a FileSource parameter that validates file structure.
"""
from productivity_app.data_pipeline.parameters.parts_list import PartsList
from productivity_app.data_pipeline.types_enum import FileTypes, DataTypes
from productivity_app.data_pipeline.schemas import DataSchema, data_schemas, FileSchema
from productivity_app.data_pipeline.sources.base import Source
from productivity_app.data_pipeline.decorators.register_report import register_report


# Define a schema for Excel files containing parts
PARTS_EXCEL_SCHEMA = FileSchema(
    name="PartsExcel",
    required_columns=["Part Name", "Part Number"]
)


def PartsExcelFile(name: str, required: bool = True, description: str = "Parts Excel file"):
    """Create a FileSource parameter for parts Excel files with schema validation

    Args:
        name: Parameter name
        required: Whether file is required
        description: Description of this file parameter

    Returns:
        FileSourceParameter with Excel type and schema validation
    """
    return Source.FileSource(
        name=name,
        file_type=FileTypes.ExcelFile,
        schema=PARTS_EXCEL_SCHEMA,
        required=required,
        description=description
    )


# Example report using FileSource with schema
@register_report(
    name="Import Parts from Excel",
    description="Import and validate parts from an Excel file",
    category="Import",
    parameters=[
        PartsExcelFile(
            name="parts_file",
            required=True,
            description="Excel file with parts (must have 'Part Name' and 'Part Number' columns)"
        )
    ]
)
def import_parts_excel(parts_file):
    """Import parts from Excel file with automatic schema validation

    Args:
        parts_file: Path to Excel file (schema validated on load)

    Returns:
        DataFrame with parts data
    """
    import pandas as pd

    # Load the Excel file
    df = pd.read_excel(parts_file)

    # Schema validation already happened!
    # We know 'Part Name' and 'Part Number' columns exist

    print(f"Loaded {len(df)} parts")
    print(f"Columns: {df.columns.tolist()}")

    return df


# Alternative: Use DataSource with PartsList for in-memory data


@register_report(
    name="Process Parts Data",
    description="Process parts data from any source",
    category="Processing",
    parameters=[
        # DataSource for in-memory DataFrame/dict
        PartsList(
            name="parts_data",
            required=True,
            description="Parts data (DataFrame or dict)"
        )
    ]
)
def process_parts_data(parts_data):
    """Process parts data (works with DataFrames, dicts, etc.)

    Args:
        parts_data: Data with 'Part Name' and 'Part Number'
    """
    # Schema validation already happened!
    pass
