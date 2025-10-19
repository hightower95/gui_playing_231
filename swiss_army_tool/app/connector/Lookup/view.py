"""
Connector Lookup View - Search and filter connectors
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QTableView, QListWidget, QGridLayout, QFrame, QSizePolicy,
                               QComboBox, QLineEdit, QMenu, QListWidgetItem)
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QCursor, QPixmap
from app.ui.base_sub_tab_view import BaseTabView
from app.ui.components.label import StandardLabel, TextStyle
from app.ui.table_context_menu_mixin import TableContextMenuMixin
from app.core.config import UI_COLORS, UI_STYLES
from app.connector.Lookup.config import (
    FAMILIES, SHELL_TYPES, SHELL_SIZES, INSERT_ARRANGEMENTS,
    SOCKET_TYPES, KEYINGS, MATERIALS
)
from app.shared.feature_toggles import ENABLE_PINOUT_IMAGE
from collections import deque
from datetime import datetime, timedelta


class LookupConnectorView(BaseTabView, TableContextMenuMixin):
    """View for looking up connectors with collapsible filters"""

    # Signals
    search_requested = Signal(dict)  # filter criteria
    standards_changed = Signal(list)  # selected standards changed
    refresh_requested = Signal()
    export_requested = Signal()
    clear_filters_requested = Signal()
    reset_requested = Signal()  # Reset tab to initial state
    find_alternative_requested = Signal(str)  # part_code
    find_opposite_requested = Signal(str)  # part_code

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_filter_expanded = False  # Hidden by default
        self.HEADER_HEIGHT_COLLAPSED = 140  # Height when only search box is visible

        # Recent searches tracking (max 35 recent searches, show 15 before scrolling)
        self.recent_searches = deque(maxlen=35)
        self.recent_searches_data = {}  # Maps description to filters dict
        self.recent_searches_timestamps = {}  # Maps description to timestamp
        # Maps description to first result (Part Number, Part Code)
        self.recent_searches_results = {}
        # Flag to prevent re-adding when restoring from history
        self._is_restoring_search = False
        # Flag to allow updating most recent search
        self._most_recent_search_open_for_modification = False
        self._most_recent_search_timestamp = None  # Timestamp of most recent search

        # Calculate expanded height based on number of filter rows
        # With 4 columns, we now have 2 rows (7 filters: 2, 2, 2, 1)
        num_filter_rows = 2  # 2 rows in the grid layout
        # Height per filter row (list widget 105px + spacing 25px)
        row_height = 130
        base_height = 140  # Collapsed height
        filter_padding = 30  # Increased padding
        self.HEADER_HEIGHT_EXPANDED = base_height + \
            (num_filter_rows * row_height) + filter_padding

        # Set help content for this tab
        self._setup_help_content()

        self._setup_header()
        self._setup_results()
        self._setup_context_area()  # New method for enhanced context area
        self._setup_footer()
        self._setup_context_menu()

    def _setup_help_content(self):
        """Set up help content specific to Connector Lookup"""
        help_html = """
        <h2>Connector Lookup - Help & Navigation</h2>
        
        <h3>🔍 Search & Filters</h3>
        <ul>
            <li><b>Text Search:</b> Enter part code, number, alias, or property in the search box</li>
            <li><b>Multi-term Search:</b> Separate multiple search terms with commas (e.g., "D38999, VG95234")</li>
            <li><b>Advanced Filters:</b> Click "▶ Advanced Search" to show/hide filter options</li>
            <li><b>Standard Filter:</b> Selecting standards dynamically updates other filter options</li>
        </ul>
        
        <h3>⌨️ Keyboard Shortcuts</h3>
        <table style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #2D2D30;">
                <td style="padding: 8px; border: 1px solid #3F3F46;"><b>Shortcut</b></td>
                <td style="padding: 8px; border: 1px solid #3F3F46;"><b>Action</b></td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #3F3F46;"><b>Enter</b></td>
                <td style="padding: 8px; border: 1px solid #3F3F46;">Execute search</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #3F3F46;"><b>Ctrl + Click</b></td>
                <td style="padding: 8px; border: 1px solid #3F3F46;">Select/deselect multiple rows</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #3F3F46;"><b>Shift + Click</b></td>
                <td style="padding: 8px; border: 1px solid #3F3F46;">Select range of rows</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #3F3F46;"><b>Ctrl + A</b></td>
                <td style="padding: 8px; border: 1px solid #3F3F46;">Select all filter items (in multiselect)</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #3F3F46;"><b>Double-Click</b></td>
                <td style="padding: 8px; border: 1px solid #3F3F46;">Select only that item (deselect others in filter)</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #3F3F46;"><b>↑ ↓ Arrows</b></td>
                <td style="padding: 8px; border: 1px solid #3F3F46;">Navigate table rows</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #3F3F46;"><b>Shift + Arrows</b></td>
                <td style="padding: 8px; border: 1px solid #3F3F46;">Extend selection in table</td>
            </tr>
        </table>
        
        <h3>🖱️ Mouse Actions</h3>
        <ul>
            <li><b>Right-Click Row:</b> Context menu with actions (Copy Row, Find Alternative, Find Opposite, etc.)</li>
            <li><b>Double-Click Filter:</b> Select only that filter value (clears other selections)</li>
            <li><b>Ctrl + Click Filter:</b> Select all items in that filter</li>
            <li><b>Click Recent Search:</b> Restore previous search (moves to top of history)</li>
            <li><b>Right-Click Recent Search:</b> Delete from history</li>
        </ul>
        
        <h3>📋 Table Features</h3>
        <ul>
            <li><b>Multi-Row Selection:</b> Select multiple rows with Ctrl/Shift + Click</li>
            <li><b>Copy Rows:</b> Right-click → "Copy Row" copies all selected rows with headers (Excel-compatible)</li>
            <li><b>Sorting:</b> Click column headers to sort</li>
            <li><b>Column Visibility:</b> Some columns may be hidden by default</li>
        </ul>
        
        <h3>🔄 Smart Features</h3>
        <ul>
            <li><b>Smart Clear:</b> First click clears filters, second click clears text</li>
            <li><b>Search History:</b> Recent searches saved automatically (max 35, shows 15 before scrolling)</li>
            <li><b>Search Debouncing:</b> Rapid filter changes within 10 seconds update the same history entry</li>
            <li><b>Dynamic Filters:</b> Filter options update based on selected standards</li>
            <li><b>No Empty Searches:</b> Searches with 0 results are not saved to history</li>
        </ul>
        
        <h3>🔧 Context Menu Actions (Single Selection Only)</h3>
        <ul>
            <li><b>Find Alternative:</b> Search for alternative connectors with similar specifications</li>
            <li><b>Find Opposite:</b> Find mating connector (plug ↔ receptacle)</li>
            <li><b>View Details:</b> Show detailed connector information</li>
            <li><b>Copy Row:</b> Copy selected rows with headers to clipboard</li>
        </ul>
        
        <h3>📊 Context Panel</h3>
        <ul>
            <li><b>Connector Details:</b> Shows details of selected connector</li>
            <li><b>Pinout Image:</b> Displays connector pinout diagram (when available)</li>
            <li><b>Action Buttons:</b> "Find Alternative" and "Find Opposite" (enabled when 1 row selected)</li>
        </ul>
        
        <h3>💡 Tips</h3>
        <ul>
            <li>Hover over filter items to see full text in tooltip</li>
            <li>Use comma-separated searches to find multiple parts: "D38999, VG95234, MIL"</li>
            <li>Recent searches show first result's Part Number and Part Code</li>
            <li>Filters are synchronized - left and right columns scroll together</li>
            <li>Search history persists during session (resets on restart)</li>
        </ul>
        """
        self.set_help_content(help_html)

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
            list_item = QListWidgetItem(item)
            # Add tooltip with the same text
            list_item.setToolTip(item)
            left_list.addItem(list_item)
            # Disable empty padding items
            if item == "":
                idx = left_list.count() - 1
                item_widget = left_list.item(idx)
                if item_widget:
                    # Make unselectable and invisible
                    item_widget.setFlags(Qt.NoItemFlags)
                    item_widget.setToolTip("")  # No tooltip for empty items
        left_list.setStyleSheet(left_style)
        left_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left_list.setContentsMargins(0, 0, 0, 0)

        # Create right list
        right_list = QListWidget()
        right_list.setSelectionMode(QListWidget.MultiSelection)
        for item in right_items:
            list_item = QListWidgetItem(item)
            # Add tooltip with the same text
            list_item.setToolTip(item)
            right_list.addItem(list_item)
            # Disable empty padding items
            if item == "":
                idx = right_list.count() - 1
                item_widget = right_list.item(idx)
                if item_widget:
                    # Make unselectable and invisible
                    item_widget.setFlags(Qt.NoItemFlags)
                    item_widget.setToolTip("")  # No tooltip for empty items
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
        label = StandardLabel(label_text, style=TextStyle.LABEL)

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

        title_label = StandardLabel("Connector Lookup", style=TextStyle.TITLE)

        title_row.addWidget(title_label)
        title_row.addStretch()
        title_row.addWidget(self.help_label)  # Add help button from base class

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
            "part code, number, alias or property (comma-separated for multiple)")
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

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setMinimumHeight(30)
        self.reset_btn.setToolTip(
            "Reset tab to initial state (clear all filters, search text, and results)")

        search_container_layout.addWidget(
            self.search_input, 3)  # Give search input more space
        search_container_layout.addWidget(self.search_btn)
        # search_container_layout.addWidget(self.refresh_btn)
        # search_container_layout.addWidget(self.export_btn)
        search_container_layout.addWidget(self.clear_btn)
        search_container_layout.addWidget(self.reset_btn)

        # Set size policy to limit width (similar to SearchEpdView)
        search_container.setMaximumWidth(int(self.header_frame.width() * 0.7))

        search_controls_layout.addWidget(search_container)
        search_controls_layout.addStretch()

        header_layout.addLayout(search_controls_layout)

        # Connect signals
        self.search_btn.clicked.connect(self._on_search_clicked)
        self.clear_btn.clicked.connect(self._on_clear_clicked)
        self.reset_btn.clicked.connect(self._on_reset_clicked)

        # === Advanced Search Toggle ===
        advanced_search_row = QHBoxLayout()
        advanced_search_row.setContentsMargins(
            0, 15, 0, 0)  # No bottom spacing

        # Advanced search toggle label - keeping QLabel for custom hover behavior
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

        # Row 0: Material
        material_container, self.material_list_left, self.material_list_right = self._create_labeled_filter(
            "Material:", MATERIALS)

        # Row 1: Shell Size
        shell_size_container, self.shell_size_list_left, self.shell_size_list_right = self._create_labeled_filter(
            "Shell Size:", SHELL_SIZES)

        # === Column 3 ===

        # Row 0: Insert Arrangement
        insert_arrangement_container, self.insert_arrangement_list_left, self.insert_arrangement_list_right = self._create_labeled_filter(
            "Insert Arrangement:", INSERT_ARRANGEMENTS)

        # Row 1: Socket Type
        socket_type_container, self.socket_type_list_left, self.socket_type_list_right = self._create_labeled_filter(
            "Socket Type:", SOCKET_TYPES)

        # === Column 4 ===

        # Row 0: Keying
        keying_container, self.keying_list_left, self.keying_list_right = self._create_labeled_filter(
            "Keying:", KEYINGS)

        # Add to grid in 4 columns, 2 rows
        filter_layout.addWidget(standard_container, 0, 0)
        filter_layout.addWidget(shell_type_container, 1, 0)
        filter_layout.addWidget(material_container, 0, 1)
        filter_layout.addWidget(shell_size_container, 1, 1)
        filter_layout.addWidget(insert_arrangement_container, 0, 2)
        filter_layout.addWidget(socket_type_container, 1, 2)
        filter_layout.addWidget(keying_container, 0, 3)

        # Add stretch column
        filter_layout.setColumnStretch(4, 1)

        header_layout.addWidget(self.filter_container)

        # Connect filter change signals
        self._connect_filter_signals()

    def _connect_filter_signals(self):
        """Connect all filter multiselect signals to trigger search"""
        # Standard filter has special handling - it updates other filters
        self.standard_list_left.itemSelectionChanged.connect(
            self._on_standard_filter_changed)
        self.standard_list_right.itemSelectionChanged.connect(
            self._on_standard_filter_changed)

        # All other filters trigger normal search
        self.shell_type_list_left.itemSelectionChanged.connect(
            self._on_filter_changed)
        self.shell_type_list_right.itemSelectionChanged.connect(
            self._on_filter_changed)

        self.material_list_left.itemSelectionChanged.connect(
            self._on_filter_changed)
        self.material_list_right.itemSelectionChanged.connect(
            self._on_filter_changed)

        self.shell_size_list_left.itemSelectionChanged.connect(
            self._on_filter_changed)
        self.shell_size_list_right.itemSelectionChanged.connect(
            self._on_filter_changed)

        self.insert_arrangement_list_left.itemSelectionChanged.connect(
            self._on_filter_changed)
        self.insert_arrangement_list_right.itemSelectionChanged.connect(
            self._on_filter_changed)

        self.socket_type_list_left.itemSelectionChanged.connect(
            self._on_filter_changed)
        self.socket_type_list_right.itemSelectionChanged.connect(
            self._on_filter_changed)

        self.keying_list_left.itemSelectionChanged.connect(
            self._on_filter_changed)
        self.keying_list_right.itemSelectionChanged.connect(
            self._on_filter_changed)

    def _on_standard_filter_changed(self):
        """Handle standard filter change - updates other filter options and triggers search"""
        # Get selected standards
        selected_standards = [item.text() for item in self.standard_list_left.selectedItems()] + \
            [item.text() for item in self.standard_list_right.selectedItems()]

        # Emit signal to request updated filter options
        self.standards_changed.emit(selected_standards)

        # Also trigger search with current filters
        filters = self._get_selected_filters()
        self.search_requested.emit(filters)

    def _on_filter_changed(self):
        """Handle any filter selection change - trigger search"""
        filters = self._get_selected_filters()
        self.search_requested.emit(filters)

    def _setup_results(self):
        """Setup results table"""
        # Create table in the left content area
        results_layout = QVBoxLayout(self.left_content_frame)
        results_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableView()
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        # Allow multiple selection with Shift/Ctrl
        self.table.setSelectionMode(QTableView.ExtendedSelection)
        self.table.setAlternatingRowColors(True)

        results_layout.addWidget(self.table)

        # Set custom text for the inherited record_count_label
        self.record_count_label.setText("Showing only results from database")

    def _setup_context_area(self):
        """Setup enhanced context area with image and buttons"""
        # The context_box is inherited from BaseTabView
        # We'll replace its layout to include image and buttons

        # Get the context frame from base class
        context_frame = self.context_box.parent()
        context_layout = context_frame.layout()

        # Remove the existing context_box temporarily
        context_layout.removeWidget(self.context_box)

        # Create new container for context content
        context_container = QWidget()
        context_container_layout = QVBoxLayout(context_container)
        context_container_layout.setContentsMargins(5, 5, 5, 5)
        context_container_layout.setSpacing(5)

        # Create horizontal layout for text and image
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)

        # Left side: Context text
        if not ENABLE_PINOUT_IMAGE:
            # If image disabled, let context box take full width
            self.context_box.setMinimumWidth(0)
        else:
            # If image enabled, set minimum width for text area
            self.context_box.setMinimumWidth(200)
        content_layout.addWidget(self.context_box, 1)  # Stretch factor 1

        # Right side: Image placeholder for connector pinout (only if enabled)
        if ENABLE_PINOUT_IMAGE:
            # Pinout image container - keeping QLabel for image display with custom border
            self.pinout_image_label = QLabel("No Image")
            self.pinout_image_label.setAlignment(Qt.AlignCenter)
            self.pinout_image_label.setFixedSize(200, 200)
            self.pinout_image_label.setStyleSheet(f"""
                QLabel {{
                    border: 2px dashed {UI_COLORS['frame_border']};
                    background-color: {UI_COLORS['section_background']};
                    color: {UI_COLORS['muted_text']};
                    border-radius: 5px;
                }}
            """)
            self.pinout_image_label.setScaledContents(True)
            content_layout.addWidget(self.pinout_image_label)
        else:
            # Create placeholder attribute so code doesn't break if referenced elsewhere
            self.pinout_image_label = None

        context_container_layout.addLayout(
            content_layout, 1)  # Stretch factor 1

        # Button row below the text/image
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.find_alternative_btn = QPushButton("Find Alternatives")
        self.find_alternative_btn.setMinimumHeight(30)
        self.find_alternative_btn.setEnabled(
            False)  # Disabled until one row selected
        self.find_alternative_btn.clicked.connect(
            self._on_find_alternative_button_clicked)
        self.find_alternative_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {UI_COLORS['section_highlight_primary']};
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {UI_COLORS['filter_pill_hover']};
            }}
            QPushButton:disabled {{
                background-color: {UI_COLORS['section_background']};
                color: {UI_COLORS['muted_text']};
            }}
        """)

        self.find_opposite_btn = QPushButton("Find Opposite")
        self.find_opposite_btn.setMinimumHeight(30)
        # Disabled until one row selected
        self.find_opposite_btn.setEnabled(False)
        self.find_opposite_btn.clicked.connect(
            self._on_find_opposite_button_clicked)
        self.find_opposite_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {UI_COLORS['section_highlight_primary']};
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {UI_COLORS['filter_pill_hover']};
            }}
            QPushButton:disabled {{
                background-color: {UI_COLORS['section_background']};
                color: {UI_COLORS['muted_text']};
            }}
        """)

        button_layout.addWidget(self.find_alternative_btn)
        button_layout.addWidget(self.find_opposite_btn)
        button_layout.addStretch()

        context_container_layout.addLayout(button_layout)

        # Add the new container back to the context layout
        context_layout.addWidget(context_container, 1)

    def _setup_footer(self):
        """Setup footer with recent searches dropdown"""
        # Clear the default footer_box and replace with custom layout
        # The footer_box is inherited from BaseTabView

        # Create a horizontal layout for the footer
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(5, 5, 5, 5)
        footer_layout.setSpacing(10)

        # Recent searches label and dropdown
        recent_label = StandardLabel("Recent Searches:", style=TextStyle.LABEL)

        self.recent_searches_combo = QComboBox()
        self.recent_searches_combo.setPlaceholderText(
            "Select a recent search...")
        self.recent_searches_combo.setMinimumWidth(400)
        self.recent_searches_combo.setMaximumWidth(800)
        self.recent_searches_combo.setMaxVisibleItems(
            15)  # Scroll after 15 items
        self.recent_searches_combo.currentTextChanged.connect(
            self._on_recent_search_selected)
        self.recent_searches_combo.setContextMenuPolicy(Qt.CustomContextMenu)
        self.recent_searches_combo.customContextMenuRequested.connect(
            self._show_history_context_menu)

        # Use size adjust policy to expand dropdown to content
        from PySide6.QtWidgets import QComboBox as QCB
        self.recent_searches_combo.setSizeAdjustPolicy(QCB.AdjustToContents)

        self.recent_searches_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {UI_COLORS['section_background']};
                color: {UI_COLORS['highlight_text']};
                border: 1px solid {UI_COLORS['frame_border']};
                border-radius: 3px;
                padding: 3px 5px;
                min-height: 20px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {UI_COLORS['highlight_text']};
                margin-right: 5px;
            }}
            QComboBox QAbstractItemView {{
                min-width: 600px;
                background-color: {UI_COLORS['section_background']};
                color: {UI_COLORS['highlight_text']};
                selection-background-color: {UI_COLORS['section_highlight_primary']};
                border: 1px solid {UI_COLORS['frame_border']};
            }}
        """)

        # Replace footer_box content with layout
        # Clear existing layout if any
        if self.footer_box.layout():
            QWidget().setLayout(self.footer_box.layout())

        footer_layout.addWidget(recent_label)
        footer_layout.addWidget(self.recent_searches_combo)
        footer_layout.addStretch()

        self.footer_box.setLayout(footer_layout)

    def _setup_context_menu(self):
        """Setup right-click context menu for table"""
        self.setup_table_context_menu(
            self.table,
            actions=[
                ("View Details", self._on_view_details_context),
                ("Find Alternatives", self._on_find_alternative_context),
                ("Find Opposite", self._on_find_opposite_context),
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
        """Emit search signal with selected filters and close modification window"""
        # Close modification window for most recent search
        self._close_modification_window()

        filters = self._get_selected_filters()
        self.search_requested.emit(filters)

    def add_search_to_history(self, filters: dict, result_count: int, first_result: dict = None):
        """Add completed search to history with result count and first result info

        Args:
            filters: The filters used in the search
            result_count: Number of results returned
            first_result: Dictionary containing first result's Part Number and Part Code
        """
        # Don't add to history if we're restoring from history
        if self._is_restoring_search:
            self._is_restoring_search = False
            return

        self._add_to_recent_searches(filters, result_count, first_result)

    def _on_clear_clicked(self):
        """Smart clear: Clear filters first, then text if no filters active"""
        # Close modification window for most recent search
        self._close_modification_window()

        # Check if any filters are active
        has_active_filters = self._has_active_filters()

        if has_active_filters:
            # Clear only the multiselect filters, keep search text
            self.standard_list_left.clearSelection()
            self.standard_list_right.clearSelection()
            self.shell_type_list_left.clearSelection()
            self.shell_type_list_right.clearSelection()
            self.material_list_left.clearSelection()
            self.material_list_right.clearSelection()
            self.shell_size_list_left.clearSelection()
            self.shell_size_list_right.clearSelection()
            self.insert_arrangement_list_left.clearSelection()
            self.insert_arrangement_list_right.clearSelection()
            self.socket_type_list_left.clearSelection()
            self.socket_type_list_right.clearSelection()
            self.keying_list_left.clearSelection()
            self.keying_list_right.clearSelection()
            self.clear_filters_requested.emit()
        else:
            # No filters active, clear the search text
            self.search_input.clear()
            self.clear_filters_requested.emit()

    def _has_active_filters(self) -> bool:
        """Check if any multiselect filters have selections"""
        return bool(
            self.standard_list_left.selectedItems() or
            self.standard_list_right.selectedItems() or
            self.shell_type_list_left.selectedItems() or
            self.shell_type_list_right.selectedItems() or
            self.material_list_left.selectedItems() or
            self.material_list_right.selectedItems() or
            self.shell_size_list_left.selectedItems() or
            self.shell_size_list_right.selectedItems() or
            self.insert_arrangement_list_left.selectedItems() or
            self.insert_arrangement_list_right.selectedItems() or
            self.socket_type_list_left.selectedItems() or
            self.socket_type_list_right.selectedItems() or
            self.keying_list_left.selectedItems() or
            self.keying_list_right.selectedItems()
        )

    def _on_reset_clicked(self):
        """Reset the tab to initial state - clear all filters, search text, results, and history"""
        # Close modification window
        self._close_modification_window()

        # Clear search input
        self.search_input.clear()

        # Clear all filter selections
        self.standard_list_left.clearSelection()
        self.standard_list_right.clearSelection()
        self.shell_type_list_left.clearSelection()
        self.shell_type_list_right.clearSelection()
        self.material_list_left.clearSelection()
        self.material_list_right.clearSelection()
        self.shell_size_list_left.clearSelection()
        self.shell_size_list_right.clearSelection()
        self.insert_arrangement_list_left.clearSelection()
        self.insert_arrangement_list_right.clearSelection()
        self.socket_type_list_left.clearSelection()
        self.socket_type_list_right.clearSelection()
        self.keying_list_left.clearSelection()
        self.keying_list_right.clearSelection()

        # Clear recent searches history
        self.recent_searches.clear()
        self.recent_searches_data.clear()
        self.recent_searches_timestamps.clear()
        self.recent_searches_results.clear()
        self._update_recent_searches_combo()

        # Clear context display
        self.context_box.clear()

        # Emit reset signal to presenter to clear table
        self.reset_requested.emit()

    def _add_to_recent_searches(self, filters: dict, result_count: int, first_result: dict = None):
        """Add search to recent searches history with debouncing

        Args:
            filters: The filter dict from the search
            result_count: Number of results found
            first_result: Dictionary containing first result's Part Number and Part Code
        """
        # Don't save searches with no results
        if result_count == 0:
            return

        # Don't save if no filters or text are set (empty search)
        has_text = bool(filters.get('search_text', '').strip())
        has_filters = bool(
            filters.get('standard') or
            filters.get('shell_type') or
            filters.get('material') or
            filters.get('shell_size') or
            filters.get('insert_arrangement') or
            filters.get('socket_type') or
            filters.get('keying')
        )
        if not has_text and not has_filters:
            return

        current_time = datetime.now()

        # Check if we should UPDATE the most recent search (within 10 seconds and open for modification)
        should_update_recent = False
        if (self._most_recent_search_open_for_modification and
            self._most_recent_search_timestamp and
                len(self.recent_searches) > 0):
            time_diff = current_time - self._most_recent_search_timestamp
            if time_diff < timedelta(seconds=10):
                should_update_recent = True

        # Create a human-readable description of the search
        # Check if this is a special action (Find Alternative/Opposite)
        is_special_action = filters.get('_special_action') in [
            'find_alternative', 'find_opposite']

        if is_special_action:
            # For special actions, use the search_text directly (e.g., "Alternative to ABC123")
            search_type = filters.get('search_text', 'Unknown Action')
        else:
            # Normal search - build description from filters
            # NOTE: Exclude 'standard' (Family) from the summary as requested
            advanced_filter_parts = []
            # if filters.get('standard'):  # EXCLUDED from summary
            #     advanced_filter_parts.extend(filters['standard'])
            if filters.get('shell_type'):
                advanced_filter_parts.extend(filters['shell_type'])
            if filters.get('material'):
                advanced_filter_parts.extend(filters['material'])
            if filters.get('shell_size'):
                advanced_filter_parts.extend(filters['shell_size'])
            if filters.get('insert_arrangement'):
                advanced_filter_parts.extend(filters['insert_arrangement'])
            if filters.get('socket_type'):
                advanced_filter_parts.extend(filters['socket_type'])
            if filters.get('keying'):
                advanced_filter_parts.extend(filters['keying'])

            # Build search description
            if advanced_filter_parts:
                # For advanced search: show comma-separated filter values
                search_type = ", ".join(advanced_filter_parts)
                # Add search text if present
                if filters.get('search_text'):
                    search_type = f"{filters['search_text']} + {search_type}"
            else:
                # For simple text search: just show the search text
                search_type = filters.get('search_text', 'All Results')

        # Add first result info if available
        result_info = ""
        if first_result and result_count > 0:
            part_num = first_result.get('Part Number', '')
            part_code = first_result.get('Part Code', '')
            if part_num or part_code:
                result_info = f" | {part_num} - {part_code}" if part_num and part_code else f" | {part_num or part_code}"

        # Format: "D38999, Aluminum (25 results) | PART123 - ABC"
        search_description = f"{search_type} ({result_count} result{'s' if result_count != 1 else ''}){result_info}"

        if should_update_recent:
            # UPDATE the most recent search instead of adding new one
            # Get the first (most recent) item
            most_recent_key = self.recent_searches[0]

            # Remove old entry from all tracking structures
            self.recent_searches.remove(most_recent_key)
            if most_recent_key in self.recent_searches_data:
                del self.recent_searches_data[most_recent_key]
            if most_recent_key in self.recent_searches_timestamps:
                del self.recent_searches_timestamps[most_recent_key]
            if most_recent_key in self.recent_searches_results:
                del self.recent_searches_results[most_recent_key]
        else:
            # Not updating - this is a new search, so remove duplicate if it exists
            if search_description in self.recent_searches:
                self.recent_searches.remove(search_description)

        # Store the filters data, timestamp, and first result for this search
        self.recent_searches_data[search_description] = filters.copy()
        self.recent_searches_timestamps[search_description] = current_time
        if first_result:
            self.recent_searches_results[search_description] = first_result.copy(
            )

        # Add to front of deque
        self.recent_searches.appendleft(search_description)

        # Mark this search as open for modification
        self._most_recent_search_open_for_modification = True
        self._most_recent_search_timestamp = current_time

        # Update combo box
        self._update_recent_searches_combo()

    def _update_recent_searches_combo(self):
        """Update the recent searches combo box"""
        self.recent_searches_combo.blockSignals(True)
        self.recent_searches_combo.clear()
        self.recent_searches_combo.addItems(list(self.recent_searches))
        self.recent_searches_combo.setCurrentIndex(-1)  # No selection
        self.recent_searches_combo.blockSignals(False)

    def _on_recent_search_selected(self, search_text: str):
        """Handle selection of a recent search - restore that search and move to top"""
        if not search_text or search_text not in self.recent_searches_data:
            return

        # Pop this search from the list and re-add to top
        if search_text in self.recent_searches:
            # Get the data before removing
            filters = self.recent_searches_data[search_text].copy()
            timestamp = self.recent_searches_timestamps.get(search_text)
            first_result = self.recent_searches_results.get(search_text, {}).copy(
            ) if search_text in self.recent_searches_results else None

            # Remove from current position
            self.recent_searches.remove(search_text)

            # Re-add to top (front of deque)
            self.recent_searches.appendleft(search_text)

            # Update combo box to reflect new order
            self._update_recent_searches_combo()

        # Get the stored filters for this search
        filters = self.recent_searches_data[search_text]

        # Check if this is a special action (Find Alternative/Opposite)
        special_action = filters.get('_special_action')
        if special_action in ['find_alternative', 'find_opposite']:
            # Extract the part code from the search text
            # Format is "Alternative to {Part Code}" or "Opposite to {Part Code}"
            search_text_value = filters.get('search_text', '')
            if 'Alternative to ' in search_text_value:
                part_code = search_text_value.replace(
                    'Alternative to ', '').strip()
                # Emit the find alternative signal
                self.find_alternative_requested.emit(part_code)
            elif 'Opposite to ' in search_text_value:
                part_code = search_text_value.replace(
                    'Opposite to ', '').strip()
                # Emit the find opposite signal
                self.find_opposite_requested.emit(part_code)

            # Reset combo box to placeholder
            self.recent_searches_combo.setCurrentIndex(-1)
            return

        # Normal search - restore filters and execute
        # Clear current state first
        self._clear_all_selections()

        # Restore search text
        if filters.get('search_text'):
            self.search_input.setText(filters['search_text'])

        # Restore multiselect filters
        self._restore_multiselect_selections(
            self.standard_list_left, self.standard_list_right,
            filters.get('standard', [])
        )
        self._restore_multiselect_selections(
            self.shell_type_list_left, self.shell_type_list_right,
            filters.get('shell_type', [])
        )
        self._restore_multiselect_selections(
            self.material_list_left, self.material_list_right,
            filters.get('material', [])
        )
        self._restore_multiselect_selections(
            self.shell_size_list_left, self.shell_size_list_right,
            filters.get('shell_size', [])
        )
        self._restore_multiselect_selections(
            self.insert_arrangement_list_left, self.insert_arrangement_list_right,
            filters.get('insert_arrangement', [])
        )
        self._restore_multiselect_selections(
            self.socket_type_list_left, self.socket_type_list_right,
            filters.get('socket_type', [])
        )
        self._restore_multiselect_selections(
            self.keying_list_left, self.keying_list_right,
            filters.get('keying', [])
        )

        # Trigger the search (this will NOT add to history or reorder since we're restoring)
        # We'll use a flag to prevent re-adding to history
        self._is_restoring_search = True
        self.search_requested.emit(filters)

        # Reset combo box to placeholder
        self.recent_searches_combo.setCurrentIndex(-1)

    def _clear_all_selections(self):
        """Clear all filter selections and search text"""
        self.search_input.clear()
        self.standard_list_left.clearSelection()
        self.standard_list_right.clearSelection()
        self.shell_type_list_left.clearSelection()
        self.shell_type_list_right.clearSelection()
        self.material_list_left.clearSelection()
        self.material_list_right.clearSelection()
        self.shell_size_list_left.clearSelection()
        self.shell_size_list_right.clearSelection()
        self.insert_arrangement_list_left.clearSelection()
        self.insert_arrangement_list_right.clearSelection()
        self.socket_type_list_left.clearSelection()
        self.socket_type_list_right.clearSelection()
        self.keying_list_left.clearSelection()
        self.keying_list_right.clearSelection()

    def _restore_multiselect_selections(self, left_list, right_list, selected_values: list):
        """Restore selections in a dual-column multiselect

        Args:
            left_list: Left QListWidget
            right_list: Right QListWidget
            selected_values: List of values to select
        """
        if not selected_values:
            return

        # Block signals to prevent triggering filter changes during restore
        left_list.blockSignals(True)
        right_list.blockSignals(True)

        # Select items in left list
        for i in range(left_list.count()):
            item = left_list.item(i)
            if item and item.text() in selected_values:
                item.setSelected(True)

        # Select items in right list
        for i in range(right_list.count()):
            item = right_list.item(i)
            if item and item.text() in selected_values:
                item.setSelected(True)

        # Re-enable signals
        left_list.blockSignals(False)
        right_list.blockSignals(False)

    def _get_selected_filters(self) -> dict:
        """Get currently selected filter values from dual-column lists"""
        return {
            'search_text': self.search_input.text().strip(),
            'standard': [item.text() for item in self.standard_list_left.selectedItems()] +
            [item.text() for item in self.standard_list_right.selectedItems()],
            'shell_type': [item.text() for item in self.shell_type_list_left.selectedItems()] +
            [item.text() for item in self.shell_type_list_right.selectedItems()],
            'material': [item.text() for item in self.material_list_left.selectedItems()] +
            [item.text() for item in self.material_list_right.selectedItems()],
            'shell_size': [item.text() for item in self.shell_size_list_left.selectedItems()] +
            [item.text() for item in self.shell_size_list_right.selectedItems()],
            'insert_arrangement': [item.text() for item in self.insert_arrangement_list_left.selectedItems()] +
            [item.text()
             for item in self.insert_arrangement_list_right.selectedItems()],
            'socket_type': [item.text() for item in self.socket_type_list_left.selectedItems()] +
            [item.text() for item in self.socket_type_list_right.selectedItems()],
            'keying': [item.text() for item in self.keying_list_left.selectedItems()] +
            [item.text() for item in self.keying_list_right.selectedItems()]
        }

    def update_filter_options(self, filter_options: dict):
        """Update available options in filter multiselects based on selected standards

        Args:
            filter_options: Dict with keys shell_types, materials, shell_sizes, 
                          insert_arrangements, socket_types, keyings
        """
        # Update each filter while preserving current selections
        self._update_multiselect_options(
            self.shell_type_list_left,
            self.shell_type_list_right,
            filter_options.get('shell_types', [])
        )

        self._update_multiselect_options(
            self.material_list_left,
            self.material_list_right,
            filter_options.get('materials', [])
        )

        self._update_multiselect_options(
            self.shell_size_list_left,
            self.shell_size_list_right,
            filter_options.get('shell_sizes', [])
        )

        self._update_multiselect_options(
            self.insert_arrangement_list_left,
            self.insert_arrangement_list_right,
            filter_options.get('insert_arrangements', [])
        )

        self._update_multiselect_options(
            self.socket_type_list_left,
            self.socket_type_list_right,
            filter_options.get('socket_types', [])
        )

        self._update_multiselect_options(
            self.keying_list_left,
            self.keying_list_right,
            filter_options.get('keyings', [])
        )

    def _update_multiselect_options(self, left_list, right_list, new_items: list):
        """Update a dual-column multiselect with new items while preserving selections

        Args:
            left_list: Left QListWidget
            right_list: Right QListWidget
            new_items: New list of items to display
        """
        # Store currently selected items
        selected_items = set()
        for item in left_list.selectedItems():
            selected_items.add(item.text())
        for item in right_list.selectedItems():
            selected_items.add(item.text())

        # Filter out any selected items that are no longer available
        selected_items = selected_items.intersection(set(new_items))

        # Temporarily disconnect signals to avoid triggering filter changes
        left_list.blockSignals(True)
        right_list.blockSignals(True)

        # Clear both lists
        left_list.clear()
        right_list.clear()

        # If no items available, show "No options" message
        if not new_items:
            left_list.addItem("No options")
            no_options_item = left_list.item(0)
            if no_options_item:
                # Make it non-selectable
                no_options_item.setFlags(Qt.NoItemFlags)
                # Style it as disabled/muted text
                no_options_item.setForeground(Qt.gray)

            # Re-enable signals and return early
            left_list.blockSignals(False)
            right_list.blockSignals(False)
            return

        # Split items into two columns
        mid_point = (len(new_items) + 1) // 2
        left_items = new_items[:mid_point]
        right_items = new_items[mid_point:]

        # Add padding for odd numbers
        if len(new_items) % 2 == 1:
            left_items = left_items + ["", ""]
            right_items = right_items + [""]

        # Populate left list
        for item in left_items:
            left_list.addItem(item)
            if item == "":
                idx = left_list.count() - 1
                item_widget = left_list.item(idx)
                if item_widget:
                    item_widget.setFlags(Qt.NoItemFlags)
            elif item in selected_items:
                left_list.item(left_list.count() - 1).setSelected(True)

        # Populate right list
        for item in right_items:
            right_list.addItem(item)
            if item == "":
                idx = right_list.count() - 1
                item_widget = right_list.item(idx)
                if item_widget:
                    item_widget.setFlags(Qt.NoItemFlags)
            elif item in selected_items:
                right_list.item(right_list.count() - 1).setSelected(True)

        # Re-enable signals
        left_list.blockSignals(False)
        right_list.blockSignals(False)

    def _on_view_details_context(self, index, row, column):
        """Handle view details action from context menu"""
        # Close modification window when using context menu
        self._close_modification_window()

        print(f"View details for row {row}, column {column}")
        # To be implemented

    def _on_find_alternative_context(self, index, row, column):
        """Handle find alternative action from context menu"""
        # Close modification window when using context menu
        self._close_modification_window()

        # Only allow if exactly one row is selected
        selected_rows = self.table.selectionModel().selectedRows()
        if len(selected_rows) != 1:
            print("Please select exactly one row to find alternative")
            return

        # Get the part code from the selected row
        part_code = self._get_part_code_from_row(selected_rows[0].row())
        if part_code:
            print(f"Finding alternative for part code: {part_code}")
            self.find_alternative_requested.emit(part_code)

    def _on_find_opposite_context(self, index, row, column):
        """Handle find opposite action from context menu"""
        # Close modification window when using context menu
        self._close_modification_window()

        # Only allow if exactly one row is selected
        selected_rows = self.table.selectionModel().selectedRows()
        if len(selected_rows) != 1:
            print("Please select exactly one row to find opposite")
            return

        # Get the part code from the selected row
        part_code = self._get_part_code_from_row(selected_rows[0].row())
        if part_code:
            print(f"Finding opposite for part code: {part_code}")
            self.find_opposite_requested.emit(part_code)

    def _on_find_alternative_button_clicked(self):
        """Handle Find Alternative button click"""
        selected_rows = self.table.selectionModel().selectedRows()
        if len(selected_rows) == 1:
            part_code = self._get_part_code_from_row(selected_rows[0].row())
            if part_code:
                print(f"Finding alternative for part code: {part_code}")
                self.find_alternative_requested.emit(part_code)
                self._close_modification_window()

    def _on_find_opposite_button_clicked(self):
        """Handle Find Opposite button click"""
        selected_rows = self.table.selectionModel().selectedRows()
        if len(selected_rows) == 1:
            part_code = self._get_part_code_from_row(selected_rows[0].row())
            if part_code:
                print(f"Finding opposite for part code: {part_code}")
                self.find_opposite_requested.emit(part_code)
                self._close_modification_window()

    def _get_part_code_from_row(self, row: int) -> str:
        """Get the Part Code from a specific row

        Args:
            row: Row index in the table

        Returns:
            Part Code string or empty string if not found
        """
        if not hasattr(self, 'table') or not self.table.model():
            return ""

        model = self.table.model()

        # Find the Part Code column
        source_model = model.sourceModel() if hasattr(model, 'sourceModel') else model
        if hasattr(source_model, '_data'):
            df = source_model._data
            if 'Part Code' in df.columns:
                # Get the actual row from the source model (in case of sorting/filtering)
                if hasattr(model, 'mapToSource'):
                    source_index = model.mapToSource(model.index(row, 0))
                    actual_row = source_index.row()
                else:
                    actual_row = row

                if actual_row < len(df):
                    return str(df.iloc[actual_row]['Part Code'])

        return ""

    def update_context_buttons_state(self):
        """Enable/disable Find Alternative and Find Opposite buttons based on selection"""
        selected_rows = self.table.selectionModel(
        ).selectedRows() if self.table.selectionModel() else []
        exactly_one_selected = len(selected_rows) == 1

        self.find_alternative_btn.setEnabled(exactly_one_selected)
        self.find_opposite_btn.setEnabled(exactly_one_selected)

    def _on_view_details(self, index, row, column):
        """Handle view details action - DEPRECATED, use _on_view_details_context"""
        print(f"View details for row {row}, column {column}")
        # To be implemented

    def _on_find_alternative(self, index, row, column):
        """Handle find alternative action - DEPRECATED, use _on_find_alternative_context"""
        print(f"Find alternative for row {row}")
        # To be implemented

    def _on_find_opposite(self, index, row, column):
        """Handle find opposite action - DEPRECATED, use _on_find_opposite_context"""
        print(f"Find opposite for row {row}")
        # To be implemented

    def _on_export_selection(self, index, row, column):
        """Handle export selection action"""
        print(f"Export selection for row {row}")
        # To be implemented

    def _show_history_context_menu(self, position):
        """Show context menu for recent searches dropdown"""
        # Get the item at the current index
        current_index = self.recent_searches_combo.currentIndex()
        if current_index < 0:
            return

        search_text = self.recent_searches_combo.itemText(current_index)
        if not search_text:
            return

        # Create context menu
        menu = QMenu(self)
        delete_action = menu.addAction("Delete from History")

        # Show menu at cursor position
        action = menu.exec_(QCursor.pos())

        if action == delete_action:
            self._delete_from_history(search_text)

    def _delete_from_history(self, search_text: str):
        """Delete a specific search from history

        Args:
            search_text: The search description to delete
        """
        if search_text in self.recent_searches:
            # Remove from deque
            self.recent_searches.remove(search_text)

            # Remove from data dictionaries
            if search_text in self.recent_searches_data:
                del self.recent_searches_data[search_text]
            if search_text in self.recent_searches_timestamps:
                del self.recent_searches_timestamps[search_text]
            if search_text in self.recent_searches_results:
                del self.recent_searches_results[search_text]

            # Update combo box
            self._update_recent_searches_combo()

    def _close_modification_window(self):
        """Close the modification window for the most recent search"""
        self._most_recent_search_open_for_modification = False

    def _on_view_details(self, index, row, column):
        """Handle view details action"""
        # Close modification window when using context menu
        self._close_modification_window()

        print(f"View details for row {row}, column {column}")
        # To be implemented

    def _on_find_alternative(self, index, row, column):
        """Handle find alternative action"""
        # Close modification window when using context menu
        self._close_modification_window()

        print(f"Find alternative for row {row}")
        # To be implemented

    def _on_find_opposite(self, index, row, column):
        """Handle find opposite action"""
        # Close modification window when using context menu
        self._close_modification_window()

        print(f"Find opposite for row {row}")
        # To be implemented

    def _on_export_selection(self, index, row, column):
        """Handle export selection action"""
        # Close modification window when using context menu
        self._close_modification_window()

        print(f"Export selection for row {row}")
        # To be implemented

    def show_loading(self, visible: bool):
        """Show/hide loading indicator"""
        # To be implemented with loading overlay
        pass

    def update_loading_progress(self, percent: int, message: str):
        """Update loading progress"""
        self.record_count_label.setText(f"Loading: {percent}% - {message}")

    def show_error(self, error_message: str):
        """Display error message"""
        self.record_count_label.setText(f"Error: {error_message}")
        self.record_count_label.setStyleSheet(
            f"color: {UI_COLORS['danger_color']};")
