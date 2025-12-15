from abc import ABC, abstractmethod
from enum import Enum

from dataclasses import dataclass, replace


class DataTypes(Enum):
    PartsList = "PartsList"


class FileTypes(Enum):
    ExcelFile = "ExcelFile"


class DataSchema:
    def __init__(self, name: str, required_columns: list[str]):
        self.name = name
        self.required_columns = required_columns

    def validate(self, data) -> bool:
        return all(col in data.columns for col in self.required_columns)


class FileSchema:
    def __init__(self, name: str, required_columns: list[str]):
        self.name = name
        self.required_columns = required_columns

    def validate(self, data) -> bool:
        return all(col in data.columns for col in self.required_columns)


PARTS_LIST_SCHEMA = DataSchema(
    name="PartsList",
    required_columns=["PartNumber", "Description", "Quantity"]
)


DATA_TYPE_SCHEMAS = {
    DataTypes.PartsList: PARTS_LIST_SCHEMA
}
FILE_TYPE_SCHEMAS = {
    # DataTypes.PartsList: PARTS_LIST_SCHEMA
}


@dataclass(frozen=True)
class Parameter(ABC):
    name: str
    required: bool = True
    description: str = ""

    @abstractmethod
    def validate(self, value) -> bool:
        pass

    @staticmethod
    def FileSource(name: str, file_type: FileTypes, **kwargs):
        return FileSourceParameter(name,
                                   file_type,
                                   schema=kwargs.pop(
                                       "schema", FILE_TYPE_SCHEMAS.get(file_type)),
                                   **kwargs)

    @staticmethod
    def DataSource(name: str, data_type: DataTypes, **kwargs):
        return DataSourceParameter(
            name=name,
            data_type=data_type,
            schema=kwargs.pop("schema", DATA_TYPE_SCHEMAS.get(data_type)),
            **kwargs
        )


@dataclass(frozen=True)
class DataSourceParameter(Parameter):
    data_type: DataTypes = None
    schema: DataSchema = None

    def validate(self, value) -> bool:
        """Validate value against schema if available"""
        if self.schema is None:
            return True
        return self.schema.validate(value)

    def modify(self, name: str = None, required: bool = None) -> 'DataSourceParameter':
        """Create a modified copy of this parameter"""
        changes = {}
        if name is not None:
            changes['name'] = name
        if required is not None:
            changes['required'] = required

        if not changes:
            return self

        return replace(self, **changes)


@dataclass(frozen=True)
class FileSourceParameter(Parameter):
    file_type: FileTypes = None
    schema: 'FileSchema' = None

    def validate(self, value) -> bool:
        """Validate file against schema if available"""
        if self.schema is None:
            return True
        return self.schema.validate(value)


PartsList = Parameter.DataSource(
    name="parts_list",  # Assigned when used
    data_type=DataTypes.PartsList,
    description="A data source containing a parts list"
)


class ParameterSpec(ABC):
    @abstractmethod
    def bind(self, function_signature):
        pass


class Repeatable(ParameterSpec):
    def __init__(
        self,
        prototype: Parameter,
        min_items: int = 1,
        max_items: int | None = None
    ):
        self.prototype = prototype
        self.min_items = min_items
        self.max_items = max_items
