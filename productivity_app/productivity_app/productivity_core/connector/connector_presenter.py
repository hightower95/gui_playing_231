"""
Connector Presenter - Main coordinator for connector module
"""
from PySide6.QtCore import QObject, Signal, QTimer
from .connector_model import ConnectorModel


class ConnectorPresenter(QObject):
    """Main presenter coordinating the connector module"""

    # Signals
    loading_started = Signal()
    loading_progress = Signal(int, str)
    loading_completed = Signal()
    loading_failed = Signal(str)

    def __init__(self, context):
        super().__init__()
        self.context = context
        self.model = ConnectorModel(context)

        # Connect model signals
        self.model.loading_progress.connect(self.loading_progress)
        self.model.data_loaded.connect(self._on_data_loaded)
        self.model.loading_failed.connect(self.loading_failed)

    def _on_data_loaded(self, data):
        """Handle successful data loading"""
        self.loading_completed.emit()

    def _auto_load_data(self):
        """Auto-load data on initialization with slight delay"""
        QTimer.singleShot(100, self.model.load_async)

    def start_loading(self):
        """Start loading connector data"""
        self.loading_started.emit()
        self.model.load_async()
