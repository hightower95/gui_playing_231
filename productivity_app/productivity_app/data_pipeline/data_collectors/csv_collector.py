
from productivity_app.data_pipeline.data_collectors.decorator import data_collector
from productivity_app.data_pipeline.parameters import Variables
import pandas as pd


@data_collector(
    name="CSVCollector",
    inputs=[Variables.FilePath],
    outputs=[Variables.DataFrame])
def csv_collector(filepath: str) -> pd.DataFrame:
    """Collect data from a CSV file

    Args:
        filepath: Path to the CSV file"""
    import pandas as pd

    df = pd.read_csv(filepath)
    return df
