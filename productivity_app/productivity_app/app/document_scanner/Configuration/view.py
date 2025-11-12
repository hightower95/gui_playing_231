"""
Document Scanner Configuration View - Manage document sources
"""
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QTableView, QHeaderView, QDialog, QLineEdit,
                               QComboBox, QSpinBox, QCheckBox, QTextEdit,
                               QFileDialog, QGroupBox, QListWidget, QListWidgetItem,
                               QDialogButtonBox, QFormLayout, QMessageBox, QWidget, QFrame)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem, QDragEnterEvent, QDropEvent
from app.ui.base_sub_tab_view import BaseTabView
from app.ui.components.label import StandardLabel, TextStyle
import pandas as pd
from pathlib import Path


class DropZoneWidget(QFrame):
    """Widget that accepts drag and drop of files"""

    file_dropped = Signal(str)  # Emits file path when file is dropped

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            DropZoneWidget {
                border: 2px dashed #cccccc;
                border-radius: 5px;
                background-color: #f9f9f9;
                padding: 20px;
            }
            DropZoneWidget:hover {
                border-color: #4CAF50;
                background-color: #f0f8f0;
            }
        """)

        layout = QVBoxLayout(self)

        self.drop_label = StandardLabel(
            "📄 Drag & drop file here\nor", style=TextStyle.SECTION)
        self.drop_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.drop_label)

        self.browse_btn = QPushButton("📁 Browse for File")
        self.browse_btn.clicked.connect(self._browse_file)
        layout.addWidget(self.browse_btn)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                DropZoneWidget {
                    border: 2px dashed #4CAF50;
                    border-radius: 5px;
                    background-color: #e8f5e9;
                    padding: 20px;
                }
            """)

    def dragLeaveEvent(self, event):
        """Handle drag leave event"""
        self.setStyleSheet("""
            DropZoneWidget {
                border: 2px dashed #cccccc;
                border-radius: 5px;
                background-color: #f9f9f9;
                padding: 20px;
            }
            DropZoneWidget:hover {
                border-color: #4CAF50;
                background-color: #f0f8f0;
            }
        """)

    def dropEvent(self, event: QDropEvent):
        """Handle file drop event"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.file_dropped.emit(file_path)
            event.acceptProposedAction()

        # Reset style
        self.dragLeaveEvent(None)

    def _browse_file(self):
        """Browse for a document file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Document",
            "",
            "Documents (*.csv *.txt *.xlsx *.xls);;All Files (*.*)"
        )

        if file_path:
            self.file_dropped.emit(file_path)


class AddDocumentDialog(QDialog):
    """Dialog for adding a new document with expandable step-by-step workflow"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Document")
        self.setMinimumWidth(800)

        self.file_path = None
        self.df = None
        self.config = {}
        self.is_excel_file = False
        self.available_sheets = []

        # Track completion state of each step
        self.step_completed = {
            1: False,  # File selected
            # Document structure configured (header + search columns)
            2: False,
            3: False,  # Return columns selected
        }

        self._setup_ui()

    def _setup_ui(self):
        """Setup the dialog UI with collapsible steps"""
        layout = QVBoxLayout(self)
        layout.setSpacing(5)

        # Step 1: Add Document
        self.step1_group = self._create_step_group(
            "Step 1: Add Document", expanded=True)

        self.drop_zone = DropZoneWidget()
        self.drop_zone.file_dropped.connect(self._on_file_selected)
        self.step1_group.layout().addWidget(self.drop_zone)

        self.file_path_label = StandardLabel("", style=TextStyle.NOTES)
        self.file_path_label.setVisible(False)
        self.step1_group.layout().addWidget(self.file_path_label)

        # Excel sheet selection (only visible for .xlsx/.xls files)
        self.sheet_selection_layout = QHBoxLayout()
        self.sheet_label = QLabel("Excel Sheet:")
        self.sheet_combo = QComboBox()
        self.sheet_combo.currentIndexChanged.connect(self._on_sheet_changed)
        self.sheet_selection_layout.addWidget(self.sheet_label)
        self.sheet_selection_layout.addWidget(self.sheet_combo)
        self.sheet_selection_layout.addStretch()

        self.sheet_selection_widget = QWidget()
        self.sheet_selection_widget.setLayout(self.sheet_selection_layout)
        self.sheet_selection_widget.setVisible(False)
        self.step1_group.layout().addWidget(self.sheet_selection_widget)

        # Document source type selection
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Document Source:"))
        self.source_type_combo = QComboBox()
        self.source_type_combo.addItems(["Local File", "Cached Document"])
        self.source_type_combo.currentIndexChanged.connect(
            self._on_source_type_changed)
        source_layout.addWidget(self.source_type_combo)
        source_layout.addStretch()
        self.step1_group.layout().addLayout(source_layout)

        # Cached document metadata fields (only visible when "Cached Document" is selected)
        self.cached_fields_group = QGroupBox("Cached Document Metadata")
        cached_layout = QFormLayout()

        self.document_version_edit = QLineEdit()
        self.document_version_edit.setPlaceholderText(
            "e.g., 1.0.0, 2024-10-24")
        cached_layout.addRow("Document Version:", self.document_version_edit)

        self.timestamp_edit = QLineEdit()
        self.timestamp_edit.setPlaceholderText("e.g., 2024-10-24T10:30:00Z")
        cached_layout.addRow("Timestamp:", self.timestamp_edit)

        self.file_id_edit = QLineEdit()
        self.file_id_edit.setPlaceholderText(
            "e.g., unique-file-identifier-123")
        cached_layout.addRow("File ID:", self.file_id_edit)

        self.schema_version_edit = QLineEdit()
        self.schema_version_edit.setPlaceholderText("e.g., 1.0")
        cached_layout.addRow("Schema Version:", self.schema_version_edit)

        self.cached_fields_group.setLayout(cached_layout)
        self.cached_fields_group.setVisible(False)  # Hidden by default
        self.step1_group.layout().addWidget(self.cached_fields_group)

        self.step1_ok_btn = QPushButton("✓ Confirm File")
        self.step1_ok_btn.setEnabled(False)
        self.step1_ok_btn.clicked.connect(lambda: self._complete_step(1))
        self.step1_group.layout().addWidget(self.step1_ok_btn)

        layout.addWidget(self.step1_group)
        self.step1_group.toggled.connect(
            lambda checked: self._on_group_toggled(self.step1_group, checked))

        # Step 2: Configure Document Structure (Combined preview + header + search columns)
        self.step2_group = self._create_step_group(
            "Step 2: Configure Document Structure", expanded=False)

        # Instructions
        instructions = QLabel(
            "Set the header row so column names appear at the top of the preview:")
        instructions.setStyleSheet("font-weight: bold; color: #333;")
        self.step2_group.layout().addWidget(instructions)

        # Header row configuration
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Header Row:"))
        self.header_row_spin = QSpinBox()
        self.header_row_spin.setMinimum(0)
        self.header_row_spin.setValue(0)
        self.header_row_spin.setToolTip(
            "0-based row index where column headers are located")
        self.header_row_spin.valueChanged.connect(self._reload_preview)
        header_layout.addWidget(self.header_row_spin)
        header_layout.addWidget(QLabel("(0 = first row)"))
        header_layout.addStretch()
        self.step2_group.layout().addLayout(header_layout)

        # Preview table
        preview_label = QLabel("Preview (first 20 rows):")
        preview_label.setStyleSheet("margin-top: 10px; font-weight: bold;")
        self.step2_group.layout().addWidget(preview_label)

        self.preview_table = QTableView()
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setMaximumHeight(200)
        self.step2_group.layout().addWidget(self.preview_table)

        # Search columns selection
        search_label = QLabel("Select column(s) to search in:")
        search_label.setStyleSheet("margin-top: 10px; font-weight: bold;")
        self.step2_group.layout().addWidget(search_label)

        self.search_columns_list = QListWidget()
        self.search_columns_list.setSelectionMode(QListWidget.MultiSelection)
        self.search_columns_list.setMaximumHeight(120)
        self.search_columns_list.itemSelectionChanged.connect(
            self._check_step2_complete)
        self.step2_group.layout().addWidget(self.search_columns_list)

        self.step2_ok_btn = QPushButton("✓ Confirm Configuration")
        self.step2_ok_btn.setEnabled(False)
        self.step2_ok_btn.clicked.connect(lambda: self._complete_step(2))
        self.step2_group.layout().addWidget(self.step2_ok_btn)

        layout.addWidget(self.step2_group)
        self.step2_group.toggled.connect(
            lambda checked: self._on_group_toggled(self.step2_group, checked))

        # Step 3: Select Return Columns
        self.step3_group = self._create_step_group(
            "Step 3: Select Return Columns", expanded=False)

        return_instructions = QLabel(
            "Select which columns to return in search results:")
        return_instructions.setStyleSheet("font-weight: bold; color: #333;")
        self.step3_group.layout().addWidget(return_instructions)

        self.return_columns_list = QListWidget()
        self.return_columns_list.setSelectionMode(QListWidget.MultiSelection)
        self.return_columns_list.setMaximumHeight(150)
        self.return_columns_list.itemSelectionChanged.connect(
            self._check_step3_complete)
        self.step3_group.layout().addWidget(self.return_columns_list)

        self.step3_ok_btn = QPushButton("✓ Confirm Return Columns")
        self.step3_ok_btn.setEnabled(False)
        self.step3_ok_btn.clicked.connect(lambda: self._complete_step(3))
        self.step3_group.layout().addWidget(self.step3_ok_btn)

        layout.addWidget(self.step3_group)
        self.step3_group.toggled.connect(
            lambda checked: self._on_group_toggled(self.step3_group, checked))

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        self.finish_btn = QPushButton("Finish & Add Document")
        self.finish_btn.setEnabled(False)
        self.finish_btn.clicked.connect(self._accept)
        self.finish_btn.setStyleSheet("font-weight: bold;")
        button_layout.addWidget(self.finish_btn)

        layout.addLayout(button_layout)

    def _create_step_group(self, title: str, expanded: bool = False) -> QGroupBox:
        """Create a collapsible step group box"""
        group = QGroupBox(title)
        group.setCheckable(True)
        group.setChecked(expanded)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QGroupBox::indicator {
                width: 13px;
                height: 13px;
            }
        """)

        # Create a layout for the group box to hold content
        group_layout = QVBoxLayout(group)
        group.setLayout(group_layout)

        return group

    def _on_group_toggled(self, group: QGroupBox, checked: bool):
        """Handle group expand/collapse"""
        # Hide/show all child widgets
        for i in range(group.layout().count()):
            widget = group.layout().itemAt(i).widget()
            if widget:
                widget.setVisible(checked)

        # Special handling: Load preview when Step 3 is expanded
        if checked and group == self.step2_group and self.file_path:
            # Only reload if preview is empty
            if self.preview_table.model() is None or self.preview_table.model().rowCount() == 0:
                self._reload_preview()

    def _complete_step(self, step_num: int):
        """Mark a step as complete and expand the next step"""
        self.step_completed[step_num] = True

        # Update step appearance
        step_group = getattr(self, f'step{step_num}_group')
        step_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #4CAF50;
            }
        """)

        # Collapse current step
        step_group.setChecked(False)

        # Special handling: Load preview when moving from Step 1 to Step 2
        if step_num == 1 and self.file_path:
            self._reload_preview()

        # Special handling: Populate return columns list when moving from Step 2 to Step 3
        if step_num == 2:
            self._populate_return_columns()

        # Expand next step
        if step_num < 3:
            next_group = getattr(self, f'step{step_num + 1}_group')
            next_group.setChecked(True)

        # Check if all required steps are complete
        self._check_can_finish()

    def _check_can_finish(self):
        """Check if all required steps are complete to enable finish button"""
        required_steps = [1, 2, 3]  # All three steps required
        can_finish = all(self.step_completed[step] for step in required_steps)
        self.finish_btn.setEnabled(can_finish)

    def _on_file_selected(self, file_path: str):
        """Handle file selection from drag-drop or browse"""
        self.file_path = file_path
        path = Path(file_path)

        # Check if it's an Excel file
        self.is_excel_file = path.suffix.lower() in ['.xlsx', '.xls']

        if self.is_excel_file:
            # Load sheet names using pandas
            try:
                excel_file = pd.ExcelFile(file_path)
                self.available_sheets = excel_file.sheet_names
                excel_file.close()

                # Populate combo box
                self.sheet_combo.clear()
                self.sheet_combo.addItems(self.available_sheets)

                # Show sheet selection
                self.sheet_selection_widget.setVisible(True)

                self.file_path_label.setText(
                    f"📄 Selected: {path.name} ({len(self.available_sheets)} sheet(s))"
                )
            except Exception as e:
                QMessageBox.warning(
                    self, "Error", f"Could not read Excel sheets: {e}")
                self.file_path_label.setText(
                    f"❌ Error reading sheets: {path.name}")
                self.file_path_label.setStyleSheet(
                    "color: red; font-weight: bold; margin-top: 10px;")
                self.file_path_label.setVisible(True)
                return
        else:
            # Not an Excel file, hide sheet selection
            self.sheet_selection_widget.setVisible(False)
            self.file_path_label.setText(f"📄 Selected: {path.name}")

        self.file_path_label.setStyleSheet(
            "color: green; font-weight: bold; margin-top: 10px;")
        self.file_path_label.setVisible(True)
        self.step1_ok_btn.setEnabled(True)
        self._load_file()

    def _on_sheet_changed(self, index: int):
        """Handle Excel sheet selection change"""
        if self.is_excel_file and index >= 0:
            # Reload the file with the new sheet
            self._load_file()

    def _on_source_type_changed(self, index: int):
        """Handle document source type change"""
        # Show/hide cached document fields based on selection
        is_cached = (index == 1)  # "Cached Document" is index 1
        self.cached_fields_group.setVisible(is_cached)

    def _load_file(self):
        """Load the file into dataframe"""
        if not self.file_path:
            return

        try:
            path = Path(self.file_path)

            # Load based on file type
            if path.suffix.lower() in ['.xlsx', '.xls']:
                # Get selected sheet name
                sheet_name = self.sheet_combo.currentText() if self.sheet_combo.count() > 0 else 0
                self.df = pd.read_excel(
                    self.file_path, sheet_name=sheet_name, header=None)
            else:
                # Try to read as CSV, fall back to tab-separated if that fails
                try:
                    self.df = pd.read_csv(self.file_path, header=None)
                except:
                    # Try tab-separated
                    self.df = pd.read_csv(
                        self.file_path, sep='\t', header=None)

            # Auto-complete step 1 if not already completed
            if not self.step_completed[1]:
                # Don't auto-complete, let user confirm
                pass

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load file: {e}")
            self.file_path_label.setText("❌ Error loading file")
            self.file_path_label.setStyleSheet("color: red; margin-top: 10px;")

    def _check_step2_complete(self):
        """Check if step 2 can be completed"""
        search_cols = self.search_columns_list.selectedItems()
        self.step2_ok_btn.setEnabled(len(search_cols) > 0)

    def _reload_preview(self):
        """Reload the preview with current header row setting"""
        if not self.file_path:
            return

        try:
            header_row = self.header_row_spin.value()
            path = Path(self.file_path)

            # Reload file with proper header row using pandas parameters
            if path.suffix.lower() in ['.xlsx', '.xls']:
                # Get selected sheet name
                sheet_name = self.sheet_combo.currentText() if self.sheet_combo.count() > 0 else 0
                preview_df = pd.read_excel(
                    self.file_path, sheet_name=sheet_name, header=header_row, nrows=20)
            else:
                # Try CSV first
                try:
                    preview_df = pd.read_csv(
                        self.file_path, header=header_row, nrows=20)
                except:
                    # Fall back to tab-separated
                    preview_df = pd.read_csv(
                        self.file_path, sep='\t', header=header_row, nrows=20)

            # Display in table
            model = QStandardItemModel(
                len(preview_df), len(preview_df.columns))
            model.setHorizontalHeaderLabels(
                [str(col) for col in preview_df.columns])

            for row in range(len(preview_df)):
                for col in range(len(preview_df.columns)):
                    value = preview_df.iloc[row, col]
                    # Handle NaN values
                    if pd.isna(value):
                        item = QStandardItem("")
                    else:
                        item = QStandardItem(str(value))
                    model.setItem(row, col, item)

            self.preview_table.setModel(model)
            self.preview_table.resizeColumnsToContents()

            # Update column list for step 2 (search columns only)
            columns = [str(col) for col in preview_df.columns]

            self.search_columns_list.clear()

            for col in columns:
                self.search_columns_list.addItem(col)

        except Exception as e:
            QMessageBox.warning(self, "Preview Error",
                                f"Failed to reload preview: {e}")

    def _check_step2_complete(self):
        """Check if step 2 can be completed"""
        search_cols = self.search_columns_list.selectedItems()
        self.step2_ok_btn.setEnabled(len(search_cols) > 0)

    def _populate_return_columns(self):
        """Populate return columns list with all available columns"""
        self.return_columns_list.clear()

        # Get all columns from the search columns list
        for i in range(self.search_columns_list.count()):
            col_name = self.search_columns_list.item(i).text()
            item = QListWidgetItem(col_name)
            self.return_columns_list.addItem(item)

        # No auto-selection - user must manually select columns

    def _check_step3_complete(self):
        """Check if step 3 can be completed"""
        return_cols = self.return_columns_list.selectedItems()
        self.step3_ok_btn.setEnabled(len(return_cols) > 0)

    def _accept(self):
        """Validate and accept the configuration"""
        if not self.file_path:
            QMessageBox.warning(self, "Error", "Please select a file")
            return

        search_cols = [item.text()
                       for item in self.search_columns_list.selectedItems()]

        return_cols = [item.text()
                       for item in self.return_columns_list.selectedItems()]

        if not search_cols:
            QMessageBox.warning(
                self, "Error", "Please select at least one search column")
            return

        if not return_cols:
            QMessageBox.warning(
                self, "Error", "Please select at least one return column")
            return

        # Determine source type
        is_cached = (self.source_type_combo.currentIndex() == 1)

        # Build configuration
        self.config = {
            'file_path': self.file_path,
            'file_name': Path(self.file_path).name,
            'doc_type': 'default',  # Simplified: always default
            'header_row': self.header_row_spin.value(),
            'search_columns': search_cols,
            'return_columns': return_cols,  # User-selected return columns
            'precondition_enabled': False,
            'precondition': '',
            'sheet_name': self.sheet_combo.currentText() if self.is_excel_file else None,
            'source_type': 'cached' if is_cached else 'local',
        }

        # Add cached document metadata if applicable
        if is_cached:
            self.config['cached_metadata'] = {
                'document_version': self.document_version_edit.text().strip(),
                'timestamp': self.timestamp_edit.text().strip(),
                'file_id': self.file_id_edit.text().strip(),
                'schema_version': self.schema_version_edit.text().strip(),
            }

        self.accept()


class ConfigurationView(BaseTabView):
    """View for managing document configurations"""

    # Signals
    add_document_requested = Signal(dict)  # config
    remove_document_requested = Signal(int)  # row index
    edit_document_requested = Signal(int, dict)  # row index, config
    export_config_requested = Signal()  # request to export configuration

    def __init__(self, parent=None):
        super().__init__(parent)
        self.documents_model = None
        self._setup_ui_content()

    def _setup_ui_content(self):
        """Setup the configuration UI"""
        # Update header
        self.header_frame.setFixedHeight(80)
        header_layout = QVBoxLayout(self.header_frame)
        header_layout.setContentsMargins(10, 10, 10, 10)

        # Title and buttons
        title_row = QHBoxLayout()
        title_label = QLabel("Document Configuration")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        title_row.addWidget(title_label)
        title_row.addStretch()

        self.add_btn = QPushButton("➕ Add Document")
        self.add_btn.clicked.connect(self._on_add_document)
        title_row.addWidget(self.add_btn)

        self.edit_btn = QPushButton("✏️ Edit")
        self.edit_btn.clicked.connect(self._on_edit_document)
        self.edit_btn.setEnabled(False)
        title_row.addWidget(self.edit_btn)

        self.remove_btn = QPushButton("🗑️ Remove")
        self.remove_btn.clicked.connect(self._on_remove_document)
        self.remove_btn.setEnabled(False)
        title_row.addWidget(self.remove_btn)

        self.export_btn = QPushButton("📤 Export Config")
        self.export_btn.clicked.connect(self._on_export_config)
        title_row.addWidget(self.export_btn)

        header_layout.addLayout(title_row)

        # Status label
        self.status_label = StandardLabel(
            "No documents configured", style=TextStyle.STATUS)
        header_layout.addWidget(self.status_label)

        # Documents table in left content
        content_layout = QVBoxLayout(self.left_content_frame)
        content_layout.setContentsMargins(10, 10, 10, 10)

        self.documents_table = QTableView()
        self.documents_table.setAlternatingRowColors(True)
        self.documents_table.setSelectionBehavior(QTableView.SelectRows)
        self.documents_table.setSelectionMode(QTableView.SingleSelection)

        # Setup table model FIRST
        self.documents_model = QStandardItemModel()
        self.documents_model.setHorizontalHeaderLabels([
            'File Name', 'Source', 'Type', 'Search Columns', 'Return Columns', 'Precondition'
        ])
        self.documents_table.setModel(self.documents_model)
        self.documents_table.horizontalHeader().setStretchLastSection(True)

        # NOW connect selection signal (after model is set)
        self.documents_table.selectionModel().selectionChanged.connect(
            self._on_selection_changed)

        content_layout.addWidget(self.documents_table)

        # Context area for document details
        self.context_box.setPlaceholderText(
            "Select a document to view configuration details...")

    def _on_add_document(self):
        """Show add document dialog"""
        dialog = AddDocumentDialog(self)

        if dialog.exec() == QDialog.Accepted:
            self.add_document_requested.emit(dialog.config)

    def _on_edit_document(self):
        """Edit selected document"""
        selection = self.documents_table.selectionModel()
        if not selection.hasSelection():
            return

        row = selection.selectedRows()[0].row()
        # TODO: Populate edit dialog with existing config
        QMessageBox.information(self, "Edit", "Edit functionality coming soon")

    def _on_remove_document(self):
        """Remove selected document"""
        selection = self.documents_table.selectionModel()
        if not selection.hasSelection():
            return

        row = selection.selectedRows()[0].row()
        file_name = self.documents_model.item(row, 0).text()

        reply = QMessageBox.question(
            self,
            "Confirm Remove",
            f"Remove document '{file_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.remove_document_requested.emit(row)

    def _on_export_config(self):
        """Export configuration to JSON file"""
        self.export_config_requested.emit()

    def _on_selection_changed(self):
        """Handle document selection"""
        has_selection = self.documents_table.selectionModel().hasSelection()
        self.edit_btn.setEnabled(has_selection)
        self.remove_btn.setEnabled(has_selection)

        if has_selection:
            row = self.documents_table.selectionModel().selectedRows()[0].row()
            self._show_document_details(row)

    def _show_document_details(self, row: int):
        """Show details of selected document in context area"""
        file_name = self.documents_model.item(row, 0).text()
        source_type = self.documents_model.item(row, 1).text()
        doc_type = self.documents_model.item(row, 2).text()
        search_cols = self.documents_model.item(row, 3).text()
        return_cols = self.documents_model.item(row, 4).text()
        precondition = self.documents_model.item(row, 5).text()

        # Get the actual config to show sheet name separately if it's an Excel file
        configs = []  # We'll need access to the model's configs
        # For now, just show the file name which includes sheet name in brackets

        details = (
            f"Document Configuration:\n\n"
            f"File: {file_name}\n"
            f"Source: {source_type}\n"
            f"Type: {doc_type}\n"
            f"Search Columns: {search_cols}\n"
            f"Return Columns: {return_cols}\n"
            f"Precondition: {precondition if precondition else 'None'}\n\n"
            f"Note: For Excel files, the sheet name is shown in brackets [Sheet Name]"
        )

        self.context_box.setPlainText(details)

    def add_document_row(self, config: dict):
        """Add a document to the table

        Args:
            config: Document configuration dictionary
        """
        # For Excel files, append sheet name to file name
        display_name = config['file_name']
        if config.get('sheet_name'):
            display_name = f"{config['file_name']} [{config['sheet_name']}]"

        # Get source type display
        source_type = config.get('source_type', 'local')
        source_display = '📁 Local' if source_type == 'local' else '💾 Cached'

        row = [
            QStandardItem(display_name),
            QStandardItem(source_display),
            QStandardItem(config['doc_type']),
            QStandardItem(', '.join(config['search_columns'])),
            QStandardItem(', '.join(config['return_columns'])),
            QStandardItem(config['precondition']
                          if config['precondition'] else 'None')
        ]

        self.documents_model.appendRow(row)
        self._update_status()

    def remove_document_row(self, row: int):
        """Remove a document from the table"""
        self.documents_model.removeRow(row)
        self._update_status()

    def _update_status(self):
        """Update status label"""
        count = self.documents_model.rowCount()
        if count == 0:
            self.status_label.setText("No documents configured")
            self.status_label.setStyleSheet("color: gray; font-size: 10pt;")
        else:
            self.status_label.setText(f"{count} document(s) configured")
            self.status_label.setStyleSheet("color: green; font-size: 10pt;")
