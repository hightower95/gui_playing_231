"""
EPD View - Electronic Parts Data analysis interface
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QTableView,
                               QTreeWidget, QTreeWidgetItem, QTableWidget,
                               QTableWidgetItem, QFrame, QLabel, QComboBox,
                               QPushButton, QGridLayout, QGroupBox, QSizePolicy)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox, QTableView
)
from PySide6.QtCore import Qt, Signal, QAbstractTableModel
from ..core.base_view import BaseView
# from ..core.app_context import AppContext
# from ..presenters.epd_presenter import EpdPresenter


class EpdView(QWidget):
    # Custom signal: emitted when user types in the search box
    searchTextChanged = Signal(str)
    minRatingChanged = Signal(int)
    maxAwgChanged = Signal(int)
    resetFiltersClicked = Signal(bool)

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)

        self.reset_button = QPushButton("Reset Filters")
        search_layout.addWidget(self.reset_button)

        # Numeric filters
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Min Rating (A):"))
        self.min_rating = QSpinBox()
        self.min_rating.setRange(0, 100)
        filter_layout.addWidget(self.min_rating)

        filter_layout.addWidget(QLabel("Max AWG:"))
        self.max_awg = QSpinBox()
        self.max_awg.setRange(0, 40)
        filter_layout.addWidget(self.max_awg)

        layout.addLayout(filter_layout)

        # Table
        self.table = QTableView()
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)

        self.setLayout(layout)

        # Connect signals
        self.search_box.textChanged.connect(self.searchTextChanged)
        self.min_rating.valueChanged.connect(self.minRatingChanged)
        self.max_awg.valueChanged.connect(self.maxAwgChanged)
        self.reset_button.clicked.connect(self.resetFiltersClicked)

    def set_table_model(self, model):
        """Attach a Qt model to the table view."""
        self.table.setModel(model)
        self.table.resizeColumnsToContents()


# class EpdView(BaseView):
#     def _setup_ui(self):
#         layout = QVBoxLayout()
#         layout.addWidget(QLabel("EPD Tool Placeholder"))
#         self.setLayout(layout)

# class EpdView(BaseView):
#     """EPD Analysis view with breakout wire and connection management"""

#     # Signals for user interactions
#     breakout_wire_selected = Signal(str)
#     connection_selected = Signal(str, str)  # breakout_wire, connection

#     def __init__(self, context: AppContext, parent=None):
#         self.presenter = EpdPresenter(context)
#         super().__init__(context, parent)

#     def _setup_ui(self):
#         """Setup the EPD analysis UI"""
#         layout = QHBoxLayout(self)
#         layout.setContentsMargins(10, 10, 10, 10)
#         layout.setSpacing(10)

#         # Create main splitter
#         splitter = QSplitter(Qt.Horizontal)
#         layout.addWidget(splitter)

#         # Left panel - Breakout Wire tree
#         self._create_left_panel(splitter)

#         # Right panel - Main content area
#         self._create_right_panel(splitter)

#         # Set splitter proportions
#         splitter.setSizes([200, 800])

#     def _create_left_panel(self, parent_splitter):
#         """Create the left panel with breakout wire tree"""
#         self.left_panel = QFrame()
#         self.left_panel.setFrameStyle(QFrame.Box)
#         self.left_panel.setMaximumWidth(250)
#         self.left_panel.setMinimumWidth(150)

#         layout = QVBoxLayout(self.left_panel)

#         # Title
#         title_label = QLabel("Breakout Wires")
#         title_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
#         layout.addWidget(title_label)

#         # Tree widget
#         self.breakout_tree = QTreeWidget()
#         self.breakout_tree.setHeaderHidden(True)
#         self.breakout_tree.itemClicked.connect(self._on_tree_item_clicked)
#         layout.addWidget(self.breakout_tree)

#         parent_splitter.addWidget(self.left_panel)

#         # Initialize tree with sample data
#         self._initialize_breakout_tree()

#     def _create_right_panel(self, parent_splitter):
#         """Create the right panel with main content"""
#         right_widget = QWidget()
#         right_layout = QVBoxLayout(right_widget)
#         right_layout.setSpacing(10)

#         # Top control panels
#         self._create_top_control_panels(right_layout)

#         # Tables panel
#         self._create_tables_panel(right_layout)

#         # Bottom control panel
#         self._create_bottom_panel(right_layout)

#         parent_splitter.addWidget(right_widget)

#     def _create_top_control_panels(self, parent_layout):
#         """Create top control panels"""
#         top_splitter = QSplitter(Qt.Horizontal)
#         parent_layout.addWidget(top_splitter, 1)

#         # Left control panel - Breakout Wire being reviewed
#         self.left_control = self._create_control_panel("Breakout Wire Being Reviewed")
#         top_splitter.addWidget(self.left_control)

#         # Right control panel - Connection being reviewed
#         self.right_control = self._create_control_panel("Connection Being Reviewed")
#         top_splitter.addWidget(self.right_control)

#     def _create_control_panel(self, title):
#         """Create a control panel with standard layout"""
#         panel = QFrame()
#         panel.setFrameStyle(QFrame.Box)

#         layout = QVBoxLayout(panel)

#         # Title
#         title_label = QLabel(title)
#         title_label.setStyleSheet("font-weight: bold; padding: 5px;")
#         title_label.setAlignment(Qt.AlignCenter)
#         layout.addWidget(title_label)

#         # Grid layout for controls
#         grid_layout = QGridLayout()

#         # Cable dropdown
#         cable_combo = QComboBox()
#         cable_combo.addItems(["Cable_A", "Cable_B", "Cable_C"])
#         grid_layout.addWidget(cable_combo, 0, 0)

#         # Jump to E3 button
#         jump_btn = QPushButton("Jump to E3")
#         grid_layout.addWidget(jump_btn, 0, 1)

#         # X1 and X2 labels
#         x1_label = QLabel("X1: Auto_Value_1")
#         x2_label = QLabel("X2: Auto_Value_2")
#         grid_layout.addWidget(x1_label, 1, 0)
#         grid_layout.addWidget(x2_label, 1, 1)

#         # Status label
#         status_label = QLabel("Status: Ready")
#         grid_layout.addWidget(status_label, 2, 0, 1, 2)

#         layout.addLayout(grid_layout)

#         return panel

#     def _create_tables_panel(self, parent_layout):
#         """Create the tables panel"""
#         tables_frame = QFrame()
#         tables_frame.setFrameStyle(QFrame.Box)
#         tables_layout = QHBoxLayout(tables_frame)

#         # Left table - Breakout Wire Pins
#         self.left_table = self._create_table("Breakout Wire Pins",
#                                            ["Pin", "Signal", "Type", "Status"])
#         tables_layout.addWidget(self.left_table)

#         # Middle table - Connection Pin Data
#         self.middle_table = self._create_table("Connection Pin Data",
#                                              ["Pin", "Connection", "Wire", "Notes"])
#         tables_layout.addWidget(self.middle_table)

#         # Right table - GYS Data (toggleable)
#         self.right_table = self._create_table("GYS Data",
#                                             ["ID", "Value", "Status", "Info"])
#         tables_layout.addWidget(self.right_table)

#         parent_layout.addWidget(tables_frame, 5)

#     def _create_table(self, title, headers):
#         """Create a table with title and headers"""
#         container = QWidget()
#         layout = QVBoxLayout(container)
#         layout.setContentsMargins(5, 5, 5, 5)

#         # Title
#         title_label = QLabel(title)
#         title_label.setAlignment(Qt.AlignCenter)
#         title_label.setStyleSheet("font-weight: bold; padding: 5px;")
#         layout.addWidget(title_label)

#         # Table
#         table = QTableWidget(20, len(headers))
#         table.setHorizontalHeaderLabels(headers)
#         table.horizontalHeader().setStretchLastSection(True)
#         table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
#         layout.addWidget(table)

#         return container

#     def _create_bottom_panel(self, parent_layout):
#         """Create bottom panel with recommendation sections"""
#         bottom_frame = QFrame()
#         bottom_frame.setFrameStyle(QFrame.Box)
#         bottom_layout = QHBoxLayout(bottom_frame)

#         sections = ["AWG", "Signals", "Pin Count", "Connectors"]

#         for section in sections:
#             group_box = QGroupBox(section)
#             group_layout = QVBoxLayout(group_box)

#             # Recommendation text
#             recommendation_label = QLabel(f"<Recommendation for {section}>")
#             recommendation_label.setWordWrap(True)
#             group_layout.addWidget(recommendation_label)

#             # Yes/No buttons
#             button_layout = QHBoxLayout()
#             yes_btn = QPushButton("✓ Yes")
#             yes_btn.setStyleSheet("background-color: lightgreen;")
#             no_btn = QPushButton("✗ No")
#             no_btn.setStyleSheet("background-color: lightcoral;")

#             button_layout.addWidget(yes_btn)
#             button_layout.addWidget(no_btn)
#             group_layout.addLayout(button_layout)

#             bottom_layout.addWidget(group_box)

#         # Save button section
#         save_container = QWidget()
#         save_layout = QVBoxLayout(save_container)

#         status_text = QLabel("Status:\nNo selections made")
#         status_text.setAlignment(Qt.AlignCenter)
#         save_layout.addWidget(status_text)

#         save_btn = QPushButton("Save Result")
#         save_btn.setStyleSheet("font-weight: bold; padding: 10px;")
#         save_layout.addWidget(save_btn)

#         bottom_layout.addWidget(save_container)

#         parent_layout.addWidget(bottom_frame, 2)

#     def _initialize_breakout_tree(self):
#         """Initialize the breakout wire tree with sample data"""
#         breakout_wires = ["BreakoutWire1", "BreakoutWire2", "BreakoutWire3",
#                          "BreakoutWire4", "BreakoutWire5"]

#         for breakout_wire in breakout_wires:
#             parent = QTreeWidgetItem(self.breakout_tree)
#             parent.setText(0, breakout_wire)
#             parent.setFlags(parent.flags() | Qt.ItemIsSelectable)

#             # Add connections
#             for i in range(1, 4):
#                 child = QTreeWidgetItem(parent)
#                 child.setText(0, f"Connection{i}")
#                 child.setFlags(child.flags() | Qt.ItemIsSelectable)

#     def _connect_signals(self):
#         """Connect signals to presenter"""
#         self.breakout_wire_selected.connect(self.presenter.handle_breakout_wire_selection)
#         self.connection_selected.connect(self.presenter.handle_connection_selection)

#     def _on_tree_item_clicked(self, item, column):
#         """Handle tree item clicks"""
#         selected_text = item.text(0)
#         parent_item = item.parent()

#         if parent_item is None:
#             # This is a breakout wire
#             self.breakout_wire_selected.emit(selected_text)
#         else:
#             # This is a connection
#             breakout_wire = parent_item.text(0)
#             self.connection_selected.emit(breakout_wire, selected_text)

#     def update_breakout_wire_data(self, data):
#         """Update breakout wire pin data table"""
#         # Implementation to update left table
#         pass

#     def update_connection_data(self, data):
#         """Update connection pin data table"""
#         # Implementation to update middle table
#         pass

#     def toggle_gys_data_visibility(self, visible: bool):
#         """Toggle visibility of GYS data table"""
#         self.right_table.setVisible(visible)
