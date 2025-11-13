from PySide6.QtWidgets import (QWidget, QLineEdit, QHBoxLayout, QPushButton, QLabel,
                               QTextEdit, QTableView, QVBoxLayout, QProgressBar, QSizePolicy,
                               QApplication)
from PySide6.QtCore import Signal, Qt
from productivity_core.ui.base_sub_tab_view import BaseTabView
from productivity_core.ui.components.label import StandardLabel, TextStyle
from productivity_core.ui.table_context_menu_mixin import TableContextMenuMixin
from productivity_core.core.config import UI_COLORS


class SearchEpdView(BaseTabView, TableContextMenuMixin):
    searchEPDTriggered = Signal(str)
    rowSelected = Signal(dict)
    refresh_requested = Signal()
    export_requested = Signal(str)  # file_path

    def __init__(self, parent=None):
        # header = QWidget()
        # layout = QHBoxLayout()
        # # self.search_input = QLineEdit()
        # # self.search_input.setPlaceholderText("Search EPD...")
        # # self.search_button = QPushButton("Search")
        # # layout.addWidget(self.search_input)
        # # layout.addWidget(self.search_button)
        # # header.setLayout(layout)

        # --- Build base layout ---
        super().__init__(parent=parent)
        self._setup_header()
        self._setup_results_area()

    def _setup_header(self):
        # Add search bar and button inside header_frame
        self.header_frame.setFixedHeight(120)

        layout = QVBoxLayout(self.header_frame)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title row
        title_row = QHBoxLayout()
        title_label = StandardLabel("Search EPD", style=TextStyle.TITLE)
        title_row.addWidget(title_label)
        title_row.addStretch()
        title_row.addWidget(self.help_label)  # Add help button from base class
        layout.addLayout(title_row)

        # Search controls row
        search_row = QHBoxLayout()

        # Search controls
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search EPD records...")
        self.search_button = QPushButton("Search")

        # Action buttons
        self.refresh_button = QPushButton("Refresh")
        self.export_button = QPushButton("Export")

        # Progress bar for loading
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(20)

        # Status label
        self.status_label = StandardLabel("Ready", style=TextStyle.STATUS)

        # Create a container widget for the search controls
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.refresh_button)
        search_layout.addWidget(self.export_button)

        # Create progress container
        progress_container = QWidget()
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)

        # Add the containers to search row
        search_row.addWidget(search_container)
        search_row.addWidget(progress_container)
        search_row.addStretch()  # This pushes the controls to the left

        layout.addLayout(search_row)

        # Set size policy to limit width
        search_container.setMaximumWidth(int(self.header_frame.width() * 0.65))
        progress_container.setMaximumWidth(200)

        # Connect signals
        self.search_button.clicked.connect(self._emit_search)
        self.search_input.returnPressed.connect(self._emit_search)
        self.search_input.textChanged.connect(self._emit_search)
        self.refresh_button.clicked.connect(self._emit_refresh)
        self.export_button.clicked.connect(self._emit_export)

    def _setup_results_area(self):
        left_layout = QVBoxLayout(self.left_content_frame)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # Create table with custom styling
        self.table = QTableView()
        self._style_table()

        # Enable context menu for right-click using mixin
        self.setup_table_context_menu(
            self.table,
            actions=[
                ("Open PDF", self._on_open_pdf)
            ],
            include_copy_row=True
        )

        # Add table to layout - the record_count_label is inherited from BaseTabView
        # Stretch factor 1 = takes available space
        left_layout.addWidget(self.table, 1)

        # Use the inherited context_box from BaseTabView (no need to create a new one)
        self.context_box.setPlaceholderText(
            "Select an EPD record to see details here")

        # Use the inherited footer_box from BaseTabView (no need to create a new one)
        self.footer_box.setPlaceholderText("Footer info for selected EPD")

    def _copy_context_to_clipboard(self):
        """Copy the context box content to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.context_box.toPlainText())

    def _style_table(self):
        """Apply custom styling to the table using shared EPD config"""
        from productivity_core.epd.epd_config import apply_epd_table_styling
        apply_epd_table_styling(self.table)

    def _emit_search(self):
        text = self.search_input.text().strip()
        self.search_input.blockSignals(True)
        self.search_input.setText(text)  # Clean up whitespace
        self.search_input.blockSignals(False)
        self.searchEPDTriggered.emit(text)

    def _emit_refresh(self):
        """Emit refresh signal"""
        self.refresh_requested.emit()

    def _emit_export(self):
        """Emit export signal"""
        # In a real implementation, this would open a file dialog
        # For now, just emit with a default path

        self.export_requested.emit("epd_export.csv")

    def display_context(self, context_text: str):
        # print("reached")
        self.context_box.setPlainText(context_text)

    def display_footer(self, footer_text: str):
        self.footer_box.setPlainText(footer_text)

    def show_loading(self, show: bool = True):
        """Show/hide loading state"""
        self.progress_bar.setVisible(show)
        self.search_input.setEnabled(not show)
        self.search_button.setEnabled(not show)
        self.export_button.setEnabled(not show)

        if show:
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            self.status_label.setText("Loading...")
        else:
            self.progress_bar.setRange(0, 100)
            self.status_label.setText("Ready")

    def update_loading_progress(self, progress: int, message: str):
        """Update loading progress"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(progress)
        self.status_label.setText(message)
        print(f"Loading progress: {progress}% - {message}")
        if progress >= 100:
            # Hide progress bar after a short delay
            from PySide6.QtCore import QTimer
            QTimer.singleShot(1000, lambda: self.show_loading(False))

    def show_error(self, error_message: str):
        """Show error state"""
        self.show_loading(False)
        self.status_label.setText(f"Error: {error_message}")

        # Reset status after 5 seconds
        from PySide6.QtCore import QTimer
        QTimer.singleShot(5000, self._reset_status)

    def _reset_status(self):
        """Reset status to normal"""
        self.status_label.setText("Ready")

    def _on_open_pdf(self, index, row, column):
        """Handle Open PDF action from context menu"""
        model = self.table.model()

        if model:
            # Get the part number or relevant identifier from the row
            part_number = None

            # Try to find a part number column
            for col_idx in range(model.columnCount()):
                header_data = model.headerData(
                    col_idx, Qt.Orientation.Horizontal)
                if header_data and 'Part' in str(header_data):
                    part_number = model.data(model.index(row, col_idx))
                    break

            if not part_number:
                # Fallback to first column
                part_number = model.data(model.index(row, 0))

            # Update status with message
            self.status_label.setText(
                f"Opening PDF for: {part_number} - Not yet implemented")
            print(f"Open PDF requested for row {row}: {part_number}")
        else:
            self.status_label.setText("Cannot open PDF - no data available")

    def update_record_count(self, count: int, total: int = None):
        """Update the record count display"""
        if total is None:
            self.record_count_label.setText(f"Showing {count} records")
        else:
            self.record_count_label.setText(
                f"Showing {count} of {total} records")
