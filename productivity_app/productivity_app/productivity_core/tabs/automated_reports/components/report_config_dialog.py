"""
Report Configuration Dialog - Interstitial for configuring and running reports

Matches the design from the UI mockup with:
- Report title and description
- Tab system (Summary, per-document tabs, Settings)
- File browse buttons for document inputs
- Run Report / Save as Draft / Cancel buttons
"""
from typing import Optional, Dict, List
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                QPushButton, QLineEdit, QTabWidget, QWidget,
                                QTableWidget, QTableWidgetItem, QFileDialog,
                                QCheckBox, QFrame, QScrollArea)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class ReportConfigDialog(QDialog):
    """Dialog for configuring report inputs and running reports"""
    
    report_executed = Signal(str, dict)  # Emits (report_title, parameters)
    
    def __init__(self, report_title: str, report_description: str, 
                 required_inputs: List[str], optional_inputs: List[str] = None,
                 parent: Optional[QWidget] = None):
        """Initialize report configuration dialog
        
        Args:
            report_title: Title of the report
            report_description: Description text
            required_inputs: List of required input names
            optional_inputs: List of optional input names
            parent: Parent widget
        """
        super().__init__(parent)
        self.report_title = report_title
        self.report_description = report_description
        self.required_inputs = required_inputs or []
        self.optional_inputs = optional_inputs or []
        self.input_values: Dict[str, str] = {}  # Store input selections
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle(f"Configure Report - {self.report_title}")
        self.setMinimumSize(950, 650)
        self.setModal(True)
        
        # Apply dark theme styling
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #e3e3e3;
            }
            QLabel {
                color: #e3e3e3;
            }
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                color: #e3e3e3;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #252525;
            }
            QPushButton#runButton {
                background-color: #0e639c;
                border: 1px solid #1177bb;
            }
            QPushButton#runButton:hover {
                background-color: #1177bb;
            }
            QPushButton#runButton:disabled {
                background-color: #3a3a3a;
                color: #666666;
                border: 1px solid #444444;
            }
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                color: #e3e3e3;
                padding: 6px;
            }
            QLineEdit:focus {
                border: 1px solid #0e639c;
            }
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                background-color: #252525;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                border: 1px solid #3a3a3a;
                padding: 8px 16px;
                color: #a3a3a3;
            }
            QTabBar::tab:selected {
                background-color: #252525;
                color: #e3e3e3;
                border-bottom-color: #252525;
            }
            QTabBar::tab:hover:!selected {
                background-color: #3a3a3a;
            }
            QTableWidget {
                background-color: #252525;
                border: 1px solid #3a3a3a;
                gridline-color: #3a3a3a;
                color: #e3e3e3;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #e3e3e3;
                border: 1px solid #3a3a3a;
                padding: 4px;
            }
            QCheckBox {
                color: #e3e3e3;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Header section
        self._create_header(layout)
        
        # Tab widget for Summary / Document inputs / Settings
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs, stretch=1)
        
        # Create tabs
        self._create_summary_tab()
        self._create_document_tabs()
        self._create_settings_tab()
        
        # Footer with action buttons
        self._create_footer(layout)
        
        # Update button states
        self._update_run_button_state()
        
    def _create_header(self, layout: QVBoxLayout):
        """Create header with title and description"""
        # Title
        title_label = QLabel(self.report_title)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(self.report_description)
        desc_label.setStyleSheet("color: #a3a3a3; font-size: 12px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #3a3a3a;")
        layout.addWidget(line)
        
    def _create_summary_tab(self):
        """Create Summary tab showing required inputs"""
        summary_widget = QWidget()
        summary_layout = QVBoxLayout(summary_widget)
        summary_layout.setContentsMargins(16, 16, 16, 16)
        summary_layout.setSpacing(12)
        
        # Header
        header_label = QLabel("Report Configuration")
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        header_label.setFont(header_font)
        summary_layout.addWidget(header_label)
        
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
        self.summary_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Add required inputs
        self.summary_table.setRowCount(len(self.required_inputs))
        for i, input_name in enumerate(self.required_inputs):
            # Status circle
            status_item = QTableWidgetItem("⭕")
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.summary_table.setItem(i, 0, status_item)
            
            # Input name
            name_item = QTableWidgetItem(input_name + " *")
            self.summary_table.setItem(i, 1, name_item)
            
            # Description
            desc_item = QTableWidgetItem(self._get_input_description(input_name))
            self.summary_table.setItem(i, 2, desc_item)
            
            # Value (initially "Not selected")
            value_item = QTableWidgetItem("Not selected")
            value_item.setForeground(Qt.GlobalColor.gray)
            self.summary_table.setItem(i, 3, value_item)
        
        summary_layout.addWidget(self.summary_table, stretch=1)
        
        # Footer note
        note_label = QLabel("* Required fields must be completed before running the report")
        note_label.setStyleSheet("color: #d16969; font-size: 11px; font-style: italic;")
        summary_layout.addWidget(note_label)
        
        self.tabs.addTab(summary_widget, "Summary")
        
    def _create_document_tabs(self):
        """Create a tab for each required document input"""
        for input_name in self.required_inputs:
            tab = self._create_document_input_tab(input_name)
            # Determine if it's optional
            is_optional = "(Optional)" in input_name or "optional" in input_name.lower()
            tab_label = input_name.replace("(Optional)", "").strip()
            if is_optional:
                tab_label += " (Optional)"
            self.tabs.addTab(tab, tab_label)
            
    def _create_document_input_tab(self, input_name: str) -> QWidget:
        """Create a tab for a single document input with source selection
        
        Args:
            input_name: Name of the input
            
        Returns:
            Tab widget
        """
        from PySide6.QtGui import QDragEnterEvent, QDropEvent
        
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.setContentsMargins(16, 16, 16, 16)
        tab_layout.setSpacing(16)
        
        # Input description header
        is_required = input_name in self.required_inputs
        
        # Title with required indicator
        title_label = QLabel(input_name + (" *" if is_required else ""))
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #e3e3e3;")
        tab_layout.addWidget(title_label)
        
        # Required/Optional indicator
        status_label = QLabel("⭕ Required" if is_required else "Optional")
        status_label.setStyleSheet("color: #a3a3a3; font-size: 11px;")
        tab_layout.addWidget(status_label)
        
        # Description text
        desc_text = self._get_detailed_input_description(input_name)
        desc_label = QLabel(desc_text)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #a3a3a3; font-size: 11px; margin-bottom: 8px;")
        tab_layout.addWidget(desc_label)
        
        # Accepted formats
        formats_label = QLabel("Accepted formats: .xlsx, .csv, .xls")
        formats_label.setStyleSheet("color: #888888; font-size: 10px; font-style: italic;")
        tab_layout.addWidget(formats_label)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #3a3a3a; margin: 8px 0px;")
        tab_layout.addWidget(line)
        
        # "or choose source" label
        source_label = QLabel("or choose source")
        source_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        source_label.setStyleSheet("color: #888888; font-size: 11px; margin: 8px 0px;")
        tab_layout.addWidget(source_label)
        
        # Source selection buttons
        source_buttons_layout = QHBoxLayout()
        source_buttons_layout.setSpacing(12)
        
        # Upload button
        upload_btn = QPushButton("Upload")
        upload_btn.setCheckable(True)
        upload_btn.setChecked(True)  # Default selected
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #e8f0fe;
                border: 2px solid #1a73e8;
                border-radius: 8px;
                color: #1967d2;
                padding: 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d2e3fc;
            }
            QPushButton:checked {
                background-color: #e8f0fe;
                border: 2px solid #1a73e8;
            }
            QPushButton:!checked {
                background-color: #2d2d2d;
                border: 1px solid #3a3a3a;
                color: #a3a3a3;
            }
        """)
        
        # From Server button
        server_btn = QPushButton("From Server")
        server_btn.setCheckable(True)
        server_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                color: #a3a3a3;
                padding: 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QPushButton:checked {
                background-color: #e8f0fe;
                border: 2px solid #1a73e8;
                color: #1967d2;
            }
        """)
        
        # From Cache button
        cache_btn = QPushButton("From Cache")
        cache_btn.setCheckable(True)
        cache_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                color: #a3a3a3;
                padding: 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QPushButton:checked {
                background-color: #e8f0fe;
                border: 2px solid #1a73e8;
                color: #1967d2;
            }
        """)
        
        # Add icons to buttons
        upload_btn.setIcon(upload_btn.style().standardIcon(upload_btn.style().StandardPixmap.SP_ArrowUp))
        server_btn.setIcon(server_btn.style().standardIcon(server_btn.style().StandardPixmap.SP_DriveNetIcon))
        cache_btn.setIcon(cache_btn.style().standardIcon(cache_btn.style().StandardPixmap.SP_DirIcon))
        
        source_buttons_layout.addWidget(upload_btn, stretch=1)
        source_buttons_layout.addWidget(server_btn, stretch=1)
        source_buttons_layout.addWidget(cache_btn, stretch=1)
        
        tab_layout.addLayout(source_buttons_layout)
        
        # Drag and drop area (shown when Upload is selected)
        drop_area = QFrame()
        drop_area.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: 2px dashed #3a3a3a;
                border-radius: 8px;
                padding: 40px;
            }
        """)
        drop_area.setAcceptDrops(True)
        
        drop_layout = QVBoxLayout(drop_area)
        drop_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_layout.setSpacing(12)
        
        # Upload icon
        icon_label = QLabel("⬆")
        icon_label.setStyleSheet("font-size: 48px; color: #666666; background: transparent; border: none;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_layout.addWidget(icon_label)
        
        # Drag and drop text
        drag_text = QLabel("Drag and drop files here")
        drag_text.setStyleSheet("color: #e3e3e3; font-size: 13px; background: transparent; border: none;")
        drag_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_layout.addWidget(drag_text)
        
        # "or" text
        or_label = QLabel("or")
        or_label.setStyleSheet("color: #888888; font-size: 11px; background: transparent; border: none;")
        or_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_layout.addWidget(or_label)
        
        # Browse files button
        browse_btn = QPushButton("browse files")
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #4a9eff;
                font-size: 12px;
                text-decoration: underline;
                padding: 4px 8px;
            }
            QPushButton:hover {
                color: #6bb3ff;
            }
        """)
        browse_btn.clicked.connect(lambda: self._browse_for_file_enhanced(input_name, selected_file_label))
        drop_layout.addWidget(browse_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        tab_layout.addWidget(drop_area, stretch=1)
        
        # Selected file display (initially hidden)
        selected_file_label = QLabel("")
        selected_file_label.setStyleSheet("color: #4ec9b0; font-size: 11px; margin-top: 8px;")
        selected_file_label.setWordWrap(True)
        selected_file_label.hide()
        tab_layout.addWidget(selected_file_label)
        
        # Upload Files dialog (shown when "Upload Files" clicked)
        upload_dialog = QFrame()
        upload_dialog.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border: 2px solid #1a73e8;
                border-radius: 8px;
                padding: 24px;
            }
        """)
        upload_dialog.hide()
        
        upload_dialog_layout = QVBoxLayout(upload_dialog)
        upload_dialog_layout.setSpacing(16)
        
        # Dialog header
        upload_header = QHBoxLayout()
        upload_title = QLabel("Upload Files")
        upload_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #e3e3e3;")
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #888888;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #e3e3e3;
            }
        """)
        close_btn.clicked.connect(upload_dialog.hide)
        
        upload_header.addWidget(upload_title)
        upload_header.addStretch()
        upload_header.addWidget(close_btn)
        upload_dialog_layout.addLayout(upload_header)
        
        # Upload icon and button
        upload_icon = QLabel("⬆")
        upload_icon.setStyleSheet("font-size: 32px; color: #4a9eff;")
        upload_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upload_dialog_layout.addWidget(upload_icon)
        
        choose_files_btn = QPushButton("Choose Files")
        choose_files_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                border: none;
                border-radius: 6px;
                color: white;
                padding: 10px 24px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        choose_files_btn.clicked.connect(lambda: self._browse_for_file_enhanced(input_name, selected_file_label))
        upload_dialog_layout.addWidget(choose_files_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        upload_info = QLabel("Select one or more files from your computer")
        upload_info.setStyleSheet("color: #888888; font-size: 11px;")
        upload_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upload_dialog_layout.addWidget(upload_info)
        
        tab_layout.addWidget(upload_dialog)
        
        # Connect source button toggle logic
        def on_upload_clicked():
            if upload_btn.isChecked():
                server_btn.setChecked(False)
                cache_btn.setChecked(False)
                drop_area.show()
                upload_dialog.hide()
                
        def on_server_clicked():
            if server_btn.isChecked():
                upload_btn.setChecked(False)
                cache_btn.setChecked(False)
                drop_area.hide()
                upload_dialog.hide()
                # TODO: Show server file browser
                
        def on_cache_clicked():
            if cache_btn.isChecked():
                upload_btn.setChecked(False)
                server_btn.setChecked(False)
                drop_area.hide()
                upload_dialog.hide()
                # TODO: Show cache file list
        
        upload_btn.clicked.connect(on_upload_clicked)
        server_btn.clicked.connect(on_server_clicked)
        cache_btn.clicked.connect(on_cache_clicked)
        
        # Store references for drag-drop handling
        setattr(self, f"_drop_area_{input_name.replace(' ', '_')}", drop_area)
        setattr(self, f"_selected_file_label_{input_name.replace(' ', '_')}", selected_file_label)
        
        return tab_widget
        
    def _get_detailed_input_description(self, input_name: str) -> str:
        """Get detailed description for an input parameter
        
        Args:
            input_name: Name of the input
            
        Returns:
            Description text
        """
        if "parts" in input_name.lower() or "list" in input_name.lower():
            return "Upload the master parts list for comparison. This should include all parts that are expected to be in inventory."
        elif "inventory" in input_name.lower():
            return "Current inventory snapshot"
        elif "bom" in input_name.lower():
            return "Optional BOM for cross-reference"
        else:
            return "Required input for report generation"
    
    def _browse_for_file_enhanced(self, input_name: str, label: QLabel):
        """Open file browser and update both path and label
        
        Args:
            input_name: Name of the input
            label: Label to update with selected file
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select {input_name}",
            "",
            "All Files (*);;CSV Files (*.csv);;Excel Files (*.xlsx *.xls)"
        )
        
        if file_path:
            self._on_input_changed(input_name, file_path)
            label.setText(f"✓ Selected: {file_path}")
            label.show()
        
    def _create_settings_tab(self):
        """Create Settings tab for report options"""
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setContentsMargins(16, 16, 16, 16)
        settings_layout.setSpacing(12)
        
        # Output file name
        output_label = QLabel("Output File Name (Optional)")
        output_label.setStyleSheet("font-weight: bold;")
        settings_layout.addWidget(output_label)
        
        self.output_filename = QLineEdit()
        self.output_filename.setPlaceholderText("Enter output file name")
        settings_layout.addWidget(self.output_filename)
        
        # Case sensitive comparison
        self.case_sensitive_checkbox = QCheckBox("Case Sensitive Comparison (Optional)")
        self.case_sensitive_checkbox.setStyleSheet("font-weight: bold;")
        self.case_sensitive_checkbox.setChecked(False)
        settings_layout.addWidget(self.case_sensitive_checkbox)
        
        case_desc = QLabel("Match text case exactly")
        case_desc.setStyleSheet("color: #a3a3a3; font-size: 11px; margin-left: 24px;")
        settings_layout.addWidget(case_desc)
        
        # Timestamp checkbox
        self.timestamp_checkbox = QCheckBox("Include Timestamp (Optional)")
        self.timestamp_checkbox.setStyleSheet("font-weight: bold;")
        self.timestamp_checkbox.setChecked(True)
        settings_layout.addWidget(self.timestamp_checkbox)
        
        timestamp_desc = QLabel("Add timestamp to report output")
        timestamp_desc.setStyleSheet("color: #a3a3a3; font-size: 11px; margin-left: 24px;")
        settings_layout.addWidget(timestamp_desc)
        
        settings_layout.addStretch()
        
        self.tabs.addTab(settings_widget, "Settings")
        
    def _create_footer(self, layout: QVBoxLayout):
        """Create footer with action buttons"""
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(12)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        # Info label
        self.info_label = QLabel("⓵ Complete required inputs to run report")
        self.info_label.setStyleSheet("color: #a3a3a3; font-size: 11px;")
        
        # Save as Draft button
        draft_btn = QPushButton("Save as Draft")
        draft_btn.clicked.connect(self._on_save_draft)
        
        # Run Report button
        self.run_btn = QPushButton("Run Report")
        self.run_btn.setObjectName("runButton")
        self.run_btn.clicked.connect(self._on_run_report)
        
        footer_layout.addWidget(cancel_btn)
        footer_layout.addWidget(self.info_label, stretch=1)
        footer_layout.addWidget(draft_btn)
        footer_layout.addWidget(self.run_btn)
        
        layout.addLayout(footer_layout)
        
    def _browse_for_file(self, input_name: str, line_edit: QLineEdit):
        """Open file browser for selecting input file
        
        Args:
            input_name: Name of the input
            line_edit: Line edit to update with selected file
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select {input_name}",
            "",
            "All Files (*);;CSV Files (*.csv);;Excel Files (*.xlsx *.xls)"
        )
        
        if file_path:
            line_edit.setText(file_path)
            self._on_input_changed(input_name, file_path)
            
    def _on_input_changed(self, input_name: str, value: str):
        """Handle input value change
        
        Args:
            input_name: Name of the input that changed
            value: New value
        """
        self.input_values[input_name] = value
        self._update_summary_table()
        self._update_run_button_state()
        
    def _update_summary_table(self):
        """Update summary table with current input values"""
        for i, input_name in enumerate(self.required_inputs):
            value = self.input_values.get(input_name, "")
            
            # Update status
            status_item = self.summary_table.item(i, 0)
            if value:
                status_item.setText("✅")
            else:
                status_item.setText("⭕")
            
            # Update value
            value_item = self.summary_table.item(i, 3)
            if value:
                value_item.setText(value)
                value_item.setForeground(Qt.GlobalColor.white)
            else:
                value_item.setText("Not selected")
                value_item.setForeground(Qt.GlobalColor.gray)
                
    def _update_run_button_state(self):
        """Enable/disable run button based on required inputs"""
        all_required_filled = all(
            self.input_values.get(inp, "") for inp in self.required_inputs
        )
        
        self.run_btn.setEnabled(all_required_filled)
        
        if all_required_filled:
            self.info_label.setText("✓ Ready to run")
            self.info_label.setStyleSheet("color: #4ec9b0; font-size: 11px;")
        else:
            missing_count = sum(
                1 for inp in self.required_inputs 
                if not self.input_values.get(inp, "")
            )
            self.info_label.setText(
                f"⓵ Complete required inputs to run report ({missing_count} remaining)"
            )
            self.info_label.setStyleSheet("color: #a3a3a3; font-size: 11px;")
            
    def _get_input_description(self, input_name: str) -> str:
        """Get description for an input parameter
        
        Args:
            input_name: Name of the input
            
        Returns:
            Description text
        """
        # TODO: Could be enhanced by parsing from report metadata
        if "parts" in input_name.lower() or "list" in input_name.lower():
            return "Master parts list for comparison"
        elif "inventory" in input_name.lower():
            return "Current inventory snapshot"
        elif "bom" in input_name.lower():
            return "Optional BOM for cross-reference"
        else:
            return "Required input for report generation"
            
    def _on_save_draft(self):
        """Handle Save as Draft button"""
        # TODO: Implement draft saving
        print(f"[ReportConfigDialog] Save as draft: {self.input_values}")
        
    def _on_run_report(self):
        """Handle Run Report button"""
        # Collect all parameters
        parameters = self.input_values.copy()
        
        # Add settings
        if self.output_filename.text():
            parameters['output_filename'] = self.output_filename.text()
        parameters['case_sensitive'] = self.case_sensitive_checkbox.isChecked()
        parameters['include_timestamp'] = self.timestamp_checkbox.isChecked()
        
        # Emit signal with report title and parameters
        self.report_executed.emit(self.report_title, parameters)
        
        # Close dialog
        self.accept()
        
    def get_parameters(self) -> Dict[str, str]:
        """Get all configured parameters
        
        Returns:
            Dictionary of parameter names to values
        """
        parameters = self.input_values.copy()
        if self.output_filename.text():
            parameters['output_filename'] = self.output_filename.text()
        parameters['case_sensitive'] = self.case_sensitive_checkbox.isChecked()
        parameters['include_timestamp'] = self.timestamp_checkbox.isChecked()
        return parameters
