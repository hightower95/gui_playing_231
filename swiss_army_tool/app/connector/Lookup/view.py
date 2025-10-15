"""
Connector Lookup View - Search and filter connectors
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QTableView, QListWidget, QGridLayout, QFrame, QSizePolicy)
from PySide6.QtCore import Signal, Qt
from app.ui.base_sub_tab_view import BaseTabView
from app.ui.table_context_menu_mixin import TableContextMenuMixin
from app.core.config import UI_COLORS, UI_STYLES
from app.connector.Lookup.config import CONNECTOR_TYPES, GENDERS, MANUFACTURERS


class LookupConnectorView(BaseTabView, TableContextMenuMixin):
    """View for looking up connectors with collapsible filters"""

    # Signals
    search_requested = Signal(dict)  # filter criteria
    refresh_requested = Signal()
    export_requested = Signal()
    clear_filters_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_filter_expanded = True
        self._setup_header()
        self._setup_results()
        self._setup_context_menu()

    def _setup_header(self):
        """Setup header with collapsible filter section"""
        # Create header layout
        header_layout = QVBoxLayout(self.header_frame)
        header_layout.setContentsMargins(10, 5, 10, 5)
        header_layout.setSpacing(5)

        # === Title and Toggle Row ===
        title_row = QHBoxLayout()

        title_label = QLabel("Connector Lookup")
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14pt;
                font-weight: bold;
                color: {UI_COLORS['section_border']};
            }}
        """)

        self.toggle_filters_btn = QPushButton("▼ Hide Filters")
        self.toggle_filters_btn.setFixedSize(120, 25)
        self.toggle_filters_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {UI_COLORS['section_highlight_primary']};
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: {UI_COLORS['filter_pill_hover']};
            }}
        """)
        self.toggle_filters_btn.clicked.connect(self._toggle_filters)

        # Action buttons
        self.search_btn = QPushButton("Search")
        self.search_btn.setFixedSize(80, 25)
        self.search_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {UI_COLORS['section_highlight_primary']};
                color: white;
                border: none;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {UI_COLORS['filter_pill_hover']};
            }}
        """)
        self.search_btn.clicked.connect(self._on_search_clicked)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFixedSize(80, 25)
        self.clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {UI_COLORS['muted_text']};
                color: white;
                border: none;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {UI_COLORS['section_border']};
            }}
        """)
        self.clear_btn.clicked.connect(self._on_clear_clicked)

        title_row.addWidget(title_label)
        title_row.addStretch()
        title_row.addWidget(self.toggle_filters_btn)
        title_row.addWidget(self.search_btn)
        title_row.addWidget(self.clear_btn)

        header_layout.addLayout(title_row)

        # === Collapsible Filter Section ===
        self.filter_container = QFrame()
        self.filter_container.setFrameShape(QFrame.StyledPanel)
        self.filter_container.setStyleSheet(f"""
            QFrame {{
                background-color: {UI_COLORS['light_background']};
                border: 1px solid {UI_COLORS['frame_border']};
                border-radius: 5px;
            }}
        """)

        filter_layout = QGridLayout(self.filter_container)
        filter_layout.setContentsMargins(10, 10, 10, 10)
        filter_layout.setSpacing(10)

        # Create multi-select lists in 2-column grid
        # Column 1: Connector Type
        type_label = QLabel("Connector Type:")
        type_label.setStyleSheet("font-weight: bold;")
        self.type_list = QListWidget()
        self.type_list.setSelectionMode(QListWidget.MultiSelection)
        self.type_list.addItems(CONNECTOR_TYPES)
        self.type_list.setMaximumHeight(150)

        # Column 2: Gender
        gender_label = QLabel("Gender:")
        gender_label.setStyleSheet("font-weight: bold;")
        self.gender_list = QListWidget()
        self.gender_list.setSelectionMode(QListWidget.MultiSelection)
        self.gender_list.addItems(GENDERS)
        self.gender_list.setMaximumHeight(150)

        # Row 2, Column 1: Manufacturer
        manufacturer_label = QLabel("Manufacturer:")
        manufacturer_label.setStyleSheet("font-weight: bold;")
        self.manufacturer_list = QListWidget()
        self.manufacturer_list.setSelectionMode(QListWidget.MultiSelection)
        self.manufacturer_list.addItems(MANUFACTURERS)
        self.manufacturer_list.setMaximumHeight(150)

        # Add to grid (2 columns)
        filter_layout.addWidget(type_label, 0, 0)
        filter_layout.addWidget(self.type_list, 1, 0)

        filter_layout.addWidget(gender_label, 0, 1)
        filter_layout.addWidget(self.gender_list, 1, 1)

        filter_layout.addWidget(manufacturer_label, 2, 0)
        filter_layout.addWidget(self.manufacturer_list, 3, 0)

        header_layout.addWidget(self.filter_container)

    def _setup_results(self):
        """Setup results table"""
        # Create table in the left content area
        results_layout = QVBoxLayout(self.left_content_frame)
        results_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableView()
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.SingleSelection)
        self.table.setAlternatingRowColors(True)

        results_layout.addWidget(self.table)

    def _setup_context_menu(self):
        """Setup right-click context menu for table"""
        self.setup_table_context_menu(
            self.table,
            [
                ("View Details", self._on_view_details),
                ("Copy Part Number", self._on_copy_part_number),
                ("Export Selection", self._on_export_selection)
            ]
        )

    def _toggle_filters(self):
        """Toggle filter section visibility"""
        self.is_filter_expanded = not self.is_filter_expanded
        self.filter_container.setVisible(self.is_filter_expanded)

        if self.is_filter_expanded:
            self.toggle_filters_btn.setText("▼ Hide Filters")
            self.header_frame.setFixedHeight(300)
        else:
            self.toggle_filters_btn.setText("▶ Show Filters")
            self.header_frame.setFixedHeight(50)

    def _on_search_clicked(self):
        """Emit search signal with selected filters"""
        filters = self._get_selected_filters()
        self.search_requested.emit(filters)

    def _on_clear_clicked(self):
        """Clear all filter selections"""
        self.type_list.clearSelection()
        self.gender_list.clearSelection()
        self.manufacturer_list.clearSelection()
        self.clear_filters_requested.emit()

    def _get_selected_filters(self) -> dict:
        """Get currently selected filter values"""
        return {
            'type': [item.text() for item in self.type_list.selectedItems()],
            'gender': [item.text() for item in self.gender_list.selectedItems()],
            'manufacturer': [item.text() for item in self.manufacturer_list.selectedItems()]
        }

    def _on_view_details(self, index, row, column):
        """Handle view details action"""
        print(f"View details for row {row}, column {column}")
        # To be implemented

    def _on_copy_part_number(self, index, row, column):
        """Handle copy part number action"""
        print(f"Copy part number for row {row}")
        # To be implemented

    def _on_export_selection(self, index, row, column):
        """Handle export selection action"""
        print(f"Export selection for row {row}")
        # To be implemented

    def show_loading(self, visible: bool):
        """Show/hide loading indicator"""
        # To be implemented with loading overlay
        pass

    def update_loading_progress(self, percent: int, message: str):
        """Update loading progress"""
        self.footer_box.setText(f"Loading: {percent}% - {message}")

    def show_error(self, error_message: str):
        """Display error message"""
        self.footer_box.setText(f"Error: {error_message}")
        self.footer_box.setStyleSheet(f"color: {UI_COLORS['danger_color']};")
