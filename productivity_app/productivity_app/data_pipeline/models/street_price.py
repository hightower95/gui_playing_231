
from dataclasses import dataclass
from typing import Optional


@dataclass
class StreetPrice:
    """Single part in a parts list"""
    street: str
    town: str
    price: int
