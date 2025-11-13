"""
Query Viewer Model - Data management for Azure DevOps query execution
"""
from PySide6.QtCore import QObject, Signal


class QueryViewerModel(QObject):
    """Model for Azure DevOps Query Viewer"""

    # Signals
    query_executed = Signal(list, list)  # headers, rows
    connection_successful = Signal()
    connection_failed = Signal(str)  # error message
    error_occurred = Signal(str)  # error message

    def __init__(self):
        super().__init__()
        self.organization = ""
        self.project = ""
        self.pat = ""
        self.connected = False
        self.last_query = ""
        self.last_results = []

    def connect_to_azure_devops(self, organization: str, project: str, pat: str):
        """Connect to Azure DevOps

        Args:
            organization: Azure DevOps organization name
            project: Project name
            pat: Personal Access Token
        """
        try:
            # Store credentials
            self.organization = organization
            self.project = project
            self.pat = pat

            # TODO: Implement actual Azure DevOps connection test
            # For now, just validate that fields are provided
            if not organization or not project or not pat:
                raise ValueError("All connection fields are required")

            # Test connection (placeholder)
            # In reality, you would use azure.devops Python SDK:
            # from azure.devops.connection import Connection
            # from msrest.authentication import BasicAuthentication
            # credentials = BasicAuthentication('', pat)
            # connection = Connection(base_url=f'https://dev.azure.com/{organization}', creds=credentials)
            # core_client = connection.clients.get_core_client()
            # project_obj = core_client.get_project(project)

            self.connected = True
            self.connection_successful.emit()

        except Exception as e:
            self.connected = False
            error_msg = f"Connection failed: {str(e)}"
            self.connection_failed.emit(error_msg)

    def execute_query(self, query: str, query_type: str = "WIQL Query"):
        """Execute an Azure DevOps query

        Args:
            query: The query to execute (Query ID or WIQL)
            query_type: Type of query ("Saved Query (ID)" or "WIQL Query")
        """
        if not self.connected:
            self.error_occurred.emit("Not connected to Azure DevOps")
            return

        try:
            # Store last query
            self.last_query = query

            # Execute based on type
            if query_type == "Saved Query (ID)":
                results = self._execute_saved_query(query)
            else:  # WIQL Query
                results = self._execute_wiql_query(query)

            self.last_results = results
            headers, rows = results
            self.query_executed.emit(headers, rows)

        except Exception as e:
            error_msg = f"Error executing query: {str(e)}"
            self.error_occurred.emit(error_msg)

    def _execute_saved_query(self, query_id: str):
        """Execute a saved Azure DevOps query by ID

        Args:
            query_id: The GUID of the saved query

        Returns:
            Tuple of (headers, rows)
        """
        # TODO: Implement actual Azure DevOps saved query execution
        # from azure.devops.v7_0.work_item_tracking.models import Wiql
        # wit_client = self.connection.clients.get_work_item_tracking_client()
        # query_result = wit_client.query_by_id(query_id)

        # Placeholder implementation
        headers = ["ID", "Title", "State", "Assigned To", "Work Item Type"]
        rows = [
            ["12345", "Sample Bug", "Active", "user@example.com", "Bug"],
            ["12346", "Sample Task", "New", "user2@example.com", "Task"],
            ["12347", "Sample Feature", "In Progress",
                "user@example.com", "Feature"],
        ]

        return (headers, rows)

    def _execute_wiql_query(self, wiql: str):
        """Execute a WIQL query

        Args:
            wiql: The WIQL query string

        Returns:
            Tuple of (headers, rows)
        """
        # TODO: Implement actual WIQL query execution
        # from azure.devops.v7_0.work_item_tracking.models import Wiql
        # wit_client = self.connection.clients.get_work_item_tracking_client()
        # wiql_object = Wiql(query=wiql)
        # query_result = wit_client.query_by_wiql(wiql_object)
        # work_items = wit_client.get_work_items(ids=[item.id for item in query_result.work_items])

        # Placeholder implementation
        headers = ["ID", "Title", "State", "Assigned To",
                   "Work Item Type", "Created Date"]
        rows = [
            ["12345", "Implement feature X", "Active",
                "john.doe@example.com", "Bug", "2025-10-15"],
            ["12346", "Fix login issue", "New",
                "jane.smith@example.com", "Bug", "2025-10-16"],
            ["12347", "Update documentation", "Active",
                "john.doe@example.com", "Task", "2025-10-17"],
            ["12348", "Add validation", "In Progress",
                "bob.jones@example.com", "Task", "2025-10-18"],
        ]

        return (headers, rows)

    def clear(self):
        """Clear stored query and results"""
        self.last_query = ""
        self.last_results = []
