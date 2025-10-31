"""
Base View class for all UI components
"""
from abc import ABC, abstractmethod
from PySide6.QtWidgets import QWidget
# from PySide6.QtCore import Signal
# from .app_context import AppContext


class BaseView(QWidget):
    """Common base class for all views."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """To be implemented by subclasses."""
        pass

# class BaseView(QWidget, ABC):
#     """Base class for all view components"""

#     # Common signals that views might emit
#     view_ready = Signal()
#     view_closed = Signal()

#     def __init__(self, context: AppContext, parent=None):
#         super().__init__(parent)
#         self.context = context
#         self._setup_ui()
#         self._connect_signals()

#     @abstractmethod
#     def _setup_ui(self):
#         """Setup the UI components - must be implemented by subclasses"""
#         pass

#     def _connect_signals(self):
#         """Connect signals - can be overridden by subclasses"""
#         pass

#     def show_view(self):
#         """Show the view"""
#         self.show()
#         self.view_ready.emit()

#     def hide_view(self):
#         """Hide the view"""
#         self.hide()

#     def close_view(self):
#         """Close the view"""
#         self.close()
#         self.view_closed.emit()
