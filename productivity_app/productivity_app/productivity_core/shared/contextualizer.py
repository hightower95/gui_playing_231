from typing import List
from ..shared.result_object import ResultObject


class Contextualizer:
    """Base interface for adding context to fault finding results."""

    def contextualize(self, results: List[ResultObject]) -> List[ResultObject]:
        raise NotImplementedError
