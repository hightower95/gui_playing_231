"""
Base Presenter class for business logic components

This is an optional base class for presenters. It provides:
1. Standard initialization pattern (context, view, model, title)
2. Lifecycle management (cleanup method)
3. Common helper methods for error handling

Presenters are NOT required to inherit from this class. You can create
standalone presenters if the base class doesn't add value for your use case.
"""
from typing import Optional, Any
from PySide6.QtCore import QObject
from .app_context import AppContext


class BasePresenter(QObject):
    """
    Base class for presenter components in MVP architecture.

    Provides standard initialization and lifecycle management.
    Subclasses should override bind() to connect view signals.
    """

    def __init__(self, context: AppContext, view: QObject, model: Optional[QObject] = None, title: str = "New Tab"):
        """
        Initialize the presenter.

        Args:
            context: Application context for accessing services
            view: The view component this presenter controls
            model: Optional model component for data management
            title: Tab title (for tab-based presenters)
        """
        super().__init__()
        self.title = title
        self.context = context
        self.view = view
        self.model = model

    def bind(self):
        """
        Connect view signals to presenter slots.

        Override this method to set up signal-slot connections.
        Called after presenter initialization.
        """
        pass

    def cleanup(self):
        """
        Clean up resources when presenter is destroyed.

        Override this method to:
        - Disconnect signals
        - Stop background workers
        - Release resources
        """
        pass

    def log_error(self, error_message: str, exception: Optional[Exception] = None):
        """
        Log an error message.

        Args:
            error_message: Description of the error
            exception: Optional exception object for detailed logging
        """
        error_text = f"Error in {self.__class__.__name__}: {error_message}"
        if exception:
            error_text += f"\n  Exception: {str(exception)}"
        print(error_text)

        # Could be extended to write to log file, show dialog, etc.

    def log_info(self, message: str):
        """
        Log an informational message.

        Args:
            message: Information message to log
        """
        print(f"{self.__class__.__name__}: {message}")
