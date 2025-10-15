"""
Base Model class for data management components
"""
from abc import ABC, abstractmethod
from PySide6.QtCore import QObject, Signal
from typing import Any, Dict, List, Optional
from .app_context import AppContext


class BaseModel(QObject):
    """Base class for all model components"""

    # Common signals that models might emit
    data_updated = Signal(object)
    data_loaded = Signal(object)
    data_saved = Signal(bool)

    def __init__(self, context: AppContext):
        super().__init__()
        self.context = context
        self._data: Dict[str, Any] = {}
        self._initialize_data()

    @abstractmethod
    def _initialize_data(self):
        """Initialize model data - must be implemented by subclasses"""
        pass

    def get_data(self, key: str = None) -> Any:
        """Get data by key, or all data if no key specified"""
        if key is None:
            return self._data.copy()
        return self._data.get(key)

    def set_data(self, key: str, value: Any):
        """Set data for a specific key"""
        self._data[key] = value
        self.data_updated.emit({key: value})

    def update_data(self, data_dict: Dict[str, Any]):
        """Update multiple data items"""
        self._data.update(data_dict)
        self.data_updated.emit(data_dict)

    def clear_data(self):
        """Clear all data"""
        self._data.clear()
        self.data_updated.emit({})

    def has_data(self, key: str) -> bool:
        """Check if data exists for a key"""
        return key in self._data

    def load_data(self) -> bool:
        """Load data - can be overridden by subclasses"""
        # Default implementation - subclasses should override
        self.data_loaded.emit(self._data)
        return True

    def save_data(self) -> bool:
        """Save data - can be overridden by subclasses"""
        # Default implementation - subclasses should override
        self.data_saved.emit(True)
        return True
