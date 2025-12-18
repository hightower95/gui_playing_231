from enum import Enum


class DataTypes(Enum):
    """Enumeration of data types that can be used as parameters"""
    PartsList = "PartsList"
    BOMData = "BOMData"
    TestResults = "TestResults"
    FilePath = "FilePath"
    DataFrame = "DataFrame"
    QueryID = "QueryID"
    ComparisonResult = "ComparisonResult"

    StreetPriceList = "StreetPriceList"


class FileTypes(Enum):
    """Enumeration of file types that can be used as sources"""
    ExcelFile = "ExcelFile"
    CSVFile = "CSVFile"
    TextFile = "TextFile"
