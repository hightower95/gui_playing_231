"""
Connector Lookup View - Search and filter connectors
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QTableView, QListWidget, QGridLayout, QFrame, QSizePolicy,
                               QComboBox, QLineEdit)
from PySide6.QtCore import Signal, Qt, QSize
from app.ui.base_sub_tab_view import BaseTabView
from app.ui.table_context_menu_mixin import TableContextMenuMixin
from app.core.config import UI_COLORS, UI_STYLES
from app.connector.Lookup.config import FAMILIES, SHELL_TYPES, INSERT_ARRANGEMENTS, SOCKET_TYPES, KEYINGS, MATERIALS


class LookupConnectorView(BaseTabView, TableContextMenuMixin):
    """View for looking up connectors with collapsible filters"""

    # Signals
    search_requested = Signal(dict)  # filter criteria
    refresh_requested = Signal()
    export_requested = Signal()
    clear_filters_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_filter_expanded = False  # Hidden by default
        self.HEADER_HEIGHT_COLLAPSED = 140  # Height when only search box is visible

        # Calculate expanded height based on number of filter rows
        # With 3 columns, we have 2 rows max
        num_filter_rows = 2  # 2 rows in the grid layout
        # Height per filter row (list widget 105px + spacing 25px)
        row_height = 130
        base_height = 140  # Collapsed height
        filter_padding = 30  # Increased padding
        self.HEADER_HEIGHT_EXPANDED = base_height + \
            (num_filter_rows * row_height) + filter_padding

        self._setup_header()
        self._setup_results()
        self._setup_context_menu()

    def _create_dual_column_multiselect(self, items: list) -> tuple:
        """Create two QListWidgets side-by-side that appear as one with shared scrolling"""
        # Split items into two columns - balance them evenly
        mid_point = (len(items) + 1) // 2
        left_items = items[:mid_point]
        right_items = items[mid_point:]

        # If odd number of items, add disabled padding items to both columns for synchronized scrolling
        if len(items) % 2 == 1:
            # Add empty padding item to left
            left_items = left_items + ["", ""]
            right_items = right_items + [""]  # Add empty padding item to right

        # Determine width based on content length
        # If all items are 5 characters or less, use 50% width (55px), otherwise use full width (110px)
        max_length = max(len(item) for item in items) if items else 0
        width = 55 if max_length <= 5 else 110

        # For narrow lists, add a visible separator border; for wide lists, no border
        right_border_style = "1px solid #555555" if width == 55 else "none"
        # For narrow lists, remove left border to bring closer; for wide lists, no left border
        left_border_style = "none"

        # Style for left list (light grey right border for narrow lists, no border for wide lists)
        left_style = f"""
            QListWidget {{
                background-color: {UI_COLORS['section_background']};
                color: {UI_COLORS['highlight_text']};
                border: 1px solid {UI_COLORS['frame_border']};
                border-right: {right_border_style};
                border-top-left-radius: 3px;
                border-bottom-left-radius: 3px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                min-width: 110px;
                max-width: 110px;
                min-height: 95px;
                max-height: 95px;
                padding: 0px;
                margin: 0px;
            }}
            QListWidget::item {{
                padding: 3px;
                min-height: 25px;
            }}
            QListWidget::item:selected {{
                background-color: {UI_COLORS['section_highlight_primary']};
                color: white;
            }}
            QScrollBar:vertical {{
                width: 0px;  /* Hide scrollbar on left widget */
            }}
        """

        # Style for right list (no left border for all cases, visible scrollbar)
        right_style = f"""
            QListWidget {{
                background-color: {UI_COLORS['section_background']};
                color: {UI_COLORS['highlight_text']};
                border: 1px solid {UI_COLORS['frame_border']};
                border-left: {right_border_style};
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
                min-width: 110px;
                max-width: 110px;
                min-height: 95px;
                max-height: 95px;
                padding: 0px;
                margin: 0px;
            }}
            QListWidget::item {{
                padding: 3px;
                min-height: 25px;
            }}
            QListWidget::item:selected {{
                background-color: {UI_COLORS['section_highlight_primary']};
                color: white;
            }}
            QScrollBar:vertical {{
                border: 1px solid {UI_COLORS['frame_border']};
                background: {UI_COLORS['section_background']};
                width: 12px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {UI_COLORS['section_highlight_primary']};
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {UI_COLORS['filter_pill_hover']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """

        # Create left list
        left_list = QListWidget()
        left_list.setSelectionMode(QListWidget.MultiSelection)
        for item in left_items:
            left_list.addItem(item)
            # Disable empty padding items
            if item == "":
                idx = left_list.count() - 1
                item_widget = left_list.item(idx)
                if item_widget:
                    # Make unselectable and invisible
                    item_widget.setFlags(Qt.NoItemFlags)
        left_list.setStyleSheet(left_style)
        left_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left_list.setContentsMargins(0, 0, 0, 0)

        # Create right list
        right_list = QListWidget()
        right_list.setSelectionMode(QListWidget.MultiSelection)
        for item in right_items:
            right_list.addItem(item)
            # Disable empty padding items
            if item == "":
                idx = right_list.count() - 1
                item_widget = right_list.item(idx)
                if item_widget:
                    # Make unselectable and invisible
                    item_widget.setFlags(Qt.NoItemFlags)
        right_list.setStyleSheet(right_style)
        right_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        right_list.setContentsMargins(0, 0, 0, 0)

        # Synchronize scrolling
        left_list.verticalScrollBar().valueChanged.connect(
            right_list.verticalScrollBar().setValue
        )
        right_list.verticalScrollBar().valueChanged.connect(
            left_list.verticalScrollBar().setValue
        )

        # Handle double-click to select only that item (deselect others in both lists)
        def make_exclusive_handler(this_list, other_list):
            def on_double_click(item):
                # Clear selection in other list
                other_list.clearSelection()
                # Clear selection in this list
                this_list.clearSelection()
                # Select only the double-clicked item
                item.setSelected(True)
            return on_double_click

        # Handle Ctrl+Click to select all items in both lists
        def make_ctrl_click_handler(this_list, other_list):
            def on_item_clicked(item):
                from PySide6.QtWidgets import QApplication
                modifiers = QApplication.keyboardModifiers()
                if modifiers == Qt.ControlModifier:
                    # Select all items in both lists
                    this_list.selectAll()
                    other_list.selectAll()
            return on_item_clicked

        left_list.itemDoubleClicked.connect(
            make_exclusive_handler(left_list, right_list))
        right_list.itemDoubleClicked.connect(
            make_exclusive_handler(right_list, left_list))

        left_list.itemClicked.connect(
            make_ctrl_click_handler(left_list, right_list))
        right_list.itemClicked.connect(
            make_ctrl_click_handler(right_list, left_list))

        return left_list, right_list

    def _create_labeled_filter(self, label_text: str, items: list) -> tuple:
        """Create a labeled dual-column multiselect filter component

        Returns:
            tuple: (container_widget, left_list, right_list)
        """
        # Create container with vertical layout (label on top, lists below)
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        # Reduced spacing between label and lists
        container_layout.setSpacing(3)

        # Create label
        label = QLabel(label_text)
        label.setStyleSheet(f"""
            QLabel {{
                font-weight: bold; 
                color: {UI_COLORS['highlight_text']};
                font-size: 9pt;
                padding-bottom: 0px;
                margin-bottom: 0px;
            }}
        """)

        # Create dual-column multiselect
        left_list, right_list = self._create_dual_column_multiselect(items)

        # Create horizontal container for the two lists
        lists_container = QWidget()
        lists_layout = QHBoxLayout(lists_container)
        lists_layout.setContentsMargins(0, 0, 0, 0)
        lists_layout.setSpacing(0)
        lists_layout.addWidget(left_list)
        lists_layout.addWidget(right_list)

        # Add label and lists to container
        container_layout.addWidget(label)
        container_layout.addWidget(lists_container)

        return container, left_list, right_list

    def _setup_header(self):
        """Setup header with search box and collapsible filter section"""
        # Increase header height for connector lookup
        self.header_frame.setFixedHeight(self.HEADER_HEIGHT_COLLAPSED)

        # Create header layout
        header_layout = QVBoxLayout(self.header_frame)
        header_layout.setContentsMargins(10, 10, 10, 10)
        header_layout.setSpacing(8)

        # === Title Row ===
        title_row = QHBoxLayout()

        title_label = QLabel("Connector Lookup")
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14pt;
                font-weight: bold;
                color: {UI_COLORS['section_border']};
            }}
        """)

        title_row.addWidget(title_label)
        title_row.addStretch()

        header_layout.addLayout(title_row)

        # === Search Controls Row ===
        search_controls_layout = QHBoxLayout()
        search_controls_layout.setSpacing(10)

        # Create search container (similar to SearchEpdView)
        search_container = QWidget()
        search_container_layout = QHBoxLayout(search_container)
        search_container_layout.setContentsMargins(0, 0, 0, 0)
        search_container_layout.setSpacing(5)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "part code, number, alias or property")
        self.search_input.setMinimumHeight(30)  # Match SearchEpd height
        self.search_input.returnPressed.connect(self._on_search_clicked)

        self.search_btn = QPushButton("Search")
        self.search_btn.setMinimumHeight(30)

        # self.refresh_btn = QPushButton("Refresh")
        # self.refresh_btn.setMinimumHeight(30)
        # self.refresh_btn.clicked.connect(lambda: self.refresh_requested.emit())

        # self.export_btn = QPushButton("Export")
        # self.export_btn.setMinimumHeight(30)
        # self.export_btn.clicked.connect(lambda: self.export_requested.emit())

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setMinimumHeight(30)

        search_container_layout.addWidget(
            self.search_input, 3)  # Give search input more space
        search_container_layout.addWidget(self.search_btn)
        # search_container_layout.addWidget(self.refresh_btn)
        # search_container_layout.addWidget(self.export_btn)
        search_container_layout.addWidget(self.clear_btn)

        # Set size policy to limit width (similar to SearchEpdView)
        search_container.setMaximumWidth(int(self.header_frame.width() * 0.7))

        search_controls_layout.addWidget(search_container)
        search_controls_layout.addStretch()

        header_layout.addLayout(search_controls_layout)

        # Connect signals
        self.search_btn.clicked.connect(self._on_search_clicked)
        self.clear_btn.clicked.connect(self._on_clear_clicked)

        # === Advanced Search Toggle ===
        advanced_search_row = QHBoxLayout()
        advanced_search_row.setContentsMargins(
            0, 15, 0, 0)  # No bottom spacing

        self.advanced_search_label = QLabel(
            "▶ Advanced Search")  # Start collapsed
        self.advanced_search_label.setStyleSheet(f"""
            QLabel {{
                color: {UI_COLORS['section_highlight_primary']};
                font-weight: bold;
                font-size: 10pt;
            }}
            QLabel:hover {{
                color: {UI_COLORS['filter_pill_hover']};
                text-decoration: underline;
            }}
        """)
        self.advanced_search_label.setCursor(Qt.PointingHandCursor)
        self.advanced_search_label.mousePressEvent = lambda event: self._toggle_filters()

        advanced_search_row.addWidget(self.advanced_search_label)
        advanced_search_row.addStretch()

        header_layout.addLayout(advanced_search_row)

        # === Collapsible Filter Section ===
        self.filter_container = QFrame()
        self.filter_container.setFrameShape(QFrame.StyledPanel)
        self.filter_container.setStyleSheet(f"""
            QFrame {{
                border-radius: 5px;
                padding: 5px;
                padding-top: 0px;
            }}
        """)
        self.filter_container.setVisible(False)  # Start hidden

        filter_layout = QGridLayout(self.filter_container)
        filter_layout.setContentsMargins(5, 0, 5, 5)  # Reduced margins
        filter_layout.setHorizontalSpacing(20)  # Reduced horizontal spacing
        # Reduced vertical spacing between rows
        filter_layout.setVerticalSpacing(12)

        # === Column 1 ===

        # Row 0: Standard
        standard_container, self.standard_list_left, self.standard_list_right = self._create_labeled_filter(
            "Standard:", FAMILIES)

        # Row 1: Shell Type
        shell_type_container, self.shell_type_list_left, self.shell_type_list_right = self._create_labeled_filter(
            "Shell Type:", SHELL_TYPES)

        # === Column 2 ===

        # Row 0: Insert Arrangement
        insert_arrangement_container, self.insert_arrangement_list_left, self.insert_arrangement_list_right = self._create_labeled_filter(
            "Insert Arrangement:", INSERT_ARRANGEMENTS)

        # Row 1: Material
        material_container, self.material_list_left, self.material_list_right = self._create_labeled_filter(
            "Material:", MATERIALS)

        # === Column 3 ===

        # Row 0: Socket Type
        socket_type_container, self.socket_type_list_left, self.socket_type_list_right = self._create_labeled_filter(
            "Socket Type:", SOCKET_TYPES)

        # Row 1: Keying
        keying_container, self.keying_list_left, self.keying_list_right = self._create_labeled_filter(
            "Keying:", KEYINGS)

        # Add to grid in 3 columns, 2 rows
        filter_layout.addWidget(standard_container, 0, 0)
        filter_layout.addWidget(shell_type_container, 1, 0)
        filter_layout.addWidget(insert_arrangement_container, 0, 1)
        filter_layout.addWidget(material_container, 1, 1)
        filter_layout.addWidget(socket_type_container, 0, 2)
        filter_layout.addWidget(keying_container, 1, 2)

        # Add stretch column
        filter_layout.setColumnStretch(3, 1)

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

        # Set custom text for the inherited record_count_label
        self.record_count_label.setText("Showing only results from database")

    def _setup_context_menu(self):
        """Setup right-click context menu for table"""
        self.setup_table_context_menu(
            self.table,
            actions=[
                ("View Details", self._on_view_details),
                ("Find Alternative", self._on_find_alternative),
                ("Find Opposite", self._on_find_opposite),
                ("Export Selection", self._on_export_selection)
            ],
            include_copy_row=True
        )

    def _toggle_filters(self):
        """Toggle filter section visibility"""
        self.is_filter_expanded = not self.is_filter_expanded
        self.filter_container.setVisible(self.is_filter_expanded)

        if self.is_filter_expanded:
            self.advanced_search_label.setText("▼ Advanced Search")
            # Adjusted for new compact layout
            self.header_frame.setFixedHeight(
                self.HEADER_HEIGHT_EXPANDED)  # Height when expanded
        else:
            self.advanced_search_label.setText("▶ Advanced Search")
            self.header_frame.setFixedHeight(
                self.HEADER_HEIGHT_COLLAPSED)  # Height for search box only

    def _on_search_clicked(self):
        """Emit search signal with selected filters"""
        filters = self._get_selected_filters()
        self.search_requested.emit(filters)

    def _on_clear_clicked(self):
        """Clear all filter selections and search input"""
        self.search_input.clear()
        self.standard_list_left.clearSelection()
        self.standard_list_right.clearSelection()
        self.shell_type_list_left.clearSelection()
        self.shell_type_list_right.clearSelection()
        self.insert_arrangement_list_left.clearSelection()
        self.insert_arrangement_list_right.clearSelection()
        self.material_list_left.clearSelection()
        self.material_list_right.clearSelection()
        self.socket_type_list_left.clearSelection()
        self.socket_type_list_right.clearSelection()
        self.keying_list_left.clearSelection()
        self.keying_list_right.clearSelection()
        self.clear_filters_requested.emit()

    def _get_selected_filters(self) -> dict:
        """Get currently selected filter values from dual-column lists"""
        return {
            'search_text': self.search_input.text().strip(),
            'standard': [item.text() for item in self.standard_list_left.selectedItems()] +
            [item.text() for item in self.standard_list_right.selectedItems()],
            'shell_type': [item.text() for item in self.shell_type_list_left.selectedItems()] +
            [item.text() for item in self.shell_type_list_right.selectedItems()],
            'insert_arrangement': [item.text() for item in self.insert_arrangement_list_left.selectedItems()] +
            [item.text()
             for item in self.insert_arrangement_list_right.selectedItems()],
            'material': [item.text() for item in self.material_list_left.selectedItems()] +
            [item.text()
             for item in self.material_list_right.selectedItems()],
            'socket_type': [item.text() for item in self.socket_type_list_left.selectedItems()] +
            [item.text() for item in self.socket_type_list_right.selectedItems()],
            'keying': [item.text() for item in self.keying_list_left.selectedItems()] +
            [item.text() for item in self.keying_list_right.selectedItems()]
        }

    def _on_view_details(self, index, row, column):
        """Handle view details action"""
        print(f"View details for row {row}, column {column}")
        # To be implemented

    def _on_find_alternative(self, index, row, column):
        """Handle find alternative action"""
        print(f"Find alternative for row {row}")
        # To be implemented

    def _on_find_opposite(self, index, row, column):
        """Handle find opposite action"""
        print(f"Find opposite for row {row}")
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
