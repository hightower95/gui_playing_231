"""Summary tab - Shows input requirements and status"""
from typing import List, Dict
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from .styles import TABLE_STYLE


class SummaryTab(QWidget):
    """Summary tab showing report configuration status"""

    def __init__(self, required_inputs: List[str], parent=None):
        super().__init__(parent)
        self.required_inputs = required_inputs
        self.input_values: Dict[str, str] = {}
        self._setup_ui()

    def _setup_ui(self):
        """Setup summary tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        header_label = QLabel("Report Configuration")
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setStyleSheet("color: #e3e3e3;")
        layout.addWidget(header_label)

        # Table showing input status
        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(4)
        self.summary_table.setHorizontalHeaderLabels([
            "Status", "Input", "Description", "Value"
        ])
        self.summary_table.horizontalHeader().setStretchLastSection(True)
        self.summary_table.setColumnWidth(0, 80)
        self.summary_table.setColumnWidth(1, 200)
        self.summary_table.setColumnWidth(2, 300)
        self.summary_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self.summary_table.setStyleSheet(TABLE_STYLE)

        # Add required inputs
        self.summary_table.setRowCount(len(self.required_inputs))
        for i, input_name in enumerate(self.required_inputs):
            # Status circle
            status_item = QTableWidgetItem("⭕")
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.summary_table.setItem(i, 0, status_item)

            # Input name
            # Store base_input_name without '*' for later retrieval
            base_input_name = input_name
            name_item = QTableWidgetItem(input_name + " *")
            name_item.setData(Qt.ItemDataRole.UserRole, base_input_name)  # Store base name
            self.summary_table.setItem(i, 1, name_item)

            # Description
            desc_item = QTableWidgetItem(
                self._get_input_description(input_name))
            self.summary_table.setItem(i, 2, desc_item)

            # Value (initially "Not selected")
            value_item = QTableWidgetItem("Not selected")
            value_item.setForeground(Qt.GlobalColor.gray)
            self.summary_table.setItem(i, 3, value_item)

        layout.addWidget(self.summary_table, stretch=1)

        # Footer note
        note_label = QLabel(
            "* Required fields must be completed before running the report")
        note_label.setStyleSheet(
            "color: #d16969; font-size: 11px; font-style: italic;")
        layout.addWidget(note_label)

    def update_input_value(self, input_name: str, value: str):
        """Update an input value in the table"""
        self.input_values[input_name] = value

        # Find row for this input
        for i, req_input in enumerate(self.required_inputs):
            if req_input == input_name:
                # Update status
                status_item = self.summary_table.item(i, 0)
                status_item.setText("✅" if value else "⭕")

                # Update value
                value_item = self.summary_table.item(i, 3)
                if value:
                    value_item.setText(value)
                    value_item.setForeground(Qt.GlobalColor.white)
                else:
                    value_item.setText("Not selected")
                    value_item.setForeground(Qt.GlobalColor.gray)
                break

    def _get_input_description(self, input_name: str) -> str:
        """Get description for an input parameter"""
        if "parts" in input_name.lower() or "list" in input_name.lower():
            return "Master parts list for comparison"
        elif "inventory" in input_name.lower():
            return "Current inventory snapshot"
        elif "bom" in input_name.lower():
            return "Optional BOM for cross-reference"
        else:
            return "Required input for report generation"
