"""
Query Viewer Presenter - Business logic for Azure DevOps query viewer
"""
from PySide6.QtCore import QObject
from .model import QueryViewerModel
from .view import QueryViewerView


class QueryViewerPresenter(QObject):
    """Presenter for Azure DevOps Query Viewer"""

    def __init__(self, context):
        super().__init__()
        self.context = context
        self.model = QueryViewerModel()
        self.view = QueryViewerView()

        # Connect view signals to presenter
        self.view.connect_requested.connect(self._on_connect)
        self.view.execute_query_requested.connect(self._on_execute_query)
        self.view.clear_requested.connect(self._on_clear)

        # Connect model signals to view updates
        self.model.connection_successful.connect(self._on_connection_successful)
        self.model.connection_failed.connect(self._on_connection_failed)
        self.model.query_executed.connect(self._on_query_executed)
        self.model.error_occurred.connect(self._on_error)

    def _on_connect(self, organization: str, project: str, pat: str):
        """Handle connection request from view

        Args:
            organization: Azure DevOps organization name
            project: Project name
            pat: Personal Access Token
        """
        self.view.set_connection_status("Connecting...", is_error=False)
        self.model.connect_to_azure_devops(organization, project, pat)

    def _on_connection_successful(self):
        """Handle successful connection to Azure DevOps"""
        self.view.set_connected(True)

    def _on_connection_failed(self, error_message: str):
        """Handle failed connection to Azure DevOps

        Args:
            error_message: Error message from model
        """
        self.view.set_connection_status(error_message, is_error=True)
        self.view.set_connected(False)

    def _on_execute_query(self, query: str):
        """Handle query execution request from view

        Args:
            query: The query to execute
        """
        query_type = self.view.get_query_type()
        self.view.set_status(f"Executing {query_type} query...")

        # Execute in model
        self.model.execute_query(query, query_type)

    def _on_query_executed(self, headers: list, rows: list):
        """Handle successful query execution

        Args:
            headers: Column headers
            rows: Result rows
        """
        self.view.display_results(headers, rows)

    def _on_error(self, error_message: str):
        """Handle error from model

        Args:
            error_message: Error message to display
        """
        self.view.set_status(error_message, is_error=True)

    def _on_clear(self):
        """Handle clear request from view"""
        self.view.clear_results()
        self.model.clear()

    def start_loading(self):
        """Initialize the presenter - called during tab loading"""
        pass  # Nothing to load on startup for now
