"""
Connector Model - Data management for connector lookups with threading support
"""
from typing import Dict, List, Any, Optional
from PySide6.QtCore import QObject, Signal, QThread, QMutex, QMutexLocker
from app.core.base_model import BaseModel
import time


class ConnectorDataWorker(QObject):
    """Worker class for loading connector data in a separate thread"""

    # Signals to communicate with main thread
    progress = Signal(int, str)  # progress_percent, status_message
    finished = Signal(object)  # loaded data
    error = Signal(str)  # error_message

    def __init__(self):
        super().__init__()
        self._is_cancelled = False

    def cancel(self):
        """Cancel the loading operation"""
        self._is_cancelled = True

    def run(self):
        """Execute the data loading in background thread"""
        try:
            # Step 1: Initialize connection
            if self._is_cancelled:
                return
            self.progress.emit(20, "Connecting to connector database...")
            time.sleep(0.3)

            # Step 2: Query data
            if self._is_cancelled:
                return
            self.progress.emit(50, "Loading connector configurations...")
            time.sleep(0.4)

            # Step 3: Process data
            if self._is_cancelled:
                return
            self.progress.emit(75, "Processing connector data...")

            # Load the actual data
            data = self._load_connector_data()
            time.sleep(0.2)

            # Complete
            if self._is_cancelled:
                return
            self.progress.emit(100, "Connector data loaded successfully")
            self.finished.emit(data)

        except Exception as e:
            self.error.emit(f"Data loading failed: {str(e)}")

    def _load_connector_data(self) -> Dict:
        """Load connector data (private method)"""
        # In real life, this would load from a database or file
        return {
            'connectors': {
                'DB9_Male_1': {
                    'name': 'DB9_Male_1',
                    'type': 'DB9',
                    'gender': 'Male',
                    'pin_count': 9,
                    'manufacturer': 'Generic',
                    'part_number': 'DB9M-001',
                },
                'DB25_Female_1': {
                    'name': 'DB25_Female_1',
                    'type': 'DB25',
                    'gender': 'Female',
                    'pin_count': 25,
                    'manufacturer': 'Generic',
                    'part_number': 'DB25F-001',
                },
                'RJ45_1': {
                    'name': 'RJ45_1',
                    'type': 'RJ45',
                    'gender': 'Hermaphroditic',
                    'pin_count': 8,
                    'manufacturer': 'Generic',
                    'part_number': 'RJ45-001',
                }
            },
            'connector_types': ['DB9', 'DB15', 'DB25', 'RJ45', 'USB-C', 'HDMI', 'VGA'],
            'genders': ['Male', 'Female', 'Hermaphroditic'],
            'manufacturers': ['Generic', 'Amphenol', 'TE Connectivity', 'Molex', 'Phoenix Contact']
        }


class ConnectorModel(BaseModel):
    """Model for managing connector data with thread-safe async loading"""

    # Additional signals for loading process
    loading_progress = Signal(int, str)  # progress_percent, status_message
    loading_failed = Signal(str)  # error_message
    data_filtered = Signal(object)  # filtered data

    def __init__(self, context):
        super().__init__(context)
        self.data = None
        self._data_mutex = QMutex()
        self._worker = None
        self._thread = None

    def load_async(self):
        """Load connector data asynchronously in a background thread"""
        with QMutexLocker(self._data_mutex):
            # Cancel any existing load operation
            if self._worker is not None:
                self._worker.cancel()
                if self._thread is not None and self._thread.isRunning():
                    self._thread.quit()
                    self._thread.wait()

            # Create worker and thread
            self._worker = ConnectorDataWorker()
            self._thread = QThread()

            # Move worker to thread
            self._worker.moveToThread(self._thread)

            # Connect signals
            self._thread.started.connect(self._worker.run)
            self._worker.progress.connect(self._on_loading_progress)
            self._worker.finished.connect(self._on_loading_finished)
            self._worker.error.connect(self._on_loading_error)
            self._worker.finished.connect(self._thread.quit)
            self._worker.error.connect(self._thread.quit)

            # Start thread
            self._thread.start()

    def _on_loading_progress(self, percent: int, message: str):
        """Handle loading progress updates"""
        self.loading_progress.emit(percent, message)

    def _on_loading_finished(self, data: Dict):
        """Handle successful data loading"""
        with QMutexLocker(self._data_mutex):
            self.data = data
            self.data_loaded.emit(data)

    def _on_loading_error(self, error_message: str):
        """Handle loading errors"""
        self.loading_failed.emit(error_message)

    def get_all(self) -> Optional[Dict]:
        """Get all connector data (thread-safe)"""
        with QMutexLocker(self._data_mutex):
            return self.data.copy() if self.data else None

    def get_connector_types(self) -> List[str]:
        """Get list of available connector types (thread-safe)"""
        with QMutexLocker(self._data_mutex):
            if self.data:
                return self.data.get('connector_types', [])
            return []

    def get_genders(self) -> List[str]:
        """Get list of available genders (thread-safe)"""
        with QMutexLocker(self._data_mutex):
            if self.data:
                return self.data.get('genders', [])
            return []

    def get_manufacturers(self) -> List[str]:
        """Get list of available manufacturers (thread-safe)"""
        with QMutexLocker(self._data_mutex):
            if self.data:
                return self.data.get('manufacturers', [])
            return []

    def get_connectors(self) -> Dict:
        """Get all connectors (thread-safe)"""
        with QMutexLocker(self._data_mutex):
            if self.data:
                return self.data.get('connectors', {})
            return {}

    def filter_connectors(self, filters: Dict) -> List[Dict]:
        """Filter connectors based on criteria (thread-safe)"""
        with QMutexLocker(self._data_mutex):
            if not self.data:
                return []

            connectors = self.data.get('connectors', {})
            results = []

            for conn_name, conn_data in connectors.items():
                match = True

                # Apply filters
                if 'type' in filters and filters['type']:
                    if conn_data.get('type') not in filters['type']:
                        match = False

                if 'gender' in filters and filters['gender']:
                    if conn_data.get('gender') not in filters['gender']:
                        match = False

                if 'manufacturer' in filters and filters['manufacturer']:
                    if conn_data.get('manufacturer') not in filters['manufacturer']:
                        match = False

                if match:
                    results.append(conn_data)

            return results
