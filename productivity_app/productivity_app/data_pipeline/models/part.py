"""
Part Dataclass

Defines the structure of a single part in a parts list.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Part:
    """Single part in a parts list"""
    part_name: str
    part_number: str
    description: Optional[str] = None
    quantity: Optional[int] = None
    unit_cost: Optional[float] = None

    def __post_init__(self):
        """Normalize field names from DataFrame columns"""
        # Handle common column name variations
        if hasattr(self, 'Part Name'):
            self.part_name = getattr(self, 'Part Name')
        if hasattr(self, 'Part Number'):
            self.part_number = getattr(self, 'Part Number')
