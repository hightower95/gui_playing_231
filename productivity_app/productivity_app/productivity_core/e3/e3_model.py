"""
E3.series Integration Model
Handles loading and caching of E3 project data
"""
import os
import time
from typing import List, Dict, Any, Optional
from PySide6.QtCore import QObject, Signal, QThread, QMutex, QMutexLocker
import pandas as pd

from .e3_config import (
    E3_COM_PROG_ID,
    E3_CACHE_DIRECTORY,
    E3_OPERATION_TIMEOUT,
    E3_CONNECTOR_FIELDS,
    E3_PROGRESS_UPDATE_FREQUENCY
)
from .e3_service import get_e3_service


class E3DataWorker(QObject):
    """Worker class for loading E3 data in a separate thread"""

    # Signals
    progress = Signal(int, str)  # progress_percent, status_message
    # loaded data (dict with projects, connectors, etc.)
    finished = Signal(object)
    error = Signal(str)  # error_message

    def __init__(self, projects: List[str], operation: str = 'list_projects'):
        super().__init__()
        self._is_cancelled = False
        self.projects = projects
        self.operation = operation

    def cancel(self):
        """Cancel the loading operation"""
        self._is_cancelled = True

    def run(self):
        """Execute the data loading in background thread"""
        try:
            if self.operation == 'list_projects':
                self._list_available_projects()
            elif self.operation == 'load_connectors':
                self._load_connector_data()
            else:
                self.error.emit(f"Unknown operation: {self.operation}")

        except Exception as e:
            self.error.emit(f"E3 operation failed: {str(e)}")

    def _list_available_projects(self):
        """List available E3 projects"""
        if self._is_cancelled:
            return

        self.progress.emit(20, "Connecting to E3.series...")
        time.sleep(0.3)

        if self._is_cancelled:
            return

        self.progress.emit(50, "Querying available projects...")
        time.sleep(0.4)

        # TODO: Implement actual E3 COM connection
        # For now, return mock data
        projects = [
            "Project_Alpha_Rev3",
            "Project_Beta_Final",
            "Connector_Library_Master",
            "System_Integration_2024",
            "Prototype_Assembly_v2"
        ]

        if self._is_cancelled:
            return

        self.progress.emit(100, "Projects loaded")
        self.finished.emit({'projects': projects})

    def _load_connector_data(self):
        """Load connector data from E3 projects"""
        if self._is_cancelled:
            return

        self.progress.emit(10, "Connecting to E3.series...")
        time.sleep(0.3)

        if self._is_cancelled:
            return

        total_projects = len(self.projects)
        connectors = []

        for idx, project in enumerate(self.projects):
            if self._is_cancelled:
                return

            progress = 10 + (idx / total_projects) * 70
            self.progress.emit(int(progress), f"Loading project: {project}...")
            time.sleep(0.5)

            # TODO: Implement actual E3 connector extraction
            # For now, add mock connector data for this project
            mock_connectors = self._get_mock_connectors(project)
            connectors.extend(mock_connectors)

        if self._is_cancelled:
            return

        self.progress.emit(90, "Processing connector data...")
        time.sleep(0.2)

        if self._is_cancelled:
            return

        self.progress.emit(
            100, f"Loaded {len(connectors)} connectors from {total_projects} project(s)")
        self.finished.emit({
            'connectors': connectors,
            'projects': self.projects,
            'count': len(connectors)
        })

    def _get_mock_connectors(self, project_name: str) -> List[Dict[str, Any]]:
        """Generate mock connector data for testing"""
        # Mock data based on project name
        base_connectors = [
            {
                'Part Number': f'{project_name[:3].upper()}/001',
                'Part Code': f'{project_name[:3].upper()}-001',
                'Minified Part Code': f'{project_name[:3].upper()}001',
                'Material': 'Aluminum',
                'Database Status': 'Active',
                'Family': project_name[:3].upper(),
                'Shell Type': '26 - Plug',
                'Shell Size': '10',
                'Insert Arrangement': 'A - 1',
                'Socket Type': 'Type A',
                'Keying': 'Normal',
                'E3 Project': project_name
            },
            {
                'Part Number': f'{project_name[:3].upper()}/002',
                'Part Code': f'{project_name[:3].upper()}-002',
                'Minified Part Code': f'{project_name[:3].upper()}002',
                'Material': 'Stainless Steel',
                'Database Status': 'Active',
                'Family': project_name[:3].upper(),
                'Shell Type': '24 - Receptacle',
                'Shell Size': '12',
                'Insert Arrangement': 'B - 2',
                'Socket Type': 'Type B',
                'Keying': 'Keyed',
                'E3 Project': project_name
            }
        ]
        return base_connectors


class E3Model(QObject):
    """Model for E3.series integration"""

    # Signals
    loading_progress = Signal(int, str)  # progress_percent, status_message
    loading_failed = Signal(str)  # error_message
    projects_loaded = Signal(list)  # list of project names
    connectors_loaded = Signal(object)  # connector data (dict or DataFrame)

    def __init__(self, context=None):
        super().__init__()
        self.context = context
        self._data_mutex = QMutex()
        self._worker = None
        self._thread = None
        self._available_projects = []
        self._cache_directory = "e3_caches"

    def load_available_projects_async(self):
        """Load list of available E3 projects asynchronously"""
        with QMutexLocker(self._data_mutex):
            if self._thread and self._thread.isRunning():
                print("E3: Operation already in progress")
                return

            # Create worker and thread
            self._worker = E3DataWorker([], operation='list_projects')
            self._thread = QThread()

            # Move worker to thread
            self._worker.moveToThread(self._thread)

            # Connect signals
            self._thread.started.connect(self._worker.run)
            self._worker.progress.connect(self.loading_progress)
            self._worker.finished.connect(self._on_projects_loaded)
            self._worker.error.connect(self.loading_failed)
            self._worker.finished.connect(self._thread.quit)
            self._worker.finished.connect(self._worker.deleteLater)
            self._thread.finished.connect(self._thread.deleteLater)

            # Start thread
            self._thread.start()

            print("E3: Started loading available projects")

    def load_connector_data_async(self, projects: List[str]):
        """Load connector data from specified E3 projects asynchronously

        Args:
            projects: List of E3 project names to load connectors from
        """
        with QMutexLocker(self._data_mutex):
            if self._thread and self._thread.isRunning():
                print("E3: Operation already in progress")
                return

            if not projects:
                self.loading_failed.emit("No projects specified")
                return

            # Create worker and thread
            self._worker = E3DataWorker(projects, operation='load_connectors')
            self._thread = QThread()

            # Move worker to thread
            self._worker.moveToThread(self._thread)

            # Connect signals
            self._thread.started.connect(self._worker.run)
            self._worker.progress.connect(self.loading_progress)
            self._worker.finished.connect(self._on_connectors_loaded)
            self._worker.error.connect(self.loading_failed)
            self._worker.finished.connect(self._thread.quit)
            self._worker.finished.connect(self._worker.deleteLater)
            self._thread.finished.connect(self._thread.deleteLater)

            # Start thread
            self._thread.start()

            print(
                f"E3: Started loading connectors from {len(projects)} project(s)")

    def _on_projects_loaded(self, data: Dict):
        """Handle projects loaded event"""
        self._available_projects = data.get('projects', [])
        print(f"E3: Loaded {len(self._available_projects)} projects")
        self.projects_loaded.emit(self._available_projects)

    def _on_connectors_loaded(self, data: Dict):
        """Handle connectors loaded event"""
        connectors = data.get('connectors', [])
        print(f"E3: Loaded {len(connectors)} connectors")
        self.connectors_loaded.emit(data)

    def get_available_projects(self) -> List[str]:
        """Get list of available E3 projects (synchronous)

        Returns:
            List of project names
        """
        # TODO: Implement actual E3 COM connection
        # For now, return cached or default projects
        if self._available_projects:
            return self._available_projects

        return [
            "Project_Alpha_Rev3",
            "Project_Beta_Final",
            "Connector_Library_Master",
            "System_Integration_2024",
            "Prototype_Assembly_v2"
        ]

    def get_available_cache_files(self) -> List[str]:
        """Get list of available E3 cache files

        Returns:
            List of cache file paths, sorted by date (newest first)
        """
        from pathlib import Path

        cache_dir = Path(self._cache_directory)
        if not cache_dir.exists():
            print(f"E3: Cache directory not found: {cache_dir}")
            return []

        # Find all CSV files in cache directory
        cache_files = list(cache_dir.glob("*.csv"))

        # Sort by modification time (newest first)
        cache_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        # Return as string paths
        return [str(f) for f in cache_files]

    def cancel_loading(self):
        """Cancel current loading operation"""
        if self._worker:
            self._worker.cancel()
            print("E3: Loading cancelled")

    def is_e3_available(self) -> bool:
        """Check if E3.series COM interface is available

        Returns:
            True if E3 COM is available, False otherwise
        """
        service = get_e3_service()
        if service.connect():
            service.disconnect()
            return True
        return False
