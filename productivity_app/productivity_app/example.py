
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Report:
    name: str
    summary: str
    description: str
    version: str = "1.0"
    updated_at: str = "2024-01-01"
    created_date: str = "2024-01-01"
    author: str = "Unknown"
    changes: dict[str, str] = field(default_factory=dict)  # date: update


class DataType(ABC):
    @staticmethod
    def validate(data) -> bool:
        raise NotImplementedError(
            "Subclasses should implement validate method")


class BomList(DataType):
    headers = ["Part Number", "Description", "Quantity", "Unit Price"]

    @staticmethod
    def validate(data) -> bool:
        # Placeholder validation logic
        required_columns = set(BomList.headers)
        return required_columns.issubset(set(data.columns))


class DataTypes:
    BomList = BomList()


class FileTypes:
    ExcelFile = "ExcelFile"


class Parameter(ABC):
    def __init__(self, name: str, data_type: DataType, required: bool = True, description: str = ""):
        self.name = name
        self.data_type = data_type
        self.required = required
        self.description = description

    @abstractmethod
    def validate(self, value) -> bool:
        pass

    @staticmethod
    def FileSource(name: str, file_type: FileTypes, **kwargs):
        return FileSourceParameter(name, file_type, **kwargs)

    @staticmethod
    def DataSource(name: str, data_type: DataType, **kwargs):
        return DataSourceParameter(name, data_type, **kwargs)


class DataSourceParameter(Parameter):
    def __init__(self, name: str, data_type: DataType, **kwargs):
        super().__init__(name, data_type, **kwargs)


class FileSourceParameter(Parameter):
    def __init__(self, name: str, file_type: FileTypes, **kwargs):
        super().__init__(name, data_type=None, **kwargs)
        self.file_type = file_type


def report(report: Report,
           *inputs: Parameter,
           outputs: list[str]):
    """Decorator to register a report with metadata and I/O specifications"""

    def decorator(func):
        func._report_metadata = {
            "report": report,
            "inputs": inputs,
            "outputs": outputs
        }
        return func

    return decorator


@report(
    Report(name="Custom Report",
           summary="A report generated in a custom format.",
           description="""A report in a custom format.
            Takes the standard data and outputs it in a custom format.

            Some more text to make the description longer and see how it wraps in the UI.

            This report is useful for demonstrating custom report generation.
           """,
           created_date="2025-06-15",
           author="Me"
           ),
    bom_list_1=Parameter.DataSource(
        DataTypes.BomList
    ),
    cost_data=Parameter.FileSource(
        FileTypes.ExcelFile
    ),
    output_path=Parameters.FolderPath,
    other_parameter=Parameters.CustomParameter,
    outputs=[FileTypes.ExcelFile]

)
def my_first_report(bom_list_1, cost_data, output_path: str) -> str:
    """Generate a custom report from two BOM lists.

    Args:
        bom_list_1: First BOM list as DataFrame
        bom_list_2: Second BOM list as DataFrame
        output_path: Path to save the custom report"""
