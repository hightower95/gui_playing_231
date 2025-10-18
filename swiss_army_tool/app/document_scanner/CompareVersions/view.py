"""
Compare Versions View - UI for comparing different versions of documents
"""
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QComboBox, QFrame, QTableWidget, QTableWidgetItem,
                               QHeaderView, QMenu, QMessageBox, QFileDialog)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from app.ui.base_sub_tab_view import BaseTabView
from typing import Dict, List, Any
import pandas as pd


class DropArea(QFrame):
    """Drag and drop area for custom documents"""

    file_dropped = Signal(str)  # file_path

    def __init__(self, label_text: str, parent=None):
        super().__init__(parent)
        self.label_text = label_text
        self.file_path = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup drag-drop area"""
        self.setAcceptDrops(True)
        self.setFrameStyle(QFrame.Box | QFrame.Sunken)
        self.setMinimumHeight(60)
        self.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border: 2px dashed #999;
                border-radius: 5px;
            }
            QFrame:hover {
                background-color: #e8e8e8;
                border-color: #666;
            }
        """)

        layout = QVBoxLayout(self)
        self.label = QLabel(self.label_text)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet(
            "color: #333; font-weight: bold;")  # Darker text
        layout.addWidget(self.label)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QFrame {
                    background-color: #d0e8ff;
                    border: 2px solid #0078d4;
                    border-radius: 5px;
                }
            """)

    def dragLeaveEvent(self, event):
        """Handle drag leave"""
        self._reset_style()

    def dropEvent(self, event: QDropEvent):
        """Handle file drop"""
        self._reset_style()

        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.csv', '.xlsx', '.xls')):
                self.file_path = file_path
                self.label.setText(
                    f"✓ Custom File:\n{file_path.split('/')[-1]}")
                self.file_dropped.emit(file_path)
                event.acceptProposedAction()
            else:
                QMessageBox.warning(
                    self,
                    "Invalid File",
                    "Please drop a CSV or Excel file"
                )

    def _reset_style(self):
        """Reset to default style"""
        self.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border: 2px dashed #999;
                border-radius: 5px;
            }
            QFrame:hover {
                background-color: #e8e8e8;
                border-color: #666;
            }
        """)

    def clear(self):
        """Clear the drop area"""
        self.file_path = None
        self.label.setText(self.label_text)
        self._reset_style()


class CompareVersionsView(BaseTabView):
    """View for comparing document versions"""

    # Signals
    document_selected = Signal(str)  # document_id
    version1_selected = Signal(str)  # version
    version2_selected = Signal(str)  # version
    custom_file1_dropped = Signal(str)  # file_path
    custom_file2_dropped = Signal(str)  # file_path
    compare_requested = Signal()
    filter_changes_requested = Signal()
    export_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.documents_by_project = {}
        self._setup_ui_content()

        # Set help content for this tab
        self.set_help_content("""
            <h2>Compare Versions - Help</h2>
            
            <h3>Overview</h3>
            <p>Compare different versions of documents to identify changes and differences.</p>
            
            <h3>Quick Start</h3>
            <ol>
                <li><b>Select Document:</b> Choose from dropdown (organized by project)</li>
                <li><b>Select Versions:</b> Pick two versions to compare, OR drag-drop custom files</li>
                <li><b>Click Compare:</b> Configure key column and which columns to compare</li>
                <li><b>View Results:</b> Yellow rows = different, Gray rows = same</li>
                <li><b>Filter/Export:</b> Show only changes or export results</li>
            </ol>
            
            <h3>Features</h3>
            <ul>
                <li><b>Drag & Drop:</b> Drop CSV or Excel files directly into the drop areas</li>
                <li><b>Custom Documents:</b> Select "Custom Document" to compare any two files</li>
                <li><b>Filter Changes:</b> Toggle to show only rows that are different</li>
                <li><b>Export:</b> Save comparison results to CSV or Excel</li>
            </ul>
            
            <h3>Results Interpretation</h3>
            <ul>
                <li><b>Same:</b> Row exists in both versions with identical values</li>
                <li><b>Different:</b> Row exists in both but has changes (yellow highlight)</li>
                <li><b>Only in Version 1:</b> Row was removed or not in Version 2</li>
                <li><b>Only in Version 2:</b> Row was added or not in Version 1</li>
            </ul>
            
            <h3>Tips</h3>
            <ul>
                <li>Key column must be unique in both versions</li>
                <li>Select only relevant columns to compare (faster)</li>
                <li>Use CSV files for best performance with large data</li>
                <li>Right-click results table for context menu</li>
            </ul>
        """)

        # Set initial context
        self.context_box.setPlainText(
            "Welcome to Compare Versions!\n\n"
            "1. Select a document from the dropdown above\n"
            "2. Choose two versions to compare\n"
            "3. Or drag-and-drop custom CSV/Excel files\n"
            "4. Click 'Compare Versions' to begin\n\n"
            "Click '? Help' in the header for detailed instructions."
        )

    def _setup_ui_content(self):
        """Setup the compare versions UI"""
        # Update header - make it taller
        self.header_frame.setFixedHeight(280)
        header_layout = QVBoxLayout(self.header_frame)
        header_layout.setContentsMargins(10, 10, 10, 10)

        # Title and Compare button on same row
        title_row = QHBoxLayout()
        title_label = QLabel("Compare Document Versions")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        title_row.addWidget(title_label)
        title_row.addStretch()

        # Compare button (moved to title row)
        self.compare_btn = QPushButton("⚖️ Compare Versions")
        self.compare_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                padding: 8px 20px;
                font-size: 11pt;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.compare_btn.clicked.connect(self.compare_requested)
        title_row.addWidget(self.compare_btn)

        header_layout.addLayout(title_row)

        # Document selector - narrower width (40% of original)
        doc_row = QHBoxLayout()
        doc_row.addWidget(QLabel("Document:"))
        self.document_combo = QComboBox()
        self.document_combo.setMaximumWidth(400)  # Limit width to about 40%
        self.document_combo.currentTextChanged.connect(
            self._on_document_changed)
        doc_row.addWidget(self.document_combo)
        doc_row.addStretch()  # Push everything to the left
        header_layout.addLayout(doc_row)

        # Version selectors side-by-side
        version_row = QHBoxLayout()

        # Version 1
        version1_layout = QVBoxLayout()
        version1_layout.addWidget(QLabel("Version 1:"))
        self.version1_combo = QComboBox()
        self.version1_combo.currentTextChanged.connect(
            lambda v: self.version1_selected.emit(v) if v else None
        )
        version1_layout.addWidget(self.version1_combo)
        version_row.addLayout(version1_layout)

        # Version 2
        version2_layout = QVBoxLayout()
        version2_layout.addWidget(QLabel("Version 2:"))
        self.version2_combo = QComboBox()
        self.version2_combo.currentTextChanged.connect(
            lambda v: self.version2_selected.emit(v) if v else None
        )
        version2_layout.addWidget(self.version2_combo)
        version_row.addLayout(version2_layout)

        header_layout.addLayout(version_row)

        # Drag-drop areas
        drop_row = QHBoxLayout()

        self.drop_area1 = DropArea("Drag & Drop Version 1\n(sets to 'Custom')")
        self.drop_area1.file_dropped.connect(self.custom_file1_dropped)
        drop_row.addWidget(self.drop_area1)

        self.drop_area2 = DropArea("Drag & Drop Version 2\n(sets to 'Custom')")
        self.drop_area2.file_dropped.connect(self.custom_file2_dropped)
        drop_row.addWidget(self.drop_area2)

        header_layout.addLayout(drop_row)

        # Results table in content area (use left_content_frame from BaseTabView)
        content_layout = QVBoxLayout(self.left_content_frame)
        content_layout.setContentsMargins(10, 10, 10, 10)

        # Results header with filter/export buttons
        results_header = QHBoxLayout()
        results_label = QLabel("Comparison Results:")
        results_label.setStyleSheet("font-size: 10pt; font-weight: bold;")
        results_header.addWidget(results_label)
        results_header.addStretch()

        self.filter_changes_btn = QPushButton("🔍 Filter Changes Only")
        self.filter_changes_btn.clicked.connect(self.filter_changes_requested)
        self.filter_changes_btn.setEnabled(False)
        results_header.addWidget(self.filter_changes_btn)

        self.export_btn = QPushButton("📤 Export Results")
        self.export_btn.clicked.connect(self.export_requested)
        self.export_btn.setEnabled(False)
        results_header.addWidget(self.export_btn)

        content_layout.addLayout(results_header)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(
            self._show_context_menu)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.horizontalHeader().setStretchLastSection(True)
        content_layout.addWidget(self.results_table)

        # Status label
        self.results_status = QLabel("Select document and versions to compare")
        self.results_status.setStyleSheet("color: #666; font-style: italic;")
        content_layout.addWidget(self.results_status)

        # Update the record count label from BaseTabView
        self.record_count_label.setText("Ready to compare versions")

    def populate_documents(self, documents_by_project: Dict[str, List[Dict[str, Any]]]):
        """Populate document dropdown with grouped items

        Args:
            documents_by_project: Dict mapping project names to document lists
        """
        self.documents_by_project = documents_by_project
        self.document_combo.clear()

        # Add blank item
        self.document_combo.addItem("-- Select Document --", userData=None)

        # Add documents grouped by project
        for project, documents in documents_by_project.items():
            # Add project separator
            self.document_combo.addItem(f"─── {project} ───", userData=None)
            # Disable separator
            model = self.document_combo.model()
            index = self.document_combo.count() - 1
            item = model.item(index)
            item.setEnabled(False)
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)

            # Add documents under this project
            for doc in documents:
                display_name = f"  {doc['name']}"
                self.document_combo.addItem(display_name, userData=doc)

        # Add "Other" option
        self.document_combo.addItem("─── Other ───", userData=None)
        model = self.document_combo.model()
        index = self.document_combo.count() - 1
        item = model.item(index)
        item.setEnabled(False)
        self.document_combo.addItem(
            "  Custom Document", userData={"id": "custom"})

    def populate_versions(self, versions: List[str]):
        """Populate version dropdowns

        Args:
            versions: List of version strings
        """
        self.version1_combo.clear()
        self.version2_combo.clear()

        # Add "Custom" option first
        self.version1_combo.addItem("Custom")
        self.version2_combo.addItem("Custom")

        # Add versions
        for version in versions:
            self.version1_combo.addItem(version)
            self.version2_combo.addItem(version)

        # Auto-select first and last versions if available
        if len(versions) >= 2:
            self.version1_combo.setCurrentText(versions[0])
            self.version2_combo.setCurrentText(versions[-1])
        elif len(versions) == 1:
            self.version1_combo.setCurrentText(versions[0])
            self.version2_combo.setCurrentText(versions[0])

    def display_comparison_results(self, results_df: pd.DataFrame, verdict_column: str = "Verdict"):
        """Display comparison results in table

        Args:
            results_df: DataFrame with comparison results
            verdict_column: Name of the verdict column
        """
        self.results_table.clear()

        if results_df.empty:
            self.results_status.setText("No data to compare")
            return

        # Set up table
        self.results_table.setRowCount(len(results_df))
        self.results_table.setColumnCount(len(results_df.columns))
        self.results_table.setHorizontalHeaderLabels(
            results_df.columns.tolist())

        # Populate table
        for row_idx in range(len(results_df)):
            for col_idx, col_name in enumerate(results_df.columns):
                value = results_df.iloc[row_idx, col_idx]
                item = QTableWidgetItem(str(value))

                # Highlight verdict column
                if col_name == verdict_column:
                    if value == "Different":
                        item.setBackground(Qt.yellow)
                    elif value == "Same":
                        item.setBackground(Qt.lightGray)

                self.results_table.setItem(row_idx, col_idx, item)

        # Resize columns
        self.results_table.resizeColumnsToContents()

        # Enable buttons
        self.filter_changes_btn.setEnabled(True)
        self.export_btn.setEnabled(True)

        # Update status
        total_rows = len(results_df)
        if verdict_column in results_df.columns:
            changes = (results_df[verdict_column] == "Different").sum()
            same = (results_df[verdict_column] == "Same").sum()
            only_v1 = (results_df[verdict_column] == "Only in Version 1").sum()
            only_v2 = (results_df[verdict_column] == "Only in Version 2").sum()

            self.results_status.setText(
                f"Compared {total_rows} rows - {changes} differences found")
            self.record_count_label.setText(
                f"Total: {total_rows} rows | Different: {changes} | Same: {same} | Only V1: {only_v1} | Only V2: {only_v2}")

            # Update context box with summary
            self.context_box.setPlainText(
                f"Comparison Summary\n"
                f"{'='*50}\n\n"
                f"Total Rows Compared: {total_rows}\n\n"
                f"Results Breakdown:\n"
                f"  • Different: {changes} rows ({changes/total_rows*100:.1f}%)\n"
                f"  • Same: {same} rows ({same/total_rows*100:.1f}%)\n"
                f"  • Only in Version 1: {only_v1} rows\n"
                f"  • Only in Version 2: {only_v2} rows\n\n"
                f"Yellow highlighted rows indicate differences.\n\n"
                f"Use 'Filter Changes' to show only different rows.\n"
                f"Use 'Export Results' to save to CSV or Excel."
            )
        else:
            self.results_status.setText(f"Compared {total_rows} rows")
            self.record_count_label.setText(f"Total: {total_rows} rows")

    def _on_document_changed(self, text: str):
        """Handle document selection change"""
        current_data = self.document_combo.currentData()
        if current_data and "id" in current_data:
            self.document_selected.emit(current_data["id"])

    def _show_context_menu(self, pos):
        """Show context menu for results table"""
        menu = QMenu(self)

        filter_action = menu.addAction("🔍 Filter Changes Only")
        filter_action.triggered.connect(self.filter_changes_requested)

        export_action = menu.addAction("📤 Export Results")
        export_action.triggered.connect(self.export_requested)

        menu.exec_(self.results_table.mapToGlobal(pos))

    def update_status(self, message: str, color: str = "black"):
        """Update status message

        Args:
            message: Status message
            color: Text color
        """
        self.results_status.setText(message)
        self.results_status.setStyleSheet(
            f"color: {color}; font-style: italic;")
        self.record_count_label.setText(message)

        # Also update footer box with timestamped log
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        current_text = self.footer_box.toPlainText()
        self.footer_box.setPlainText(
            f"[{timestamp}] {message}\n{current_text}")

    def get_selected_document_id(self) -> str:
        """Get currently selected document ID"""
        current_data = self.document_combo.currentData()
        if current_data and "id" in current_data:
            return current_data["id"]
        return None

    def get_selected_version1(self) -> str:
        """Get selected version 1"""
        return self.version1_combo.currentText()

    def get_selected_version2(self) -> str:
        """Get selected version 2"""
        return self.version2_combo.currentText()
