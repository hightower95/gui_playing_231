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
