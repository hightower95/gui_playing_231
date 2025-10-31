"""
Base Model class for data management components

This is an optional base class for models. It provides:
1. Standard initialization with AppContext access
2. Common signals for data loading/updates
3. Lifecycle management (cleanup method)

Models are NOT required to inherit from this class. You can create
standalone models if the base class doesn't add value for your use case.
"""
from PySide6.QtCore import QObject, Signal
from typing import Optional, Any
from .app_context import AppContext


class BaseModel(QObject):
    """
    Base class for model components in MVP architecture.

    Provides:
    - AppContext access for service dependencies
    - Standard signals for data lifecycle events
    - Optional cleanup method for resource management

    Subclasses should define their own data structures and implement
    their own load/save logic as needed.
    """

    # Common signals for data lifecycle
    # Models can emit these when appropriate, or define their own signals
    data_loaded = Signal(object)  # Emitted when data is successfully loaded
    data_updated = Signal(object)  # Emitted when data changes
    data_saved = Signal(bool)  # Emitted when data is saved (success/failure)
    loading_started = Signal()  # Emitted when a load operation begins
    loading_failed = Signal(str)  # Emitted when load fails (error message)

    def __init__(self, context: AppContext):
        """
        Initialize the model.

        Args:
            context: Application context for accessing services
        """
        super().__init__()
        self.context = context

    def cleanup(self):
        """
        Clean up resources when model is destroyed.

        Override this method to:
        - Stop background workers
        - Cancel pending operations
        - Close file handles
        - Release resources
        """
        pass
