"""
EPD Model - Data management for EPD analysis with proper threading support
"""
from typing import Dict, List, Any, Optional
from PySide6.QtCore import QObject, Signal, QThread, QMutex, QMutexLocker
from app.core.base_model import BaseModel
import pandas as pd
import time


class EpdDataWorker(QObject):
    """Worker class for loading EPD data in a separate thread"""

    # Signals to communicate with main thread
    progress = Signal(int, str)  # progress_percent, status_message
    finished = Signal(object)  # loaded dataframe
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
            self.progress.emit(20, "Connecting to EPD database...")
            time.sleep(0.3)  # Simulate network delay

            # Step 2: Query data
            if self._is_cancelled:
                return
            self.progress.emit(50, "Querying EPD records...")
            time.sleep(0.4)  # Simulate query time

            # Step 3: Process data
            if self._is_cancelled:
                return
            self.progress.emit(75, "Processing EPD data...")

            # Load the actual data
            data = self._load_sample_data()
            time.sleep(0.2)  # Simulate processing time

            # Complete
            if self._is_cancelled:
                return
            self.progress.emit(100, "EPD data loaded successfully")
            self.finished.emit(data)

        except Exception as e:
            self.error.emit(f"Data loading failed: {str(e)}")

    def _load_sample_data(self) -> pd.DataFrame:
        """Load sample EPD data (private method)"""
        # In real life, this would load from Excel or a database
        sample_data = [
            {"EPD": "EPD-001", "Description": "Main harness connector",
             "Cable": "Cable 100", "AWG": 20, "Rating (A)": 15, "Pins": 12},
            {"EPD": "EPD-002", "Description": "Sensor branch harness",
             "Cable": "Cable 200", "AWG": 22, "Rating (A)": 10, "Pins": 8},
            {"EPD": "EPD-003", "Description": "Power distribution loom",
             "Cable": "Cable 100", "AWG": 18, "Rating (A)": 25, "Pins": 16},
            {"EPD": "EPD-004", "Description": "Signal processing unit",
             "Cable": "Cable 300", "AWG": 24, "Rating (A)": 5, "Pins": 20},
            {"EPD": "EPD-005", "Description": "Control module interface",
             "Cable": "Cable 150", "AWG": 20, "Rating (A)": 12, "Pins": 10},
        ]
        return pd.DataFrame(sample_data)


class EpdModel(BaseModel):
    """Model for managing EPD (Electronic Parts Data) with thread-safe async loading"""

    # Additional signals for loading process
    loading_progress = Signal(int, str)  # progress_percent, status_message
    loading_failed = Signal(str)  # error_message
    data_filtered = Signal(object)  # filtered dataframe

    def __init__(self, context):
        super().__init__(context)
        self.data = None
        self.is_loading = False

        # Thread-safe data access
        self._data_mutex = QMutex()

        # Worker thread components
        self._worker = None
        self._thread = None

    def _initialize_data(self):
        """Initialize base model data (called by BaseModel)"""
        # Base model initialization - can be empty for EPD model
        self._data = {}

    def load_async(self):
        """Start asynchronous data loading in a separate thread"""
        if self.is_loading:
            print("Already loading data...")
            return

        self.is_loading = True
        self.loading_progress.emit(0, "Starting EPD data load...")

        # Create worker and thread
        self._worker = EpdDataWorker()
        self._thread = QThread()

        # Move worker to thread
        self._worker.moveToThread(self._thread)

        # Connect signals
        self._worker.progress.connect(self._on_loading_progress)
        self._worker.finished.connect(self._on_loading_finished)
        self._worker.error.connect(self._on_loading_error)

        # Connect thread lifecycle
        self._thread.started.connect(self._worker.run)
        self._thread.finished.connect(self._thread.deleteLater)

        # Start the thread
        self._thread.start()

    def _on_loading_progress(self, progress: int, message: str):
        """Handle progress updates from worker thread"""
        self.loading_progress.emit(progress, message)

    def _on_loading_finished(self, data: pd.DataFrame):
        """Handle successful data loading from worker thread"""
        # Thread-safe data assignment
        with QMutexLocker(self._data_mutex):
            self.data = data

        self.is_loading = False

        # Emit data_loaded signal from BaseModel
        self.data_loaded.emit(self.data)

        # Update internal data storage
        self.set_data('epd_records', self.data.to_dict('records'))
        self.set_data('record_count', len(self.data))

        # Cleanup thread
        self._cleanup_thread()

    def _on_loading_error(self, error_message: str):
        """Handle loading errors from worker thread"""
        self.is_loading = False
        self.loading_failed.emit(error_message)
        print(f"EPD Model loading error: {error_message}")

        # Cleanup thread
        self._cleanup_thread()

    def _cleanup_thread(self):
        """Cleanup worker thread after completion"""
        if self._thread and self._thread.isRunning():
            self._thread.quit()
            self._thread.wait()

        self._thread = None
        self._worker = None

    def get_all(self):
        """Return full dataset (thread-safe)."""
        with QMutexLocker(self._data_mutex):
            if self.data is None:
                return pd.DataFrame()  # Return empty DataFrame if no data loaded
            return self.data.copy()

    def filter(self, text: str):
        """Return filtered rows matching text in any column (thread-safe)."""
        with QMutexLocker(self._data_mutex):
            if self.data is None:
                return pd.DataFrame()

            if not text or not text.strip():
                filtered_data = self.data.copy()
            else:
                try:
                    mask = self.data.astype(str).apply(
                        lambda row: row.str.contains(text, case=False, na=False).any(), axis=1
                    )
                    filtered_data = self.data[mask].copy()
                except Exception as e:
                    print(f"Filter error: {e}")
                    filtered_data = pd.DataFrame()

        # Emit filtered data signal (outside mutex lock)
        self.data_filtered.emit(filtered_data)
        return filtered_data

    def get_record_by_epd(self, epd_id: str) -> Optional[Dict]:
        """Get a specific EPD record by ID (thread-safe)"""
        with QMutexLocker(self._data_mutex):
            if self.data is None:
                return None

            try:
                matches = self.data[self.data['EPD'] == epd_id]
                if not matches.empty:
                    return matches.iloc[0].to_dict()
            except Exception as e:
                print(f"Error retrieving EPD record {epd_id}: {e}")

        return None

    def get_records_by_cable(self, cable_type: str) -> pd.DataFrame:
        """Get all EPD records for a specific cable type (thread-safe)"""
        with QMutexLocker(self._data_mutex):
            if self.data is None:
                return pd.DataFrame()

            try:
                return self.data[self.data['Cable'] == cable_type].copy()
            except Exception as e:
                print(f"Error filtering by cable {cable_type}: {e}")
                return pd.DataFrame()

    def get_statistics(self) -> Dict[str, Any]:
        """Get dataset statistics (thread-safe)"""
        with QMutexLocker(self._data_mutex):
            if self.data is None:
                return {'total_records': 0, 'loaded': False}

            try:
                stats = {
                    'total_records': len(self.data),
                    'unique_cables': self.data['Cable'].nunique() if 'Cable' in self.data.columns else 0,
                    'unique_epds': self.data['EPD'].nunique() if 'EPD' in self.data.columns else 0,
                    'avg_awg': self.data['AWG'].mean() if 'AWG' in self.data.columns else 0,
                    'loaded': True
                }
                return stats
            except Exception as e:
                print(f"Error calculating statistics: {e}")
                return {'total_records': 0, 'loaded': False, 'error': str(e)}

    def is_data_loaded(self) -> bool:
        """Check if data is loaded (thread-safe)"""
        with QMutexLocker(self._data_mutex):
            return self.data is not None and not self.data.empty

    def refresh_data(self):
        """Refresh data from source"""
        # Cancel any ongoing load
        if self._worker:
            self._worker.cancel()

        # Clear existing data
        with QMutexLocker(self._data_mutex):
            self.data = None

        # Reload
        self.load_async()

    def export_data(self, file_path: str = None) -> bool:
        """Export data to file (thread-safe)"""
        with QMutexLocker(self._data_mutex):
            if self.data is None:
                return False

            try:
                if file_path:
                    if file_path.endswith('.csv'):
                        self.data.to_csv(file_path, index=False)
                    elif file_path.endswith('.xlsx'):
                        self.data.to_excel(file_path, index=False)
                    else:
                        return False
                return True
            except Exception as e:
                print(f"Export error: {e}")
                return False

    def cleanup(self):
        """Cleanup resources before deletion"""
        # Cancel any ongoing operations
        if self._worker:
            self._worker.cancel()

        # Wait for thread to finish
        if self._thread and self._thread.isRunning():
            self._thread.quit()
            self._thread.wait(5000)  # Wait max 5 seconds

# class EpdModel(BaseModel):
#     """Model for managing EPD (Electronic Parts Data) analysis data"""

#     def __init__(self, context: AppContext):
#         super().__init__(context)
#         self.current_breakout_wire = None
#         self.current_connection = None

#     def _initialize_data(self):
#         """Initialize EPD model data"""
#         # Initialize with sample breakout wire data
#         self._data = {
#             'breakout_wires': {
#                 'BreakoutWire1': {
#                     'name': 'BreakoutWire1',
#                     'connections': {
#                         'Connection1': {
#                             'name': 'Connection1',
#                             'pin_data': {},
#                             'wire_color': 'Red',
#                             'signal_type': 'Power'
#                         },
#                         'Connection2': {
#                             'name': 'Connection2',
#                             'pin_data': {},
#                             'wire_color': 'Blue',
#                             'signal_type': 'Data'
#                         },
#                         'Connection3': {
#                             'name': 'Connection3',
#                             'pin_data': {},
#                             'wire_color': 'Green',
#                             'signal_type': 'Ground'
#                         }
#                     },
#                     'pin_data': {
#                         'pin_count': 25,
#                         'pins': {}
#                     },
#                     'status': 'Active',
#                     'manufacturer': 'Generic',
#                     'part_number': 'BW001'
#                 },
#                 'BreakoutWire2': {
#                     'name': 'BreakoutWire2',
#                     'connections': {
#                         'Connection1': {
#                             'name': 'Connection1',
#                             'pin_data': {},
#                             'wire_color': 'Yellow',
#                             'signal_type': 'Signal'
#                         },
#                         'Connection2': {
#                             'name': 'Connection2',
#                             'pin_data': {},
#                             'wire_color': 'Orange',
#                             'signal_type': 'Control'
#                         },
#                         'Connection3': {
#                             'name': 'Connection3',
#                             'pin_data': {},
#                             'wire_color': 'Purple',
#                             'signal_type': 'Data'
#                         }
#                     },
#                     'pin_data': {
#                         'pin_count': 15,
#                         'pins': {}
#                     },
#                     'status': 'Active',
#                     'manufacturer': 'Generic',
#                     'part_number': 'BW002'
#                 }
#             },
#             'gys_data': {
#                 'enabled': True,
#                 'data_points': {}
#             }
#         }

#         # Initialize additional breakout wires
#         for i in range(3, 6):
#             breakout_wire_name = f'BreakoutWire{i}'
#             self._data['breakout_wires'][breakout_wire_name] = {
#                 'name': breakout_wire_name,
#                 'connections': {
#                     f'Connection{j}': {
#                         'name': f'Connection{j}',
#                         'pin_data': {},
#                         'wire_color': f'Color{j}',
#                         'signal_type': f'Type{j}'
#                     } for j in range(1, 4)
#                 },
#                 'pin_data': {
#                     'pin_count': 9,
#                     'pins': {}
#                 },
#                 'status': 'Active',
#                 'manufacturer': 'Generic',
#                 'part_number': f'BW00{i}'
#             }

#     def get_breakout_wire_list(self) -> List[str]:
#         """Get list of all breakout wire names"""
#         return list(self._data.get('breakout_wires', {}).keys())

#     def get_breakout_wire_data(self, breakout_wire_name: str) -> Optional[Dict]:
#         """Get data for a specific breakout wire"""
#         return self._data.get('breakout_wires', {}).get(breakout_wire_name)

#     def get_connection_data(self, breakout_wire_name: str, connection_name: str) -> Optional[Dict]:
#         """Get data for a specific connection"""
#         breakout_wire = self.get_breakout_wire_data(breakout_wire_name)
#         if breakout_wire:
#             return breakout_wire.get('connections', {}).get(connection_name)
#         return None

#     def set_current_breakout_wire(self, breakout_wire_name: str):
#         """Set the currently selected breakout wire"""
#         self.current_breakout_wire = breakout_wire_name
#         self.set_data('current_breakout_wire', breakout_wire_name)

#     def set_current_connection(self, breakout_wire_name: str, connection_name: str):
#         """Set the currently selected connection"""
#         self.current_breakout_wire = breakout_wire_name
#         self.current_connection = connection_name
#         self.set_data('current_breakout_wire', breakout_wire_name)
#         self.set_data('current_connection', connection_name)

#     def update_breakout_wire_pin_data(self, breakout_wire_name: str, pin_data: Dict):
#         """Update pin data for a breakout wire"""
#         if breakout_wire_name in self._data.get('breakout_wires', {}):
#             self._data['breakout_wires'][breakout_wire_name]['pin_data'].update(pin_data)
#             self.data_updated.emit({
#                 'breakout_wire': breakout_wire_name,
#                 'pin_data': pin_data
#             })
#         else:
#             raise ValueError(f"Breakout wire '{breakout_wire_name}' not found")

#     def update_connection_data(self, breakout_wire_name: str, connection_name: str, connection_data: Dict):
#         """Update data for a specific connection"""
#         breakout_wire = self.get_breakout_wire_data(breakout_wire_name)
#         if breakout_wire and connection_name in breakout_wire.get('connections', {}):
#             breakout_wire['connections'][connection_name].update(connection_data)
#             self.data_updated.emit({
#                 'breakout_wire': breakout_wire_name,
#                 'connection': connection_name,
#                 'connection_data': connection_data
#             })
#         else:
#             raise ValueError(f"Connection '{connection_name}' not found in breakout wire '{breakout_wire_name}'")

#     def add_breakout_wire(self, breakout_wire_name: str, breakout_wire_data: Dict):
#         """Add a new breakout wire"""
#         if breakout_wire_name in self._data.get('breakout_wires', {}):
#             raise ValueError(f"Breakout wire '{breakout_wire_name}' already exists")

#         if 'breakout_wires' not in self._data:
#             self._data['breakout_wires'] = {}

#         self._data['breakout_wires'][breakout_wire_name] = breakout_wire_data
#         self.data_updated.emit({
#             'action': 'add_breakout_wire',
#             'breakout_wire': breakout_wire_name,
#             'data': breakout_wire_data
#         })

#     def remove_breakout_wire(self, breakout_wire_name: str):
#         """Remove a breakout wire"""
#         if breakout_wire_name not in self._data.get('breakout_wires', {}):
#             raise ValueError(f"Breakout wire '{breakout_wire_name}' not found")

#         del self._data['breakout_wires'][breakout_wire_name]
#         self.data_updated.emit({
#             'action': 'remove_breakout_wire',
#             'breakout_wire': breakout_wire_name
#         })

#     def get_gys_data(self) -> Dict:
#         """Get GYS data"""
#         return self._data.get('gys_data', {})

#     def update_gys_data(self, gys_data: Dict):
#         """Update GYS data"""
#         if 'gys_data' not in self._data:
#             self._data['gys_data'] = {}

#         self._data['gys_data'].update(gys_data)
#         self.data_updated.emit({
#             'action': 'update_gys_data',
#             'gys_data': gys_data
#         })

#     def toggle_gys_data_visibility(self, visible: bool):
#         """Toggle GYS data visibility"""
#         if 'gys_data' not in self._data:
#             self._data['gys_data'] = {}

#         self._data['gys_data']['enabled'] = visible
#         self.data_updated.emit({
#             'action': 'toggle_gys_visibility',
#             'visible': visible
#         })

#     def validate_breakout_wire_data(self, breakout_wire_name: str) -> Dict:
#         """Validate breakout wire data"""
#         breakout_wire = self.get_breakout_wire_data(breakout_wire_name)
#         if not breakout_wire:
#             return {'valid': False, 'errors': [f'Breakout wire {breakout_wire_name} not found']}

#         errors = []

#         # Check if connections exist
#         connections = breakout_wire.get('connections', {})
#         if not connections:
#             errors.append('No connections defined')

#         # Check pin data
#         pin_data = breakout_wire.get('pin_data', {})
#         if not pin_data.get('pin_count'):
#             errors.append('Pin count not defined')

#         return {
#             'valid': len(errors) == 0,
#             'errors': errors,
#             'warnings': []
#         }
