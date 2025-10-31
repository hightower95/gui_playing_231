"""
Comparison Configuration Dialog - Configure how to compare documents
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QComboBox, QGroupBox, QCheckBox, QPushButton,
                               QScrollArea, QWidget, QMessageBox)
from PySide6.QtCore import Qt
from typing import List, Dict, Any


class ComparisonConfigDialog(QDialog):
    """Dialog for configuring comparison settings"""

    def __init__(self, columns: List[str], parent=None):
        super().__init__(parent)
        self.columns = columns
        self.key_column = None
        self.compare_columns = []
        self.show_columns = []

        self.setWindowTitle("Configure Comparison")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        self._setup_ui()

    def _setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)

        # Instructions
        instructions = QLabel(
            "Configure which columns to use for comparison. "
            "The key column uniquely identifies each row."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(instructions)

        # Key column selector
        key_group = QGroupBox("Key Column (Required)")
        key_layout = QVBoxLayout(key_group)

        key_label = QLabel(
            "Select the column that uniquely identifies each row:")
        key_layout.addWidget(key_label)

        self.key_combo = QComboBox()
        self.key_combo.addItems(["-- Select Key Column --"] + self.columns)
        key_layout.addWidget(self.key_combo)

        layout.addWidget(key_group)

        # Columns to compare
        compare_group = QGroupBox("Columns to Compare")
        compare_layout = QVBoxLayout(compare_group)

        compare_label = QLabel(
            "Select which columns to compare for differences:")
        compare_layout.addWidget(compare_label)

        # Scrollable area for checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        self.compare_checkboxes = {}
        for col in self.columns:
            checkbox = QCheckBox(col)
            checkbox.setChecked(True)  # Default: compare all columns
            self.compare_checkboxes[col] = checkbox
            scroll_layout.addWidget(checkbox)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setMinimumHeight(150)
        compare_layout.addWidget(scroll_area)

        # Select/Deselect all buttons
        btn_row = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self._select_all_compare)
        btn_row.addWidget(select_all_btn)

        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self._deselect_all_compare)
        btn_row.addWidget(deselect_all_btn)
        btn_row.addStretch()

        compare_layout.addLayout(btn_row)
        layout.addWidget(compare_group)

        # Columns to show in results
        show_group = QGroupBox("Columns to Show in Results")
        show_layout = QVBoxLayout(show_group)

        show_label = QLabel(
            "Select which columns to display in the results table:")
        show_layout.addWidget(show_label)

        # Scrollable area for show checkboxes
        show_scroll_area = QScrollArea()
        show_scroll_area.setWidgetResizable(True)
        show_scroll_widget = QWidget()
        show_scroll_layout = QVBoxLayout(show_scroll_widget)

        self.show_checkboxes = {}
        for col in self.columns:
            checkbox = QCheckBox(col)
            checkbox.setChecked(True)  # Default: show all columns
            self.show_checkboxes[col] = checkbox
            show_scroll_layout.addWidget(checkbox)

        show_scroll_layout.addStretch()
        show_scroll_area.setWidget(show_scroll_widget)
        show_scroll_area.setMinimumHeight(100)
        show_layout.addWidget(show_scroll_area)

        # Select/Deselect all buttons
        show_btn_row = QHBoxLayout()
        show_select_all_btn = QPushButton("Select All")
        show_select_all_btn.clicked.connect(self._select_all_show)
        show_btn_row.addWidget(show_select_all_btn)

        show_deselect_all_btn = QPushButton("Deselect All")
        show_deselect_all_btn.clicked.connect(self._deselect_all_show)
        show_btn_row.addWidget(show_deselect_all_btn)
        show_btn_row.addStretch()

        show_layout.addLayout(show_btn_row)
        layout.addWidget(show_group)

        # Dialog buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("OK")
        ok_btn.setDefault(True)
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                padding: 6px 20px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        ok_btn.clicked.connect(self._on_ok)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

    def _select_all_compare(self):
        """Select all compare checkboxes"""
        for checkbox in self.compare_checkboxes.values():
            checkbox.setChecked(True)

    def _deselect_all_compare(self):
        """Deselect all compare checkboxes"""
        for checkbox in self.compare_checkboxes.values():
            checkbox.setChecked(False)

    def _select_all_show(self):
        """Select all show checkboxes"""
        for checkbox in self.show_checkboxes.values():
            checkbox.setChecked(True)

    def _deselect_all_show(self):
        """Deselect all show checkboxes"""
        for checkbox in self.show_checkboxes.values():
            checkbox.setChecked(False)

    def _on_ok(self):
        """Validate and accept dialog"""
        # Validate key column
        key_text = self.key_combo.currentText()
        if key_text == "-- Select Key Column --":
            QMessageBox.warning(
                self,
                "Key Column Required",
                "Please select a key column to identify unique rows."
            )
            return

        self.key_column = key_text

        # Get selected compare columns
        self.compare_columns = [
            col for col, checkbox in self.compare_checkboxes.items()
            if checkbox.isChecked()
        ]

        if not self.compare_columns:
            QMessageBox.warning(
                self,
                "No Columns to Compare",
                "Please select at least one column to compare."
            )
            return

        # Get selected show columns
        self.show_columns = [
            col for col, checkbox in self.show_checkboxes.items()
            if checkbox.isChecked()
        ]

        if not self.show_columns:
            QMessageBox.warning(
                self,
                "No Columns to Show",
                "Please select at least one column to display in results."
            )
            return

        self.accept()

    def get_config(self) -> Dict[str, Any]:
        """Get the comparison configuration

        Returns:
            Dictionary with keys: 'key_column', 'compare_columns', 'show_columns'
        """
        return {
            'key_column': self.key_column,
            'compare_columns': self.compare_columns,
            'show_columns': self.show_columns
        }
