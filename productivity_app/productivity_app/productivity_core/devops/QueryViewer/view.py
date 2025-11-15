"""
Query Viewer View - UI for viewing and executing Azure DevOps queries
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QTableWidget, QTableWidgetItem, QSplitter, QComboBox, QLineEdit
)
from PySide6.QtCore import Qt, Signal
from ...ui.components import (
    StandardButton, StandardLabel, TextStyle, StandardInput, ButtonRole
)


class QueryViewerView(QWidget):
    """View for Azure DevOps Query Viewer"""

    # Signals
    execute_query_requested = Signal(str)  # query ID or WIQL
    connect_requested = Signal(str, str, str)  # organization, project, PAT
    clear_requested = Signal()

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header
        header = StandardLabel(
            "Azure DevOps Query Viewer", style=TextStyle.TITLE)
        layout.addWidget(header)

        # Description
        desc = StandardLabel(
            "Connect to Azure DevOps and execute work item queries",
            style=TextStyle.LABEL
        )
        desc.setStyleSheet("color: gray;")
        layout.addWidget(desc)

        # Connection section
        self._create_connection_section(layout)

        # Create splitter for query input and results
        splitter = QSplitter(Qt.Vertical)

        # Top section - Query input
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Query type selector
        type_row = QHBoxLayout()
        type_row.addWidget(StandardLabel("Query Type:", style=TextStyle.LABEL))
        self.query_type_combo = QComboBox()
        self.query_type_combo.addItems(["Saved Query (ID)", "WIQL Query"])
        self.query_type_combo.currentTextChanged.connect(
            self._on_query_type_changed)
        type_row.addWidget(self.query_type_combo)
        type_row.addStretch()
        top_layout.addLayout(type_row)

        # Query input area
        query_label = StandardLabel("Query:", style=TextStyle.LABEL)
        top_layout.addWidget(query_label)

        self.query_input = QTextEdit()
        self.query_input.setPlaceholderText(
            "Enter Azure DevOps Query ID or WIQL query...\n\n"
            "Example Query ID:\n"
            "12345678-1234-1234-1234-123456789012\n\n"
            "Example WIQL:\n"
            "SELECT [System.Id], [System.Title], [System.State]\n"
            "FROM WorkItems\n"
            "WHERE [System.WorkItemType] = 'Bug'\n"
            "AND [System.State] = 'Active'\n"
            "ORDER BY [System.CreatedDate] DESC"
        )
        self.query_input.setMinimumHeight(150)
        top_layout.addWidget(self.query_input)

        # Buttons
        button_row = QHBoxLayout()
        button_row.addStretch()

        self.clear_button = StandardButton("Clear")
        self.clear_button.clicked.connect(self._on_clear)
        button_row.addWidget(self.clear_button)

        self.execute_button = StandardButton(
            "Execute Query", role=ButtonRole.PRIMARY)
        self.execute_button.clicked.connect(self._on_execute)
        self.execute_button.setEnabled(False)  # Disabled until connected
        button_row.addWidget(self.execute_button)

        top_layout.addLayout(button_row)

        splitter.addWidget(top_widget)

        # Bottom section - Results
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        results_label = StandardLabel("Results:", style=TextStyle.LABEL)
        bottom_layout.addWidget(results_label)

        # Status label
        self.status_label = StandardLabel("", style=TextStyle.LABEL)
        self.status_label.setStyleSheet("color: gray; font-style: italic;")
        bottom_layout.addWidget(self.status_label)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        bottom_layout.addWidget(self.results_table)

        splitter.addWidget(bottom_widget)

        # Set splitter sizes (60% input, 40% results)
        splitter.setSizes([600, 400])

        layout.addWidget(splitter)

        # Initialize status
        self.set_status(
            "Not connected. Please enter Azure DevOps credentials.")

    def _create_connection_section(self, parent_layout):
        """Create the Azure DevOps connection section"""
        from ...ui.components import StandardGroupBox

        conn_group = StandardGroupBox("Azure DevOps Connection")
        conn_layout = QVBoxLayout()
        conn_layout.setSpacing(8)

        # Organization
        org_row = QHBoxLayout()
        org_row.addWidget(StandardLabel(
            "Organization:", style=TextStyle.LABEL))
        self.org_input = StandardInput(placeholder="organization-name")
        self.org_input.setToolTip("Your Azure DevOps organization name")
        org_row.addWidget(self.org_input)
        conn_layout.addLayout(org_row)

        # Project
        proj_row = QHBoxLayout()
        proj_row.addWidget(StandardLabel("Project:", style=TextStyle.LABEL))
        self.project_input = StandardInput(placeholder="project-name")
        self.project_input.setToolTip("Your Azure DevOps project name")
        proj_row.addWidget(self.project_input)
        conn_layout.addLayout(proj_row)

        # Personal Access Token
        pat_row = QHBoxLayout()
        pat_row.addWidget(StandardLabel("PAT:", style=TextStyle.LABEL))
        self.pat_input = QLineEdit()
        self.pat_input.setPlaceholderText("Personal Access Token")
        self.pat_input.setEchoMode(QLineEdit.Password)
        self.pat_input.setToolTip(
            "Personal Access Token with Work Items (Read) permission")
        pat_row.addWidget(self.pat_input)
        conn_layout.addLayout(pat_row)

        # Connect button
        connect_btn_row = QHBoxLayout()
        connect_btn_row.addStretch()
        self.connect_button = StandardButton(
            "Connect", role=ButtonRole.SUCCESS)
        self.connect_button.clicked.connect(self._on_connect)
        connect_btn_row.addWidget(self.connect_button)
        conn_layout.addLayout(connect_btn_row)

        # Connection status
        self.connection_status = StandardLabel("", style=TextStyle.NOTES)
        conn_layout.addWidget(self.connection_status)

        conn_group.setLayout(conn_layout)
        parent_layout.addWidget(conn_group)

    def _on_connect(self):
        """Handle connect button click"""
        org = self.org_input.text().strip()
        project = self.project_input.text().strip()
        pat = self.pat_input.text().strip()

        if not org or not project or not pat:
            self.set_connection_status(
                "Please fill in all connection fields", is_error=True)
            return

        self.connect_requested.emit(org, project, pat)

    def _on_query_type_changed(self, query_type: str):
        """Handle query type change"""
        if query_type == "Saved Query (ID)":
            self.query_input.setPlaceholderText(
                "Enter Query ID (GUID)...\n\n"
                "Example:\n"
                "12345678-1234-1234-1234-123456789012"
            )
        else:  # WIQL Query
            self.query_input.setPlaceholderText(
                "Enter WIQL query...\n\n"
                "Example:\n"
                "SELECT [System.Id], [System.Title], [System.State]\n"
                "FROM WorkItems\n"
                "WHERE [System.WorkItemType] = 'Bug'\n"
                "AND [System.State] = 'Active'\n"
                "ORDER BY [System.CreatedDate] DESC"
            )

    def _on_execute(self):
        """Handle execute button click"""
        query = self.query_input.toPlainText().strip()
        if query:
            self.execute_query_requested.emit(query)
        else:
            self.set_status("Error: Query is empty", is_error=True)

    def _on_clear(self):
        """Handle clear button click"""
        self.query_input.clear()
        self.clear_requested.emit()

    def set_status(self, message: str, is_error: bool = False):
        """Set status message

        Args:
            message: Status message to display
            is_error: True if this is an error message
        """
        self.status_label.setText(message)
        if is_error:
            self.status_label.setStyleSheet(
                "color: red; font-style: italic; font-weight: bold;")
        else:
            self.status_label.setStyleSheet(
                "color: gray; font-style: italic;")

    def set_connection_status(self, message: str, is_error: bool = False):
        """Set connection status message

        Args:
            message: Connection status message
            is_error: True if this is an error message
        """
        self.connection_status.setText(message)
        if is_error:
            self.connection_status.setStyleSheet(
                "color: red; font-style: italic;")
        else:
            self.connection_status.setStyleSheet(
                "color: green; font-style: italic;")

    def set_connected(self, connected: bool):
        """Update UI based on connection status

        Args:
            connected: True if connected to Azure DevOps
        """
        self.execute_button.setEnabled(connected)
        self.connect_button.setEnabled(not connected)
        self.org_input.setEnabled(not connected)
        self.project_input.setEnabled(not connected)
        self.pat_input.setEnabled(not connected)

        if connected:
            self.set_connection_status("✓ Connected to Azure DevOps")
            self.set_status("Ready to execute queries")
        else:
            self.set_connection_status("")
            self.set_status("Not connected")

    def display_results(self, headers: list, rows: list):
        """Display query results in the table

        Args:
            headers: List of column headers
            rows: List of row data (each row is a list of values)
        """
        self.results_table.clear()
        self.results_table.setRowCount(len(rows))
        self.results_table.setColumnCount(len(headers))
        self.results_table.setHorizontalHeaderLabels(headers)

        # Populate table
        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                self.results_table.setItem(row_idx, col_idx, item)

        # Resize columns to content
        self.results_table.resizeColumnsToContents()

        # Update status
        self.set_status(
            f"Query executed successfully. {len(rows)} row(s) returned.")

    def clear_results(self):
        """Clear the results table"""
        self.results_table.clear()
        self.results_table.setRowCount(0)
        self.results_table.setColumnCount(0)
        self.set_status("Results cleared")

    def get_query(self) -> str:
        """Get the current query text"""
        return self.query_input.toPlainText().strip()

    def get_query_type(self) -> str:
        """Get the selected query type"""
        return self.query_type_combo.currentText()
