from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class ResultObject:
    source: str
    data: Dict[str, Any]
    context: Dict[str, Any] = None
