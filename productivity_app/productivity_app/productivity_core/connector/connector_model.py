"""
Connector Model - Data management for connector lookups with threading support
"""
from typing import Dict, List, Any, Optional
from PySide6.QtCore import QObject, Signal, QThread, QMutex, QMutexLocker
from ..core.base_model import BaseModel
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
            'connectors': [
                {
                    'Part Number': 'D38999/26WA35PN',
                    'Part Code': 'D38999-26WA35PN',
                    'Minified Part Code': 'D3899926WA35PN',
                    'Material': 'Aluminum',
                    'Database Status': 'Active',
                    'Family': 'D38999',
                    'Shell Type': '26 - Plug',
                    'Shell Size': '10',
                    'Insert Arrangement': 'A - 1',
                    'Socket Type': 'Type A',
                    'Keying': 'A'
                },
                {
                    'Part Number': 'D38999/24WB35SN',
                    'Part Code': 'D38999-24WB35SN',
                    'Minified Part Code': 'D3899924WB35SN',
                    'Material': 'Stainless Steel',
                    'Database Status': 'Active',
                    'Family': 'D38999',
                    'Shell Type': '24 - Receptacle',
                    'Shell Size': '12',
                    'Insert Arrangement': 'B - 2',
                    'Socket Type': 'Type B',
                    'Keying': 'B'
                },
                {
                    'Part Number': 'D38999/20WC10PN',
                    'Part Code': 'D38999-20WC10PN',
                    'Minified Part Code': 'D3899920WC10PN',
                    'Material': 'Aluminum',
                    'Database Status': 'Obsolete',
                    'Family': 'D38999',
                    'Shell Type': '20 - Receptacle B',
                    'Shell Size': '14',
                    'Insert Arrangement': 'C - 3',
                    'Socket Type': 'Type A',
                    'Keying': 'C'
                },
                {
                    'Part Number': 'VG95234F10A001PN',
                    'Part Code': 'VG95234-F10A001PN',
                    'Minified Part Code': 'VG95234F10A001PN',
                    'Material': 'Composite',
                    'Database Status': 'Active',
                    'Family': 'VG',
                    'Shell Type': '26 - Plug',
                    'Shell Size': '8',
                    'Insert Arrangement': 'A - 1',
                    'Socket Type': 'Type C',
                    'Keying': 'D'
                },
                {
                    'Part Number': 'VG95234F12B002SN',
                    'Part Code': 'VG95234-F12B002SN',
                    'Minified Part Code': 'VG95234F12B002SN',
                    'Material': 'Stainless Steel',
                    'Database Status': 'Active',
                    'Family': 'VG',
                    'Shell Type': '24 - Receptacle',
                    'Shell Size': '9',
                    'Insert Arrangement': 'B - 2',
                    'Socket Type': 'Type D',
                    'Keying': 'E'
                },
                {
                    'Part Number': 'D38999/26WA50PN',
                    'Part Code': 'D38999-26WA50PN',
                    'Minified Part Code': 'D3899926WA50PN',
                    'Material': 'Aluminum',
                    'Database Status': 'Active',
                    'Family': 'D38999',
                    'Shell Type': '26 - Plug',
                    'Shell Size': '16',
                    'Insert Arrangement': 'A - 1',
                    'Socket Type': 'Type B',
                    'Keying': 'A'
                },
                {
                    'Part Number': 'MS3470L16-10P',
                    'Part Code': 'MS3470L16-10P',
                    'Minified Part Code': 'MS3470L1610P',
                    'Material': 'Aluminum',
                    'Database Status': 'Active',
                    'Family': 'MS',
                    'Shell Type': '26 - Plug',
                    'Shell Size': '16',
                    'Insert Arrangement': 'A - 10',
                    'Socket Type': 'Type A',
                    'Keying': 'Normal'
                },
                {
                    'Part Number': 'MS3476L16-10S',
                    'Part Code': 'MS3476L16-10S',
                    'Minified Part Code': 'MS3476L1610S',
                    'Material': 'Aluminum',
                    'Database Status': 'Active',
                    'Family': 'MS',
                    'Shell Type': '24 - Receptacle',
                    'Shell Size': '16',
                    'Insert Arrangement': 'A - 10',
                    'Socket Type': 'Type A',
                    'Keying': 'Normal'
                },
                {
                    'Part Number': 'EN3645-003-12',
                    'Part Code': 'EN3645-003-12',
                    'Minified Part Code': 'EN364500312',
                    'Material': 'Composite',
                    'Database Status': 'Active',
                    'Family': 'EN',
                    'Shell Type': '26 - Plug',
                    'Shell Size': '12',
                    'Insert Arrangement': 'B - 3',
                    'Socket Type': 'Type B',
                    'Keying': 'F'
                },
                {
                    'Part Number': 'MIL-DTL-38999/26WA35PN',
                    'Part Code': 'MIL-DTL-38999-26WA35PN',
                    'Minified Part Code': 'MILDTL3899926WA35PN',
                    'Material': 'Stainless Steel',
                    'Database Status': 'Active',
                    'Family': 'MIL',
                    'Shell Type': '26 - Plug',
                    'Shell Size': '10',
                    'Insert Arrangement': 'A - 35',
                    'Socket Type': 'Type A',
                    'Keying': 'A'
                }
            ],
            'families': ['D38999', 'VG', 'MS', 'EN', 'MIL'],
            'shell_types': ['26 - Plug', '24 - Receptacle', '20 - Receptacle B'],
            'insert_arrangements': ['A - 1', 'B - 2', 'C - 3', 'A - 10', 'B - 3', 'A - 35'],
            'socket_types': ['Type A', 'Type B', 'Type C', 'Type D'],
            'keyings': ['A', 'B', 'C', 'D', 'E', 'F', 'N']
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

    def get_families(self) -> List[str]:
        """Get list of available families (thread-safe)"""
        with QMutexLocker(self._data_mutex):
            if self.data:
                return self.data.get('families', [])
            return []

    def get_shell_types(self) -> List[str]:
        """Get list of available shell types (thread-safe)"""
        with QMutexLocker(self._data_mutex):
            if self.data:
                return self.data.get('shell_types', [])
            return []

    def get_insert_arrangements(self) -> List[str]:
        """Get list of available insert arrangements (thread-safe)"""
        with QMutexLocker(self._data_mutex):
            if self.data:
                return self.data.get('insert_arrangements', [])
            return []

    def get_socket_types(self) -> List[str]:
        """Get list of available socket types (thread-safe)"""
        with QMutexLocker(self._data_mutex):
            if self.data:
                return self.data.get('socket_types', [])
            return []

    def get_keyings(self) -> List[str]:
        """Get list of available keyings (thread-safe)"""
        with QMutexLocker(self._data_mutex):
            if self.data:
                return self.data.get('keyings', [])
            return []

    def get_connectors(self) -> List[Dict]:
        """Get all connectors as list (thread-safe)"""
        with QMutexLocker(self._data_mutex):
            if self.data:
                return self.data.get('connectors', [])
            return []

    def get_available_filter_options(self, selected_standards: List[str] = None) -> Dict[str, List[str]]:
        """Get available filter options based on selected standards (thread-safe)

        Args:
            selected_standards: List of selected standard families (e.g., ['D38999', 'VG'])
                               If None or empty, returns all options

        Returns:
            Dict with keys: shell_types, materials, shell_sizes, insert_arrangements, socket_types, keyings
        """
        with QMutexLocker(self._data_mutex):
            if not self.data:
                return {
                    'shell_types': [],
                    'materials': [],
                    'shell_sizes': [],
                    'insert_arrangements': [],
                    'socket_types': [],
                    'keyings': []
                }

            connectors = self.data.get('connectors', [])

            # If no standards selected, get all available options
            if not selected_standards:
                filtered_connectors = connectors
            else:
                # Filter connectors to only those matching selected standards
                filtered_connectors = [
                    conn for conn in connectors
                    if conn.get('Family') in selected_standards
                ]

            # Extract unique values for each filter from the filtered connectors
            shell_types = sorted(set(
                conn.get('Shell Type') for conn in filtered_connectors
                if conn.get('Shell Type')
            ))

            materials = sorted(set(
                conn.get('Material') for conn in filtered_connectors
                if conn.get('Material')
            ))

            shell_sizes = sorted(set(
                conn.get('Shell Size') for conn in filtered_connectors
                if conn.get('Shell Size')
            ), key=lambda x: int(x) if x.isdigit() else 0)

            insert_arrangements = sorted(set(
                conn.get('Insert Arrangement') for conn in filtered_connectors
                if conn.get('Insert Arrangement')
            ))

            socket_types = sorted(set(
                conn.get('Socket Type') for conn in filtered_connectors
                if conn.get('Socket Type')
            ))

            keyings = sorted(set(
                conn.get('Keying') for conn in filtered_connectors
                if conn.get('Keying')
            ))

            return {
                'shell_types': shell_types,
                'materials': materials,
                'shell_sizes': shell_sizes,
                'insert_arrangements': insert_arrangements,
                'socket_types': socket_types,
                'keyings': keyings
            }

    def find_alternative(self, part_code: str) -> List[Dict[str, Any]]:
        """Find alternative connectors for a given part code

        Args:
            part_code: The part code to find alternatives for

        Returns:
            List of alternative connector dictionaries
        """
        with QMutexLocker(self._data_mutex):
            print(f"Model: Finding alternatives for {part_code}")

            # DUMMY DATA - Replace with actual logic
            dummy_alternatives = [
                {
                    'Part Number': 'ALT-001',
                    'Part Code': 'ALT-D38999-001',
                    'Material': 'Aluminum',
                    'Reason': 'Same shell size, different keying'
                },
                {
                    'Part Number': 'ALT-002',
                    'Part Code': 'ALT-D38999-002',
                    'Material': 'Stainless Steel',
                    'Reason': 'Same insert arrangement'
                }
            ]

            return dummy_alternatives

    def find_opposite(self, part_code: str) -> Optional[Dict[str, Any]]:
        """Find opposite (mating) connector for a given part code

        Args:
            part_code: The part code to find opposite for

        Returns:
            Opposite connector dictionary or None if not found
        """
        with QMutexLocker(self._data_mutex):
            print(f"Model: Finding opposite for {part_code}")

            # DUMMY DATA - Replace with actual logic
            dummy_opposite = {
                'Part Number': 'OPP-001',
                'Part Code': 'OPP-D38999-001',
                'Material': 'Aluminum',
                'Shell Type': '24 - Receptacle',  # Opposite of plug
                'Reason': 'Mating connector (plug <-> receptacle)'
            }

            return dummy_opposite

    def filter_connectors(self, filters: Dict) -> List[Dict]:
        """Filter connectors based on criteria (thread-safe)"""
        with QMutexLocker(self._data_mutex):
            if not self.data:
                return []

            connectors = self.data.get('connectors', [])
            results = []

            for conn_data in connectors:
                match = True

                # Apply filters (None or empty means "Any" - wildcard)
                if filters.get('family') and filters['family'] != 'Any':
                    if conn_data.get('Family') != filters['family']:
                        match = False

                if filters.get('shell_type') and filters['shell_type'] != 'Any':
                    if conn_data.get('Shell Type') != filters['shell_type']:
                        match = False

                if filters.get('insert_arrangement') and filters['insert_arrangement'] != 'Any':
                    if conn_data.get('Insert Arrangement') != filters['insert_arrangement']:
                        match = False

                if filters.get('socket_type') and filters['socket_type'] != 'Any':
                    if conn_data.get('Socket Type') != filters['socket_type']:
                        match = False

                if filters.get('keying') and filters['keying'] != 'Any':
                    if conn_data.get('Keying') != filters['keying']:
                        match = False

                # Text search across all fields
                if filters.get('search_text'):
                    search_text = filters['search_text'].lower()
                    text_match = False
                    for value in conn_data.values():
                        if search_text in str(value).lower():
                            text_match = True
                            break
                    if not text_match:
                        match = False

                if match:
                    results.append(conn_data)

            return results
