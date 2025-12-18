"""
PartsList Parameter - Collected list of Part objects

This parameter uses the collector-schema separation pattern:
- Transport collectors (csv_collector, generic_excel_collector) read files
- Schema converters (PartsList schema) convert DataFrames to Part objects
- No model-specific collectors needed
"""
from typing import List, Any
from productivity_app.data_pipeline.parameters.input_parameters import CollectedParameter
from productivity_app.data_pipeline.parameters.parameter_registry import parameter_registry
from productivity_app.data_pipeline.types_enum import DataTypes
from productivity_app.data_pipeline.parameters.resolution import resolve_collected_parameter_from_file


class StreetPriceListParameter(CollectedParameter):
    """Extended CollectedParameter with resolution capability"""

    def __init__(self, **kwargs):
        # Set defaults if not provided
        kwargs.setdefault('name', 'street_prices')
        kwargs.setdefault('description', 'List of Street Price objects')
        kwargs.setdefault('title', 'Street Price List')
        kwargs.setdefault('output_type', DataTypes.StreetPriceList)
        super().__init__(**kwargs)

    def resolve_from_file(self, filepath: str) -> List[Any]:
        """Resolve StreetPriceList from a file path

        Composes:
        1. Transport collector (CSV/Excel → DataFrame)
        2. Schema converter (DataFrame → List[StreetPrice])

        Args:
            filepath: Path to CSV or Excel file

        Returns:
            List of StreetPrice objects

        Example:
            param = ParameterEnum.StreetPriceList
            street_prices = param.resolve_from_file("street_prices.csv")
        """
        return resolve_collected_parameter_from_file(filepath, self.output_type)


parameter = parameter_registry.define_parameter(
    name="StreetPriceList",
    parameter=StreetPriceListParameter()
)

# Backwards compatibility
StreetPriceList = parameter
