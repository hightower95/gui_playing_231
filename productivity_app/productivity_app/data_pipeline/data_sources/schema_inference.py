"""
Auto-generate schema from dataclass

Infers column mapping and schema from a dataclass definition.
"""
import pandas as pd
from dataclasses import fields, is_dataclass, MISSING
from typing import Type, Callable, List, Tuple, get_origin
from productivity_app.data_pipeline.data_sources.schema_base_classes import DataSchema


def infer_schema_from_dataclass(
    model_class: Type,
    name: str = None,
    description: str = None
) -> DataSchema:
    """Generate a DataSchema from a dataclass
    
    Args:
        model_class: Dataclass to infer from (e.g., Part)
        name: Schema name (defaults to class name)
        description: Schema description
        
    Returns:
        DataSchema with inferred columns and converter
        
    Example:
        from productivity_app.data_pipeline.models.part import Part
        
        schema = infer_schema_from_dataclass(
            Part,
            name="PartsList",
            description="Parts with names and numbers"
        )
    """
    if not is_dataclass(model_class):
        raise ValueError(f"{model_class} is not a dataclass")
    
    name = name or model_class.__name__
    description = description or f"Schema for {model_class.__name__}"
    
    # Extract field information
    required_fields = []
    optional_fields = []
    column_map = {}
    
    for field in fields(model_class):
        field_name = field.name
        
        # Check if field has default or default_factory
        is_optional = field.default is not MISSING or field.default_factory is not MISSING
        
        # Support both snake_case and Title Case
        title_case = field_name.replace('_', ' ').title()
        
        column_map[field_name] = field_name  # snake_case
        column_map[title_case] = field_name  # Title Case
        
        if is_optional:
            optional_fields.append(field_name)
        else:
            required_fields.append(field_name)
    
    # Create converter function
    def converter(df: pd.DataFrame) -> List:
        """Convert DataFrame to list of model instances"""
        instances = []
        
        for _, row in df.iterrows():
            kwargs = {
                target_field: row[col]
                for col, target_field in column_map.items()
                if col in row and not pd.isna(row[col])
            }
            instances.append(model_class(**kwargs))
        
        return instances
    
    return DataSchema(
        name=name,
        required_columns=required_fields,
        optional_columns=optional_fields,
        description=description,
        converter=converter
    )


def get_column_variants(field_name: str) -> List[str]:
    """Get common variants of a column name
    
    Args:
        field_name: Field name like 'part_number'
        
    Returns:
        List of variants: ['part_number', 'Part Number', 'partnumber', 'PartNumber']
    """
    variants = [
        field_name,  # part_number
        field_name.replace('_', ' ').title(),  # Part Number
        field_name.replace('_', ''),  # partnumber
        ''.join(word.capitalize() for word in field_name.split('_'))  # PartNumber
    ]
    return list(set(variants))  # Remove duplicates
