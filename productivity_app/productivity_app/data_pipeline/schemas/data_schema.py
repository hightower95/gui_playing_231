"""
Data Schema Definition

Defines the expected structure of data sources including required columns
and optional validation logic.
"""
from typing import Any, Optional
import pandas as pd


class DataSchema:
    """Schema defining expected structure of a data source"""

    def __init__(self,
                 name: str,
                 required_columns: list[str],
                 optional_columns: Optional[list[str]] = None,
                 description: Optional[str] = None):
        self.name = name
        self.required_columns = required_columns
        self.optional_columns = optional_columns or []
        self.description = description or f"Schema for {name}"

    def validate(self, data: Any) -> bool:
        """Validate that data has all required columns

        Args:
            data: DataFrame or dict-like object with column access

        Returns:
            True if all required columns present, False otherwise
        """
        if isinstance(data, pd.DataFrame):
            return all(col in data.columns for col in self.required_columns)
        elif isinstance(data, dict):
            return all(col in data for col in self.required_columns)
        else:
            # Try generic attribute access
            try:
                return all(hasattr(data, col) for col in self.required_columns)
            except:
                return False

    def get_all_columns(self) -> list[str]:
        """Get list of all columns (required + optional)"""
        return self.required_columns + self.optional_columns

    def __repr__(self):
        return f"DataSchema(name='{self.name}', required={self.required_columns})"
