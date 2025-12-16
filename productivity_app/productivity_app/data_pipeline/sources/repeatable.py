from productivity_app.data_pipeline.models.parameter import Parameter
from abc import ABC, abstractmethod


class ParameterSpec(ABC):
    @abstractmethod
    def bind(self, function_signature):
        pass


class Repeatable(ParameterSpec):
    def __init__(
        self,
        prototype: Parameter,
        min_items: int = 1,
        max_items: int | None = None
    ):
        self.prototype = prototype
        self.min_items = min_items
        self.max_items = max_items
