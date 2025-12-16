from productivity_app.data_pipeline.decorators import data_collector
from productivity_app.data_pipeline.types_enum import DataTypes


def excel_collector(filepath, schema):
    import pandas as pd

    # Load the Excel file into a DataFrame
    df = pd.read_excel(filepath)

    # Validate required columns
    schema.validate(df)

    return df


@data_collector(
    name="ExcelToPartsListCollector",
    inputs=[DataSource.FilePath],
    outputs=[DataSource.PartsList],
)
def excel_to_parts_list_collector(file_path: str) -> list['Part']:
    """
    Collects parts list data from an Excel file.

    Args:
        file_path (str): Path to the Excel file.


    """
    # Validate required columns
    schema = data_schemas.get(DataTypes.PartsList)
    df = excel_collector(file_path, schema)

    import Part
    all_parts = []
    for row in df.itertuples():
        part = Part(
            part_name=row._asdict().get('Part Name'),
            part_number=row._asdict().get('Part Number'),
            quantity=row._asdict().get('Quantity', None)
        )
        all_parts.append(part)
        # Process part as needed

    return all_parts


@data_collector(
    name="ExcelCollector",
    inputs=[DataTypes.FilePath],
    outputs=[DataTypes.PartsList],
)
def excel_to_parts_list_collector(file_path: str) -> pd.DataFrame:
    """
    Collects parts list data from an Excel file.

    Args:
        file_path (str): Path to the Excel file.


    """

    # Load the Excel file into a DataFrame
    df = pd.read_excel(file_path)

    # Validate required columns
    schema = data_schemas.get(DataTypes.PartsList)
    schema.validate(df)
    return df
