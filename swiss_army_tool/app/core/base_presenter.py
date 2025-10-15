"""
Base Presenter class for business logic components
"""
from abc import ABC, abstractmethod
from PySide6.QtCore import QObject, Signal
from .app_context import AppContext


class BasePresenter:
    """Base class for all presenter components"""

    # Common signals that presenters might emit
    data_changed = Signal(object)
    error_occurred = Signal(str)
    operation_completed = Signal(str)

    def __init__(self, context, view, model=None, title="New TAB"):
        self.title = title
        self.context = context
        self.view = view
        self.model = model

    def bind(self):
        """Connect view signals to presenter slots."""
        pass
    # def _initialize(self):
    #     """Initialize the presenter - must be implemented by subclasses"""
    #     pass

    def handle_error(self, error_message: str):
        """Handle errors and emit error signal"""
        print(f"Error in {self.__class__.__name__}: {error_message}")
        self.error_occurred.emit(error_message)

    def complete_operation(self, operation_name: str):
        """Signal completion of an operation"""
        print(
            f"Operation completed in {self.__class__.__name__}: {operation_name}")
        self.operation_completed.emit(operation_name)
