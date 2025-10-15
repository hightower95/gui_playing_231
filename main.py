import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout,
                               QVBoxLayout, QListWidget, QLabel, QSplitter,
                               QFrame, QListWidgetItem, QComboBox, QPushButton,
                               QGridLayout, QTableWidget, QTableWidgetItem,
                               QScrollArea, QGroupBox, QSizePolicy, QTreeWidget,
                               QTreeWidgetItem)
from PySide6.QtCore import Qt, QObject, Signal


# ===== CONTROL LAYER =====

class ControlLayer(QObject):
    """Control layer that manages data and business logic for the UI"""

    # Signals to update UI components
    update_left_panel = Signal(str, str, str)  # x1_text, x2_text, status_text
    update_right_panel = Signal(str, str, str)  # x1_text, x2_text, status_text
    expand_tree_item = Signal(str)  # main_item_name

    def __init__(self):
        super().__init__()
        self.data_store = {}
        self.current_main_selection = None
        self.current_sub_selection = None
        self.initialize_data()

    def initialize_data(self):
        """Initialize the data store with default values"""
        breakout_wires = ["BreakoutWire1", "BreakoutWire2",
                          "BreakoutWire3", "BreakoutWire4", "BreakoutWire5"]

        for breakout_wire in breakout_wires:
            self.data_store[breakout_wire] = {
                'connections': [f"Connection{i}" for i in range(1, 4)],
                'left_values': {
                    'x1': f"{breakout_wire}_Left_Value",
                    'x2': f"{breakout_wire}_Left_Value2"
                },
                'cable_options': ["Cable_A", "Cable_B", "Cable_C"],
                'status': "Ready"
            }

    def breakout_wire_clicked(self, breakout_wire_name):
        """Handle breakout wire click - expand item and update left panel"""
        print(f"Control Layer: BreakoutWire Clicked - {breakout_wire_name}")

        self.current_main_selection = breakout_wire_name
        self.current_sub_selection = None

        # Expand the tree item
        self.expand_tree_item.emit(breakout_wire_name)

        # Get data for this breakout wire
        if breakout_wire_name in self.data_store:
            data = self.data_store[breakout_wire_name]
            left_values = data['left_values']

            # Update left panel
            x1_text = f"X1: {left_values['x1']}"
            x2_text = f"X2: {left_values['x2']}"
            status_text = f"Status: Reviewing {breakout_wire_name}"

            self.update_left_panel.emit(x1_text, x2_text, status_text)

            # Clear right panel when selecting breakout wire
            self.update_right_panel.emit(
                "X1: Select connection",
                "X2: Select connection",
                "Status: Awaiting connection selection"
            )

    def connection_clicked(self, breakout_wire_name, connection_name):
        """Handle connection click - update both panels"""
        print(
            f"Control Layer: Connection Clicked - {breakout_wire_name}.{connection_name}")

        self.current_main_selection = breakout_wire_name
        self.current_sub_selection = connection_name

        # Update left panel with breakout wire data
        if breakout_wire_name in self.data_store:
            data = self.data_store[breakout_wire_name]
            left_values = data['left_values']

            x1_text = f"X1: {left_values['x1']}"
            x2_text = f"X2: {left_values['x2']}"
            status_text = f"Status: Reviewing {breakout_wire_name}"

            self.update_left_panel.emit(x1_text, x2_text, status_text)

            # Update right panel with connection data
            right_x1 = f"X1: {connection_name}_{breakout_wire_name}_Value"
            right_x2 = f"X2: {connection_name}_{breakout_wire_name}_Value2"
            right_status = f"Status: Reviewing {connection_name}"

            self.update_right_panel.emit(right_x1, right_x2, right_status)

    def get_breakout_wire_data(self, breakout_wire_name):
        """Get data for a breakout wire"""
        return self.data_store.get(breakout_wire_name, {})

    def set_breakout_wire_data(self, breakout_wire_name, **kwargs):
        """Set data for a breakout wire"""
        if breakout_wire_name not in self.data_store:
            self.data_store[breakout_wire_name] = {}

        for key, value in kwargs.items():
            if key in ['x1', 'x2']:
                if 'left_values' not in self.data_store[breakout_wire_name]:
                    self.data_store[breakout_wire_name]['left_values'] = {}
                self.data_store[breakout_wire_name]['left_values'][key] = value
            else:
                self.data_store[breakout_wire_name][key] = value

    def get_current_selection(self):
        """Get current selection state"""
        return {
            'main': self.current_main_selection,
            'sub': self.current_sub_selection
        }


# ===== UI COMPONENT CLASSES =====

class LeftTreePanel(QWidget):
    """Left panel with hierarchical tree selection"""
    item_selected = Signal(str, object)  # selected_text, parent_item

    def __init__(self):
        super().__init__()
        self.main_items_data = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tree widget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setMaximumWidth(150)
        self.tree_widget.setMinimumWidth(100)
        self.tree_widget.setHeaderHidden(True)

        # Connect signals
        self.tree_widget.itemClicked.connect(self.on_item_clicked)

        layout.addWidget(self.tree_widget)

        # Initialize with default data
        self.setup_default_data()

    def setup_default_data(self):
        """Setup default tree data"""
        breakout_wires = ["BreakoutWire1", "BreakoutWire2",
                          "BreakoutWire3", "BreakoutWire4", "BreakoutWire5"]

        self.tree_widget.clear()
        self.main_items_data = {}

        for breakout_wire in breakout_wires:
            self.main_items_data[breakout_wire] = {
                'connections': [f"Connection{i}" for i in range(1, 4)],
                'left_values': {'x1': f"{breakout_wire}_Left_Value", 'x2': f"{breakout_wire}_Left_Value2"},
                'cable_options': ["Cable_A", "Cable_B", "Cable_C"]
            }

            parent = QTreeWidgetItem(self.tree_widget)
            parent.setText(0, breakout_wire)
            parent.setFlags(parent.flags() | Qt.ItemIsSelectable)

            for connection in self.main_items_data[breakout_wire]['connections']:
                child = QTreeWidgetItem(parent)
                child.setText(0, connection)
                child.setFlags(child.flags() | Qt.ItemIsSelectable)

    def on_item_clicked(self, item, column):
        """Handle tree item clicks"""
        selected_text = item.text(0)
        parent_item = item.parent()
        self.item_selected.emit(selected_text, parent_item)

    def set_connections(self, breakout_wire, connections):
        """Set connections for a breakout wire"""
        if breakout_wire not in self.main_items_data:
            self.main_items_data[breakout_wire] = {}
        self.main_items_data[breakout_wire]['connections'] = connections
        self.refresh_tree()

    def set_left_pane_data(self, breakout_wire, x1_value=None, x2_value=None):
        """Set left pane data for a breakout wire"""
        if breakout_wire not in self.main_items_data:
            self.main_items_data[breakout_wire] = {}
        if 'left_values' not in self.main_items_data[breakout_wire]:
            self.main_items_data[breakout_wire]['left_values'] = {}

        if x1_value is not None:
            self.main_items_data[breakout_wire]['left_values']['x1'] = x1_value
        if x2_value is not None:
            self.main_items_data[breakout_wire]['left_values']['x2'] = x2_value

    def set_cable_options(self, breakout_wire, cable_options):
        """Set cable options for a breakout wire"""
        if breakout_wire not in self.main_items_data:
            self.main_items_data[breakout_wire] = {}
        self.main_items_data[breakout_wire]['cable_options'] = cable_options

    def refresh_tree(self):
        """Refresh tree display"""
        breakout_wires = list(self.main_items_data.keys())
        self.tree_widget.clear()

        for breakout_wire in breakout_wires:
            parent = QTreeWidgetItem(self.tree_widget)
            parent.setText(0, breakout_wire)
            parent.setFlags(parent.flags() | Qt.ItemIsSelectable)

            for connection in self.main_items_data[breakout_wire]['connections']:
                child = QTreeWidgetItem(parent)
                child.setText(0, connection)
                child.setFlags(child.flags() | Qt.ItemIsSelectable)


class TopControlPanel(QFrame):
    """Top control panel with grid layout"""
    jump_to_e3_clicked = Signal(str)  # pane_name

    def __init__(self, pane_name=""):
        super().__init__()
        self.pane_name = pane_name
        self.setup_ui()

    def setup_ui(self):
        self.setFrameStyle(QFrame.Box)
        layout = QGridLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Cable dropdown (top left)
        self.cable_combo = QComboBox()
        self.cable_combo.addItems(["Cable_A", "Cable_B", "Cable_C"])

        # Jump to E3 button (top right)
        self.jump_btn = QPushButton("Jump to E3")
        self.jump_btn.clicked.connect(self.on_jump_clicked)

        # X1 label (bottom left)
        self.x1_label = QLabel("X1: Auto_Value_1")

        # X2 label (bottom right)
        self.x2_label = QLabel("X2: Auto_Value_2")

        # Status label (bottom, span 2 columns)
        self.status_label = QLabel("Status: Ready")

        # Add widgets to grid
        layout.addWidget(self.cable_combo, 0, 0)
        layout.addWidget(self.jump_btn, 0, 1)
        layout.addWidget(self.x1_label, 1, 0)
        layout.addWidget(self.x2_label, 1, 1)
        layout.addWidget(self.status_label, 2, 0, 1, 2)

    def on_jump_clicked(self):
        """Handle jump button click"""
        self.jump_to_e3_clicked.emit(self.pane_name)

    def set_values(self, x1_text=None, x2_text=None, status_text=None, cable_selection=None):
        """Set values in the panel"""
        if x1_text:
            self.x1_label.setText(x1_text)
        if x2_text:
            self.x2_label.setText(x2_text)
        if status_text:
            self.status_label.setText(status_text)
        if cable_selection:
            self.cable_combo.setCurrentText(cable_selection)


class TablesPanel(QFrame):
    """Middle panel with three linked tables"""

    def __init__(self):
        super().__init__()
        self.tables = []
        self.table_configs = []
        self.setup_ui()

    def setup_ui(self):
        self.setFrameStyle(QFrame.Box)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        # Setup default table configurations
        self.setup_default_configs()
        self.create_tables()

    def setup_default_configs(self):
        """Setup default table configurations"""
        self.table_configs = [
            {
                'title': 'Breakout Wire Pins',
                'rows': 56,
                'columns': 4,
                'headers': [f"Pin {i+1}" for i in range(4)],
                'data_generator': self.generate_alpha_data,
                'visible': True
            },
            {
                'title': 'Connection Pin Data',
                'rows': 56,
                'columns': 4,
                'headers': [f"Pin {i+1}" for i in range(4)],
                'data_generator': self.generate_alpha_data,
                'visible': True
            },
            {
                'title': 'GYS Data',
                'rows': 56,
                'columns': 4,
                'headers': [f"Data {i+1}" for i in range(4)],
                'data_generator': self.generate_alpha_data,
                'visible': True
            }
        ]

    def generate_alpha_data(self, row, col):
        """Default data generator"""
        chars = [chr(i) for i in range(ord('a'), ord('z')+1)] + [chr(i)
                                                                 for i in range(ord('A'), ord('Z')+1)] + ['a1', 'a2', 'a3', 'a4']
        return f"{chars[row]}{col+1}"

    def create_tables(self):
        """Create tables based on configurations"""
        # Clear existing tables
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

        self.tables = []

        for config in self.table_configs:
            # Create container
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)

            # Title
            title_label = QLabel(config['title'])
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("font-weight: bold; padding: 5px;")
            container_layout.addWidget(title_label)

            # Table
            table = QTableWidget(config['rows'], config['columns'])
            table.setHorizontalHeaderLabels(config['headers'])
            table.horizontalHeader().setStretchLastSection(True)
            table.resizeColumnsToContents()
            table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            # Populate table
            for row in range(config['rows']):
                for col in range(config['columns']):
                    item_text = config['data_generator'](row, col)
                    item = QTableWidgetItem(item_text)
                    table.setItem(row, col, item)

            self.tables.append(table)
            container_layout.addWidget(table)
            self.layout.addWidget(container)

        # Link scrollbars
        self.link_scrollbars()

    def link_scrollbars(self):
        """Link table scrollbars"""
        if len(self.tables) > 1:
            for i in range(1, len(self.tables)):
                self.tables[0].verticalScrollBar().valueChanged.connect(
                    self.tables[i].verticalScrollBar().setValue
                )
                self.tables[i].verticalScrollBar().valueChanged.connect(
                    self.tables[0].verticalScrollBar().setValue
                )

    def set_table_data(self, table_index, data_array, headers=None):
        """Set data for a specific table"""
        if table_index >= len(self.tables):
            return

        table = self.tables[table_index]
        rows = len(data_array)
        cols = len(data_array[0]) if rows > 0 else 0

        table.setRowCount(rows)
        table.setColumnCount(cols)

        if headers:
            table.setHorizontalHeaderLabels(headers)

        for row in range(rows):
            for col in range(len(data_array[row])):
                item = QTableWidgetItem(str(data_array[row][col]))
                table.setItem(row, col, item)

    def update_breakout_wire_pin_data(self, data_array, headers=None):
        """Update data for Breakout Wire Pins table"""
        self.set_table_data(0, data_array, headers)

    def update_connection_pin_data(self, data_array, headers=None):
        """Update data for Connection Pin Data table"""
        self.set_table_data(1, data_array, headers)

    def update_gys_data(self, data_array, headers=None):
        """Update data for GYS Data table"""
        self.set_table_data(2, data_array, headers)

    def clear_table(self, table_index):
        """Clear all data in a specific table"""
        if table_index < len(self.tables):
            table = self.tables[table_index]
            table.setRowCount(0)

    def clear_breakout_wire_pin_data(self):
        """Clear Breakout Wire Pins table"""
        self.clear_table(0)

    def clear_connection_pin_data(self):
        """Clear Connection Pin Data table"""
        self.clear_table(1)

    def clear_gys_data(self):
        """Clear GYS Data table"""
        self.clear_table(2)

    def set_row_highlight(self, table_index, row_indices, color="lightblue"):
        """Highlight specific rows in a table"""
        if table_index >= len(self.tables):
            return

        table = self.tables[table_index]
        if not isinstance(row_indices, list):
            row_indices = [row_indices]

        # for row in row_indices:
        #     if row < table.rowCount():
        #         for col in range(table.columnCount()):
        #             item = table.item(row, col)
        #             if item:
        #                 item.setStyleSheet(f"background-color: {color};")

    def clear_highlights(self, table_index):
        """Clear all highlights in a table"""
        if table_index >= len(self.tables):
            return

        table = self.tables[table_index]
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item:
                    item.setStyleSheet("")

    def clear_all_highlights(self):
        """Clear highlights in all tables"""
        for i in range(len(self.tables)):
            self.clear_highlights(i)

    def toggle_gys_data_visibility(self):
        """Toggle visibility of GYS Data table"""
        if len(self.tables) > 2:
            container = self.tables[2].parent(
            ).parent()  # Get container widget
            container.setVisible(not container.isVisible())
            return container.isVisible()
        return False

    def set_gys_data_visibility(self, visible):
        """Set visibility of GYS Data table"""
        if len(self.tables) > 2:
            container = self.tables[2].parent(
            ).parent()  # Get container widget
            container.setVisible(visible)

    # Legacy methods for backward compatibility
    def set_left_table_data(self, data_array, headers=None):
        """Set data for left table (legacy)"""
        self.update_breakout_wire_pin_data(data_array, headers)

    def set_middle_table_data(self, data_array, headers=None):
        """Set data for middle table (legacy)"""
        self.update_connection_pin_data(data_array, headers)

    def set_right_table_data(self, data_array, headers=None):
        """Set data for right table (legacy)"""
        self.update_gys_data(data_array, headers)


class BottomPanel(QFrame):
    """Bottom panel with four sections and save button"""
    section_completed = Signal(str, str)  # section, choice
    save_result_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.section_completed_status = {
            "AWG": False, "Signals": False, "Pin Count": False, "Connectors": False}
        self.section_choices = {
            "AWG": None, "Signals": None, "Pin Count": None, "Connectors": None}
        self.section_widgets = {}
        self.setup_ui()

    def setup_ui(self):
        self.setFrameStyle(QFrame.Box)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        sections = ["AWG", "Signals", "Pin Count", "Connectors"]

        for section in sections:
            group_box = QGroupBox(section)
            group_layout = QVBoxLayout(group_box)
            group_layout.setSpacing(5)

            # Recommendation label
            recommendation_label = QLabel(f"<Recommendation for {section}>")
            recommendation_label.setWordWrap(True)
            group_layout.addWidget(recommendation_label)

            # Yes/No buttons
            button_layout = QHBoxLayout()
            yes_btn = QPushButton("✓ Yes")
            yes_btn.setStyleSheet(
                "background-color: lightgreen; border: 2px solid transparent;")
            no_btn = QPushButton("✗ No")
            no_btn.setStyleSheet(
                "background-color: lightcoral; border: 2px solid transparent;")

            # Connect buttons
            yes_btn.clicked.connect(
                lambda checked, s=section: self.on_section_choice(s, "Yes"))
            no_btn.clicked.connect(
                lambda checked, s=section: self.on_section_choice(s, "No"))

            button_layout.addWidget(yes_btn)
            button_layout.addWidget(no_btn)
            group_layout.addLayout(button_layout)

            self.section_widgets[section] = {
                'group_box': group_box,
                'recommendation_label': recommendation_label,
                'yes_btn': yes_btn,
                'no_btn': no_btn
            }

            layout.addWidget(group_box)

        # Save Result section
        save_container = QWidget()
        save_layout = QVBoxLayout(save_container)
        save_layout.setSpacing(5)

        # Status text
        self.status_text = QLabel("Status:\nNo selections made")
        self.status_text.setAlignment(Qt.AlignCenter)
        self.status_text.setStyleSheet("font-size: 10px; padding: 5px;")
        save_layout.addWidget(self.status_text)

        save_layout.addStretch()

        # Save button
        self.save_btn = QPushButton("Save Result")
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet("font-weight: bold; padding: 10px;")
        self.save_btn.clicked.connect(self.on_save_clicked)

        save_layout.addWidget(self.save_btn)
        save_layout.addStretch()

        layout.addWidget(save_container)

    def on_section_choice(self, section, choice):
        """Handle section choice"""
        self.section_completed_status[section] = True
        self.section_choices[section] = choice

        # Update button styles
        yes_btn = self.section_widgets[section]['yes_btn']
        no_btn = self.section_widgets[section]['no_btn']

        if choice == "Yes":
            yes_btn.setStyleSheet(
                "background-color: lightgreen; border: 3px solid darkgreen; font-weight: bold;")
            no_btn.setStyleSheet(
                "background-color: lightcoral; border: 2px solid transparent;")
        else:
            no_btn.setStyleSheet(
                "background-color: lightcoral; border: 3px solid darkred; font-weight: bold;")
            yes_btn.setStyleSheet(
                "background-color: lightgreen; border: 2px solid transparent;")

        # Update status text
        self.update_status_text()

        # Check if all sections complete
        all_complete = all(self.section_completed_status.values())
        self.save_btn.setEnabled(all_complete)

        if all_complete:
            self.save_btn.setStyleSheet(
                "font-weight: bold; padding: 10px; background-color: lightblue;")
        else:
            self.save_btn.setStyleSheet("font-weight: bold; padding: 10px;")

        # Emit signal
        self.section_completed.emit(section, choice)

    def update_status_text(self):
        """Update status text with current selections"""
        status_lines = ["Status:"]
        for section, choice in self.section_choices.items():
            if choice:
                status_lines.append(f"{section}: {choice}")
            else:
                status_lines.append(f"{section}: -")
        self.status_text.setText("\n".join(status_lines))

    def on_save_clicked(self):
        """Handle save button click"""
        self.save_result_clicked.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GUI Layout")
        self.showMaximized()  # Full screen by default

        # Initialize control layer
        self.control_layer = ControlLayer()

        # Initialize callbacks
        self.callbacks = {}

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main horizontal layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Create splitter for resizable panes
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Create UI components
        self.left_panel = LeftTreePanel()
        self.top_left_panel = TopControlPanel("Left")
        self.top_right_panel = TopControlPanel("Right")
        self.tables_panel = TablesPanel()
        self.bottom_panel = BottomPanel()

        # Connect UI signals
        self.left_panel.item_selected.connect(self.on_tree_item_selected)
        self.top_left_panel.jump_to_e3_clicked.connect(self.on_jump_to_e3)
        self.top_right_panel.jump_to_e3_clicked.connect(self.on_jump_to_e3)
        self.bottom_panel.section_completed.connect(self.on_section_completed)
        self.bottom_panel.save_result_clicked.connect(self.on_save_result)

        # Connect control layer signals
        self.control_layer.update_left_panel.connect(self.update_left_panel)
        self.control_layer.update_right_panel.connect(self.update_right_panel)
        self.control_layer.expand_tree_item.connect(self.expand_tree_item)

        # Add left panel to splitter
        splitter.addWidget(self.left_panel)

        # Create right side widget
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5)

        # Top section (split horizontally)
        top_splitter = QSplitter(Qt.Horizontal)
        top_splitter.addWidget(self.top_left_panel)
        top_splitter.addWidget(self.top_right_panel)

        # Add components to right layout with stretch factors
        right_layout.addWidget(top_splitter, 1)      # 20%
        right_layout.addWidget(self.tables_panel, 5)  # 60%
        right_layout.addWidget(self.bottom_panel, 2)  # 20%

        splitter.addWidget(right_widget)

        # Set splitter proportions
        splitter.setSizes([150, 650])

    def on_tree_item_selected(self, selected_text, parent_item):
        """Handle tree item selection - delegate to control layer"""
        # Trigger callback for tree selection
        self.trigger_callback('tree_item_selected', selected_text, parent_item)

        # Check if this is a parent item (BreakoutWire) or child item (Connection)
        if parent_item is None:
            # This is a breakout wire - delegate to control layer
            self.control_layer.breakout_wire_clicked(selected_text)
        else:
            # This is a connection - delegate to control layer
            breakout_wire_name = parent_item.text(0)
            self.control_layer.connection_clicked(
                breakout_wire_name, selected_text)

    def on_jump_to_e3(self, pane_name):
        """Handle Jump to E3 button clicks"""
        print(f"Jump to E3 clicked from {pane_name} pane")
        if pane_name == "Left":
            self.top_left_panel.set_values(status_text="Status: Jumped to E3")
        else:
            self.top_right_panel.set_values(status_text="Status: Jumped to E3")

    def on_section_completed(self, section, choice):
        """Handle section completion"""
        print(f"Section {section} completed with choice: {choice}")
        # You can add additional logic here if needed

    def on_save_result(self):
        """Handle save result button click"""
        print("Save Result clicked - All sections completed!")
        # Here you would implement the save functionality
        self.top_left_panel.set_values(status_text="Status: Results Saved")
        self.top_right_panel.set_values(status_text="Status: Results Saved")

    # ===== CONTROL LAYER SIGNAL HANDLERS =====

    def update_left_panel(self, x1_text, x2_text, status_text):
        """Update left panel from control layer"""
        self.top_left_panel.set_values(
            x1_text=x1_text,
            x2_text=x2_text,
            status_text=status_text,
            cable_selection="Cable_A"
        )

    def update_right_panel(self, x1_text, x2_text, status_text):
        """Update right panel from control layer"""
        self.top_right_panel.set_values(
            x1_text=x1_text,
            x2_text=x2_text,
            status_text=status_text,
            cable_selection="Cable_X" if "sub-item" not in x1_text.lower() else None
        )

    def expand_tree_item(self, breakout_wire_name):
        """Expand tree item from control layer"""
        # Find and expand the tree item
        for i in range(self.left_panel.tree_widget.topLevelItemCount()):
            item = self.left_panel.tree_widget.topLevelItem(i)
            if item.text(0) == breakout_wire_name:
                item.setExpanded(True)
                break

    # ===== CONVENIENCE METHODS FOR COMPONENT ACCESS =====

    def set_breakout_wire_connections(self, breakout_wire, connections):
        """Set connections for a breakout wire"""
        # Update both UI and control layer
        self.left_panel.set_connections(breakout_wire, connections)
        self.control_layer.set_breakout_wire_data(
            breakout_wire, connections=connections)

    def set_breakout_wire_left_pane_data(self, breakout_wire, x1_value=None, x2_value=None):
        """Set left pane X1 and X2 values for a breakout wire"""
        # Update both UI and control layer
        self.left_panel.set_left_pane_data(breakout_wire, x1_value, x2_value)
        if x1_value is not None:
            self.control_layer.set_breakout_wire_data(
                breakout_wire, x1=x1_value)
        if x2_value is not None:
            self.control_layer.set_breakout_wire_data(
                breakout_wire, x2=x2_value)

    def set_breakout_wire_cable_options(self, breakout_wire, cable_options):
        """Set cable dropdown options for a breakout wire"""
        # Update both UI and control layer
        self.left_panel.set_cable_options(breakout_wire, cable_options)
        self.control_layer.set_breakout_wire_data(
            breakout_wire, cable_options=cable_options)

    # ===== TABLE MANAGEMENT METHODS =====

    def update_breakout_wire_pin_data(self, data_array, headers=None):
        """Update Breakout Wire Pin Data table"""
        self.tables_panel.update_breakout_wire_pin_data(data_array, headers)

    def update_connection_pin_data(self, data_array, headers=None):
        """Update Connection Pin Data table"""
        self.tables_panel.update_connection_pin_data(data_array, headers)

    def update_gys_data(self, data_array, headers=None):
        """Update GYS Data table"""
        self.tables_panel.update_gys_data(data_array, headers)

    def clear_breakout_wire_pin_data(self):
        """Clear Breakout Wire Pin Data table"""
        self.tables_panel.clear_breakout_wire_pin_data()

    def clear_connection_pin_data(self):
        """Clear Connection Pin Data table"""
        self.tables_panel.clear_connection_pin_data()

    def clear_gys_data(self):
        """Clear GYS Data table"""
        self.tables_panel.clear_gys_data()

    def set_breakout_wire_pin_highlights(self, row_indices, color="lightblue"):
        """Set row highlights in Breakout Wire Pin Data table"""
        self.tables_panel.set_row_highlight(0, row_indices, color)

    def set_connection_pin_highlights(self, row_indices, color="lightblue"):
        """Set row highlights in Connection Pin Data table"""
        self.tables_panel.set_row_highlight(1, row_indices, color)

    def set_gys_data_highlights(self, row_indices, color="lightblue"):
        """Set row highlights in GYS Data table"""
        self.tables_panel.set_row_highlight(2, row_indices, color)

    def clear_breakout_wire_pin_highlights(self):
        """Clear highlights in Breakout Wire Pin Data table"""
        self.tables_panel.clear_highlights(0)

    def clear_connection_pin_highlights(self):
        """Clear highlights in Connection Pin Data table"""
        self.tables_panel.clear_highlights(1)

    def clear_gys_data_highlights(self):
        """Clear highlights in GYS Data table"""
        self.tables_panel.clear_highlights(2)

    def clear_all_table_highlights(self):
        """Clear all table highlights"""
        self.tables_panel.clear_all_highlights()

    def toggle_gys_data_visibility(self):
        """Toggle GYS Data table visibility"""
        return self.tables_panel.toggle_gys_data_visibility()

    def set_gys_data_visibility(self, visible):
        """Set GYS Data table visibility"""
        self.tables_panel.set_gys_data_visibility(visible)

    # Legacy methods for backward compatibility
    def set_left_table_data(self, data_array, headers=None):
        """Set data for the left table (legacy)"""
        self.update_breakout_wire_pin_data(data_array, headers)

    def set_middle_table_data(self, data_array, headers=None):
        """Set data for the middle table (legacy)"""
        self.update_connection_pin_data(data_array, headers)

    def set_right_table_data(self, data_array, headers=None):
        """Set data for the right table (legacy)"""
        self.update_gys_data(data_array, headers)

    def register_callback(self, event_name, callback_func):
        """Register callback functions for various events"""
        if event_name not in self.callbacks:
            self.callbacks[event_name] = []
        self.callbacks[event_name].append(callback_func)

    def trigger_callback(self, event_name, *args, **kwargs):
        """Trigger registered callbacks for an event"""
        if event_name in self.callbacks:
            for callback in self.callbacks[event_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"Error in callback {callback.__name__}: {e}")

    # ===== CONTROL LAYER ACCESS METHODS =====

    def get_control_layer(self):
        """Get access to the control layer for advanced operations"""
        return self.control_layer

    def get_current_selection(self):
        """Get current selection from control layer"""
        return self.control_layer.get_current_selection()

    def simulate_breakout_wire_click(self, breakout_wire_name):
        """Programmatically simulate breakout wire click"""
        self.control_layer.breakout_wire_clicked(breakout_wire_name)

    def simulate_connection_click(self, breakout_wire_name, connection_name):
        """Programmatically simulate connection click"""
        self.control_layer.connection_clicked(
            breakout_wire_name, connection_name)

    # Legacy methods for backward compatibility
    def simulate_main_item_click(self, item_name):
        """Programmatically simulate main item click (legacy)"""
        self.simulate_breakout_wire_click(item_name)

    def simulate_sub_item_click(self, main_item_name, sub_item_name):
        """Programmatically simulate sub item click (legacy)"""
        self.simulate_connection_click(main_item_name, sub_item_name)


# ===== EXAMPLE USAGE FUNCTIONS =====

def example_custom_data_generator(row, col):
    """Example custom data generator for tables"""
    return f"Custom_{row}_{col}"


def example_tree_callback(selected_text, parent_item):
    """Example callback for tree selection events"""
    print(
        f"Tree callback: Selected {selected_text}, Parent: {parent_item.text(0) if parent_item else 'None'}")


def setup_custom_configuration(window):
    """Example function showing how to customize the application"""

    # Configure breakout wires with connections
    window.set_breakout_wire_connections("BreakoutWire1", [
                                         "Connection1", "Connection2", "Connection3", "Connection4"])  # Add Connection4
    window.set_breakout_wire_left_pane_data(
        "BreakoutWire1", x1_value="Custom_BW1_X1", x2_value="Custom_BW1_X2")
    window.set_breakout_wire_cable_options(
        "BreakoutWire1", ["Custom_Cable_1", "Custom_Cable_2"])

    # Configure another breakout wire
    window.set_breakout_wire_connections("BreakoutWire2", [
                                         "Connection1", "Connection2", "Connection5", "Connection6"])  # Different connections
    window.set_breakout_wire_left_pane_data(
        "BreakoutWire2", x1_value="Special_BW2_X1", x2_value="Special_BW2_X2")

    # Set table data using new methods
    breakout_wire_pin_data = [
        ["Pin A1", "Signal", "5V", "Active"],
        ["Pin A2", "Ground", "0V", "Active"],
        ["Pin B1", "Data", "3.3V", "Pending"]
    ]
    window.update_breakout_wire_pin_data(breakout_wire_pin_data, headers=[
                                         "Pin", "Type", "Voltage", "Status"])

    connection_pin_data = [
        ["Conn1", "Wire12", "Panel A", "Red"],
        ["Conn2", "Wire34", "Panel B", "Blue"],
        ["Conn3", "Wire56", "Panel C", "Green"]
    ]
    window.update_connection_pin_data(connection_pin_data, headers=[
                                      "Connection", "Wire", "Panel", "Color"])

    gys_data = [
        ["GYS001", "Primary data line"],
        ["GYS002", "Secondary data line"],
        ["GYS003", "Backup data line"]
    ]
    window.update_gys_data(gys_data, headers=["GYS ID", "Description"])

    # Demonstrate table highlighting
    window.set_breakout_wire_pin_highlights(
        [0, 2], "lightyellow")  # Highlight rows 0 and 2
    window.set_connection_pin_highlights(1, "lightgreen")  # Highlight row 1

    # Register callback for tree events
    window.register_callback('tree_item_selected', example_tree_callback)

    # Demonstrate control layer usage
    print("Current selection:", window.get_current_selection())

    # Programmatically trigger selections to test the control layer
    print("Simulating BreakoutWire1 selection...")
    window.simulate_breakout_wire_click("BreakoutWire1")

    print("Current selection after BreakoutWire1:",
          window.get_current_selection())

    # Access control layer directly for advanced operations
    control = window.get_control_layer()
    control.set_breakout_wire_data("BreakoutWire3", x1="Direct_Control_X1",
                                   x2="Direct_Control_X2", status="Modified by Control Layer")

    # Demonstrate GYS data visibility toggle
    print("Toggling GYS Data visibility...")
    visible = window.toggle_gys_data_visibility()
    print(f"GYS Data is now {'visible' if visible else 'hidden'}")

    print("Custom configuration applied!")


def main():
    app = QApplication(sys.argv)

    window = MainWindow()

    # Example: Apply custom configuration
    # Uncomment the line below to see custom configuration in action
    setup_custom_configuration(window)

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
