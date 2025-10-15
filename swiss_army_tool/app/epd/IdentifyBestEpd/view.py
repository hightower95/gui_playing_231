from PySide6.QtWidgets import (QWidget, QLineEdit, QHBoxLayout, QPushButton, QLabel,
                               QTextEdit, QTableView, QVBoxLayout, QProgressBar, QSizePolicy,
                               QApplication, QComboBox, QSpacerItem, QFrame, QFormLayout)
from PySide6.QtCore import Signal, Qt
from app.ui.base_sub_tab_view import BaseTabView
from app.ui.table_context_menu_mixin import TableContextMenuMixin
from app.core.config import UI_COLORS, UI_STYLES


class FilterWidget(QWidget):
    """Interactive filter tag widget - like e-commerce filter labels"""
    remove_requested = Signal(object)  # self

    def __init__(self, field_name, operator, value, parent=None):
        super().__init__(parent)
        self.field_name = field_name
        self.operator = operator
        self.value = value

        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create the main filter container with unified pill shape
        self.filter_container = QWidget()
        container_layout = QHBoxLayout(self.filter_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Filter text label
        filter_text = f"{self.field_name}: {self.operator} '{self.value}'"
        self.label = QLabel(filter_text)
        self.label.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                color: {UI_COLORS['filter_pill_text']};
                font-size: 12px;
                font-weight: 500;
                padding: 2px 12px;
                border: none;
            }}
        """)

        # Remove button (X) - integrated into the pill
        self.remove_btn = QPushButton("×")
        self.remove_btn.setFixedSize(24, 24)
        self.remove_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {UI_COLORS['filter_pill_text']};
                font-weight: bold;
                font-size: 16px;
                border: none;
                padding: 0px;
                margin-right: 8px;
            }}
            QPushButton:hover {{
                color: {UI_COLORS['danger_color']};
            }}
            QPushButton:pressed {{
                color: {UI_COLORS['danger_pressed']};
            }}
        """)

        # Add widgets to container
        container_layout.addWidget(self.label)
        container_layout.addWidget(self.remove_btn)

        # Style the entire container as one unified pill
        self.filter_container.setStyleSheet(f"""
            QWidget {{
                background-color: {UI_COLORS['filter_pill_background']};
                border-radius: 16px;
            }}
            QWidget:hover {{
                background-color: {UI_COLORS['filter_pill_hover']};
            }}
        """)

        # Add container to main layout
        layout.addWidget(self.filter_container)

        # Set fixed height for consistent appearance
        self.setFixedHeight(36)
        self.filter_container.setFixedHeight(32)

        # Connect signals
        self.remove_btn.clicked.connect(
            lambda: self.remove_requested.emit(self))

        # Add tooltip for better UX
        self.setToolTip(
            f"Filter: {self.field_name} {self.operator} {self.value}\nClick × to remove")

    def get_filter_data(self):
        """Return filter data as dict"""
        return {
            'field': self.field_name,
            'operator': self.operator,
            'value': self.value
        }


class IdentifyBestEpdView(BaseTabView, TableContextMenuMixin):
    filter_added = Signal(str, str, str)  # field, operator, value
    filter_removed = Signal(object)  # filter_data
    apply_filters = Signal()
    clear_filters = Signal()
    refresh_requested = Signal()
    export_requested = Signal(str)  # file_path

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # Track active filters
        self.active_filters = []

        # Double the header height from BaseTabView (80px -> 160px)
        self.header_frame.setFixedHeight(160)

        self._setup_header()
        self._setup_results_area()

    def _setup_header(self):
        """Setup the header with filter controls"""
        layout = QVBoxLayout(self.header_frame)

        # Title row
        title_layout = QHBoxLayout()
        title_label = QLabel("Identify Best EPD")
        title_label.setStyleSheet(
            f"font-weight: bold; font-size: 14px; color: {UI_COLORS['section_border']};")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        # Filter input row
        filter_layout = QHBoxLayout()

        # Field selector
        field_label = QLabel("Field:")
        self.field_combo = QComboBox()
        self.field_combo.addItems(["AWG", "Cable", "Description", "EPD"])
        self.field_combo.setMinimumWidth(100)

        # Operator selector
        operator_label = QLabel("Operator:")
        self.operator_combo = QComboBox()
        self.operator_combo.addItems(["equals", "not equals", "contains", "not contains",
                                      "less than", "greater than", "less than or equal",
                                      "greater than or equal"])
        self.operator_combo.setMinimumWidth(120)

        # Value input
        value_label = QLabel("Value:")
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Enter filter value...")
        self.value_input.setMinimumWidth(150)

        # Buttons
        self.add_filter_btn = QPushButton("Add Filter")
        self.add_filter_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {UI_COLORS['section_highlight_primary']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {UI_COLORS['section_highlight_secondary']};
            }}
        """)

        self.clear_filters_btn = QPushButton("Clear All")
        self.apply_filters_btn = QPushButton("Apply Filters")

        # Add widgets to filter layout
        filter_layout.addWidget(field_label)
        filter_layout.addWidget(self.field_combo)
        filter_layout.addWidget(operator_label)
        filter_layout.addWidget(self.operator_combo)
        filter_layout.addWidget(value_label)
        filter_layout.addWidget(self.value_input)
        filter_layout.addWidget(self.add_filter_btn)
        filter_layout.addWidget(self.clear_filters_btn)
        filter_layout.addWidget(self.apply_filters_btn)
        filter_layout.addStretch()

        # Action buttons row
        action_layout = QHBoxLayout()

        # Refresh and Export buttons
        self.refresh_button = QPushButton("Refresh Data")
        self.export_button = QPushButton("Export Results")

        # Progress bar for loading
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(20)
        self.progress_bar.setMaximumWidth(200)

        # Status label
        self.status_label = QLabel("Ready - Add filters to identify best EPD")
        self.status_label.setStyleSheet("color: gray; font-size: 10px;")

        action_layout.addWidget(self.refresh_button)
        action_layout.addWidget(self.export_button)
        action_layout.addStretch()
        action_layout.addWidget(self.progress_bar)
        action_layout.addWidget(self.status_label)

        # Add all layouts to main header layout (removed filters_frame from header)
        layout.addLayout(title_layout)
        layout.addLayout(filter_layout)
        layout.addLayout(action_layout)

        # Connect signals
        self.add_filter_btn.clicked.connect(self._add_filter)
        self.clear_filters_btn.clicked.connect(self._clear_filters)
        self.apply_filters_btn.clicked.connect(self._apply_filters)
        self.value_input.returnPressed.connect(self._add_filter)
        self.refresh_button.clicked.connect(self._emit_refresh)
        self.export_button.clicked.connect(self._emit_export)

    def _setup_results_area(self):
        """Setup the results area with table and context"""
        left_layout = QVBoxLayout(self.left_content_frame)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # Create table with custom styling
        self.table = QTableView()
        self._style_table()

        # Enable context menu for right-click using mixin
        self.setup_table_context_menu(self.table)

        # Create record count label for bottom of results
        self.record_count_label = QLabel("No filters applied")
        self.record_count_label.setStyleSheet(f"""
            QLabel {{
                color: gray;
                font-size: 10px;
                padding: 5px;
                border-top: 1px solid {UI_COLORS['dark_border']};
            }}
        """)
        self.record_count_label.setFixedHeight(25)

        # Add widgets to layout
        left_layout.addWidget(self.table, 1)
        left_layout.addWidget(self.record_count_label)

        # Setup filters display - use inherited context_box from BaseTabView
        self._setup_filters_display()

        # Update the inherited context_box placeholder
        self.context_box.setPlaceholderText(
            "Active filters and selected EPD details will appear here")

        # Use inherited footer_box from BaseTabView
        self.footer_box.setPlaceholderText(
            "EPD recommendation details will appear here")

    def _setup_filters_display(self):
        """Setup filters display using the inherited context_box from BaseTabView"""
        # Replace the context_box content with a custom widget for filters
        from PySide6.QtWidgets import QScrollArea

        # Create main container for filters
        self.filters_main_container = QWidget()
        main_layout = QVBoxLayout(self.filters_main_container)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(8)

        # Header for filters section
        filters_header = QLabel("Active Filters")
        filters_header.setStyleSheet(f"""
            QLabel {{
                font-weight: normal;
                color: {UI_COLORS['muted_text']};
                font-size: 14px;
                padding: 2px 5px;
                background-color: {UI_COLORS['section_label_background']};
                border-radius: 4px;
                margin-bottom: 1px;
            }}
        """)

    def _setup_filters_display(self):
        """Setup filters display using the inherited context_box from BaseTabView"""
        # Replace the context_box content with a custom widget for filters
        from PySide6.QtWidgets import QScrollArea

        # Create main container for filters
        self.filters_main_container = QWidget()
        main_layout = QVBoxLayout(self.filters_main_container)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(8)

        # Header for filters section
        filters_header = QLabel("Active Filters")
        filters_header.setStyleSheet("""
            QLabel {
                font-weight: normal;
                color: #888888;
                font-size: 14px;
                padding: 2px 5px;
                background-color: #121212;
                border-radius: 4px;
                margin-bottom: 1px;
            }
        """)
        filters_header.setFixedHeight(22)
        main_layout.addWidget(filters_header)

        # Scrollable area for filter pills - taller to accommodate more filters
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{ 
                border: none; 
                background-color: {UI_COLORS['light_background']};
                border-radius: 4px;
            }}
        """)

        # Container for filter pills
        self.filters_container = QWidget()
        self.filters_layout = QVBoxLayout(self.filters_container)
        self.filters_layout.setContentsMargins(8, 8, 8, 8)
        self.filters_layout.setSpacing(6)

        # No filters placeholder
        self.no_filters_label = QLabel("No active filters")
        self.filters_container.setStyleSheet(f"""
            QWidget {{
                background: {UI_COLORS['section_label_background']};
            }}
        """)
        self.no_filters_label.setStyleSheet(f"""
            QLabel {{
                color: {UI_COLORS['section_text']};
                background: {UI_COLORS['section_label_background']};
                font-style: italic;
                padding: 10px;
                text-align: center;
            }}
        """)
        self.filters_layout.addWidget(self.no_filters_label)

        # Add spacer to push content to top
        from PySide6.QtWidgets import QSpacerItem
        spacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.filters_layout.addItem(spacer)

        scroll_area.setWidget(self.filters_container)
        main_layout.addWidget(scroll_area)

        # EPD Details section header
        details_header = QLabel("Selected EPD Details")
        details_header.setStyleSheet(f"""
            QLabel {{
                font-weight: normal;
                color: {UI_COLORS['muted_text']};
                font-size: 14px;
                padding: 2px 5px;
                background-color: {UI_COLORS['section_label_background']};
                border-radius: 4px;
                margin-top: 4px;
                margin-bottom: 1px;
            }}
        """)
        details_header.setFixedHeight(22)
        main_layout.addWidget(details_header)

        # EPD details text area - matching no_filters_label styling
        self.epd_details_text = QLabel(
            "Select an EPD record to see details here")
        self.epd_details_text.setWordWrap(True)
        self.epd_details_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # color: #6c757d;
        self.epd_details_text.setStyleSheet(f"""
            QLabel {{
                color: {UI_COLORS['section_text']};
                background-color: {UI_COLORS['section_label_background']};
                font-style: italic;
                padding: 10px;
                text-align: center;
            }}
        """)
        main_layout.addWidget(self.epd_details_text)

        # Replace the context box content with our custom widget
        self._replace_context_content()

    def _replace_context_content(self):
        """Replace the inherited context_box with our custom filter display"""
        # Clear the existing context box content and replace with our widget
        parent_layout = self.context_box.parent().layout()
        if parent_layout:
            # Find the context box in the layout and replace it
            for i in range(parent_layout.count()):
                item = parent_layout.itemAt(i)
                if item.widget() == self.context_box:
                    parent_layout.removeWidget(self.context_box)
                    self.context_box.hide()
                    parent_layout.insertWidget(i, self.filters_main_container)
                    break

    def _update_context_display(self):
        """Update the filter display - no longer needed as filters are shown as widgets"""
        # This method is kept for compatibility but filters are now displayed as interactive widgets
        pass

    def _style_table(self):
        """Apply custom styling to the table using shared EPD config"""
        from app.epd.epd_config import apply_epd_table_styling
        apply_epd_table_styling(self.table)

    def _add_filter(self):
        """Add a new filter based on current inputs"""
        field = self.field_combo.currentText()
        operator = self.operator_combo.currentText()
        value = self.value_input.text().strip()

        if not value:
            self.show_error("Please enter a filter value")
            return

        # Create filter widget
        filter_widget = FilterWidget(field, operator, value)
        filter_widget.remove_requested.connect(self._remove_filter)

        # Add to active filters
        self.active_filters.append(filter_widget)

        # Add to flow layout
        self._add_filter_to_layout(filter_widget)

        # Hide "no filters" label
        self.no_filters_label.setVisible(False)

        # Update the context display to show new filters
        self._update_context_display()

        # Clear input
        self.value_input.clear()

        # Emit signal
        self.filter_added.emit(field, operator, value)

        # Update status
        self.status_label.setText(
            f"{len(self.active_filters)} filter(s) applied")

    def _add_filter_to_layout(self, filter_widget):
        """Add a filter widget to the layout - one per line"""
        # Insert before the spacer (which should be the last item)
        spacer_index = self.filters_layout.count() - 1
        if spacer_index < 0:
            spacer_index = 0
        self.filters_layout.insertWidget(spacer_index, filter_widget)

    def _remove_filter(self, filter_widget):
        """Remove a specific filter"""
        # Get filter data before removing
        filter_data = filter_widget.get_filter_data()

        # Remove from list
        self.active_filters.remove(filter_widget)

        # Remove from layout and clean up empty rows
        self._remove_filter_from_layout(filter_widget)
        filter_widget.deleteLater()

        # Show "no filters" label if no filters left
        if not self.active_filters:
            self.no_filters_label.setVisible(True)
            self.status_label.setText("No filters applied")
        else:
            self.status_label.setText(
                f"{len(self.active_filters)} filter(s) applied")

        self._update_context_display()

        # Emit signal
        self.filter_removed.emit(filter_data)

    def _remove_filter_from_layout(self, filter_widget):
        """Remove filter widget from layout"""
        # Simply remove the widget from the filters layout
        self.filters_layout.removeWidget(filter_widget)

    def _clear_filters(self):
        """Clear all filters"""
        # Remove all filter widgets
        for filter_widget in self.active_filters:
            self.filters_layout.removeWidget(filter_widget)
            filter_widget.deleteLater()

        # Show the no filters label
        self.no_filters_label.setVisible(True)

        self.active_filters.clear()
        self.status_label.setText("All filters cleared")
        self._update_context_display()

        # Emit signal
        self.clear_filters.emit()

    def _apply_filters(self):
        """Apply current filters"""
        if not self.active_filters:
            self.show_error("No filters to apply")
            return

        self.apply_filters.emit()

    def _emit_refresh(self):
        """Emit refresh signal"""
        self.refresh_requested.emit()

    def _emit_export(self):
        """Emit export signal"""
        self.export_requested.emit("best_epd_results.csv")

    def get_active_filters(self):
        """Get all active filters as list of dicts"""
        return [fw.get_filter_data() for fw in self.active_filters]

    def display_context(self, context_text: str):
        """Display context information - this will update the EPD details section"""
        self.epd_details_text.setText(context_text)

    def display_footer(self, footer_text: str):
        """Display footer information"""
        self.footer_box.setPlainText(footer_text)

    def show_loading(self, show: bool = True):
        """Show/hide loading state"""
        self.progress_bar.setVisible(show)
        self.add_filter_btn.setEnabled(not show)
        self.apply_filters_btn.setEnabled(not show)
        self.refresh_button.setEnabled(not show)
        self.export_button.setEnabled(not show)

        if show:
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            self.status_label.setText("Processing...")
        else:
            self.progress_bar.setRange(0, 100)

    def update_loading_progress(self, progress: int, message: str):
        """Update loading progress"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(progress)
        self.status_label.setText(message)

        if progress >= 100:
            from PySide6.QtCore import QTimer
            QTimer.singleShot(1000, lambda: self.show_loading(False))

    def show_error(self, error_message: str):
        """Show error state"""
        self.show_loading(False)
        self.status_label.setText(f"Error: {error_message}")
        self.status_label.setStyleSheet("color: red; font-size: 10px;")

        # Reset status after 5 seconds
        from PySide6.QtCore import QTimer
        QTimer.singleShot(5000, self._reset_status)

    def _reset_status(self):
        """Reset status to normal"""
        filter_count = len(self.active_filters)
        if filter_count == 0:
            self.status_label.setText(
                "Ready - Add filters to identify best EPD")
        else:
            self.status_label.setText(f"{filter_count} filter(s) applied")
        self.status_label.setStyleSheet("color: gray; font-size: 10px;")

    def update_record_count(self, count: int, total: int = None):
        """Update the record count display"""
        if total is None:
            self.record_count_label.setText(f"Found {count} matching EPDs")
        else:
            self.record_count_label.setText(
                f"Found {count} of {total} EPDs matching criteria")
