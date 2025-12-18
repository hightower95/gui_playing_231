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


class PartsListParameter(CollectedParameter):
    """Extended CollectedParameter with resolution capability"""
    
    def __init__(self, **kwargs):
        # Set defaults if not provided
        kwargs.setdefault('name', 'parts')
        kwargs.setdefault('description', 'List of Part objects')
        kwargs.setdefault('title', 'Parts List')
        kwargs.setdefault('output_type', DataTypes.PartsList)
        super().__init__(**kwargs)
    
    def resolve_from_file(self, filepath: str) -> List[Any]:
        """Resolve PartsList from a file path
        
        Composes:
        1. Transport collector (CSV/Excel → DataFrame)
        2. Schema converter (DataFrame → List[Part])
        
        Args:
            filepath: Path to CSV or Excel file
            
        Returns:
            List of Part objects
            
        Example:
            param = ParameterEnum.PartsList
            parts = param.resolve_from_file("parts.csv")
        """
        return resolve_collected_parameter_from_file(filepath, self.output_type)


parameter = parameter_registry.define_parameter(
    name="PartsList",
    parameter=PartsListParameter()
)

# Backwards compatibility
PartsList = parameter
