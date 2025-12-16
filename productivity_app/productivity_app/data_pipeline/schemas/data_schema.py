"""
Data Schema Definition

Defines the expected structure of data sources including required columns
and optional validation logic.
"""
from typing import Any, Optional, Callable, List
import pandas as pd


class DataSchema:
    """Schema defining expected structure of a data source"""

    def __init__(self,
                 name: str,
                 required_columns: list[str],
                 optional_columns: Optional[list[str]] = None,
                 description: Optional[str] = None,
                 converter: Optional[Callable[[pd.DataFrame], List[Any]]] = None):
        self.name = name
        self.required_columns = required_columns
        self.optional_columns = optional_columns or []
        self.description = description or f"Schema for {name}"
        self.converter = converter

    def validate(self, data: Any) -> tuple[bool, list[str]]:
        """Validate that data has all required columns

        Args:
            data: DataFrame or dict-like object with column access

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        if isinstance(data, pd.DataFrame):
            columns = data.columns
        elif isinstance(data, dict):
            columns = data.keys()
        else:
            # Try generic attribute access
            try:
                columns = [col for col in self.required_columns if hasattr(data, col)]
            except:
                return False, ["Cannot determine columns from data"]
        
        # Check for missing required columns
        missing = [col for col in self.required_columns if col not in columns]
        if missing:
            errors.append(f"Missing required columns: {', '.join(missing)}")
        
        return len(errors) == 0, errors
    
    def convert(self, df: pd.DataFrame) -> List[Any]:
        """Convert DataFrame to typed objects using registered converter
        
        Args:
            df: DataFrame to convert
            
        Returns:
            List of typed objects
            
        Raises:
            ValueError: If no converter is registered
        """
        if self.converter is None:
            raise ValueError(f"No converter registered for schema '{self.name}'")
        
        return self.converter(df)

    def get_all_columns(self) -> list[str]:
        """Get list of all columns (required + optional)"""
        return self.required_columns + self.optional_columns

    def __repr__(self):
        return f"DataSchema(name='{self.name}', required={self.required_columns})"
