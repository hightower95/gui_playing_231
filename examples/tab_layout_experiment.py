"""
Standalone Layout Experiment - Fast UI testing without loading the full app

Run directly: python tab_layout_experiment.py
"""

from PySide6.QtGui import QFont, QColor, QDrag, QPixmap
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QSpinBox, QCheckBox,
    QGroupBox, QFormLayout, QTextEdit, QFrame, QGridLayout,
    QStackedLayout, QSplitter, QTabWidget, QListWidget, QListWidgetItem,
    QScrollArea
)
import sys
from pathlib import Path

# Add parent directories to path for imports
gui_root = Path(__file__).parent.parent
sys.path.insert(0, str(gui_root))


# Optional: Try to import from productivity app for StandardLabel
try:
    from productivity_app.productivity_core.ui.components.label import StandardLabel, TextStyle
    HAS_STANDARD_LABEL = True
except ImportError:
    HAS_STANDARD_LABEL = False
    # Define a fallback

    class StandardLabel(QLabel):
        def __init__(self, text="", style=None, parent=None):
            super().__init__(text, parent)

    class TextStyle:
        SECTION = "SECTION"
        NOTES = "NOTES"
        STATUS = "STATUS"


class LayoutExperimentWindow(QMainWindow):
    """Standalone layout experiment window for rapid UI prototyping"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Layout Experiment Studio 🧪")
        self.setGeometry(100, 100, 1400, 900)

        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Left panel - Controls
        left_panel = self._create_control_panel()
        main_layout.addWidget(left_panel, 1)

        # Right panel - Sandbox
        right_panel = self._create_sandbox()
        main_layout.addWidget(right_panel, 2)

    def _create_control_panel(self) -> QGroupBox:
        """Create the control/experiment selector panel"""
        group = QGroupBox("Layout Experiments")
        layout = QVBoxLayout()
        layout.setSpacing(8)

        # Title
        title = QLabel("Quick Layout Tests")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)

        # Layout test buttons
        experiments = [
            ("🎨 Flex Layout", self._test_flex_layout),
            ("📐 Grid Layout", self._test_grid_layout),
            ("📝 Form Layout", self._test_form_layout),
            ("📚 Stacked Layout", self._test_stacked_layout),
            ("✂️ Splitter", self._test_splitter),
            ("🎯 Responsive Grid", self._test_responsive_grid),
            ("🔲 Cards Layout", self._test_cards_layout),
            ("🧩 Draggable Cards", self._test_draggable_cards),
            ("📥 File Drop Zone", self._test_file_drop_zone),
            ("📄 Document Manager", self._test_document_manager),
            ("📊 Dashboard", self._test_dashboard),
            ("🔌 Plugin Manager", self._test_plugin_manager),
        ]

        for label, callback in experiments:
            btn = QPushButton(label)
            btn.clicked.connect(callback)
            btn.setMinimumHeight(35)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #1565C0;
                }
            """)
            layout.addWidget(btn)

        # Component showcase
        layout.addSpacing(20)
        showcase_title = QLabel("Component Showcase")
        showcase_title.setFont(QFont("Arial", 11, QFont.Bold))
        layout.addWidget(showcase_title)

        layout.addWidget(StandardLabel(
            "SECTION Style", style=TextStyle.SECTION))
        layout.addWidget(StandardLabel("NOTES Style", style=TextStyle.NOTES))
        layout.addWidget(StandardLabel("STATUS Style", style=TextStyle.STATUS))

        # Input components
        layout.addSpacing(15)
        input_title = QLabel("Input Examples")
        input_title.setFont(QFont("Arial", 11, QFont.Bold))
        layout.addWidget(input_title)

        form = QFormLayout()
        form.addRow("Text:", QLineEdit("Sample"))
        form.addRow("Number:", QSpinBox())
        combo = QComboBox()
        combo.addItems(["Option 1", "Option 2", "Option 3"])
        form.addRow("Select:", combo)
        form.addRow("Check:", QCheckBox("Enable"))
        layout.addLayout(form)

        layout.addStretch()

        # Clear button
        clear_btn = QPushButton("🔄 Clear")
        clear_btn.clicked.connect(self._clear_sandbox)
        clear_btn.setMinimumHeight(30)
        layout.addWidget(clear_btn)

        group.setLayout(layout)
        return group

    def _create_sandbox(self) -> QFrame:
        """Create the sandbox/experiment area"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                border: 2px solid #999;
                border-radius: 5px;
                background-color: white;
            }
        """)

        self.sandbox_layout = QVBoxLayout(frame)
        self.sandbox_layout.setContentsMargins(10, 10, 10, 10)

        # Welcome message
        welcome = QLabel("👈 Select an experiment to get started")
        welcome.setFont(QFont("Arial", 12))
        welcome.setStyleSheet("color: #999; text-align: center;")
        welcome.setAlignment(Qt.AlignCenter)
        self.sandbox_layout.addWidget(welcome, 1)

        return frame

    def _clear_sandbox(self):
        """Clear the sandbox"""
        while self.sandbox_layout.count():
            item = self.sandbox_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        welcome = QLabel("👈 Select an experiment to get started")
        welcome.setFont(QFont("Arial", 12))
        welcome.setStyleSheet("color: #999; text-align: center;")
        welcome.setAlignment(Qt.AlignCenter)
        self.sandbox_layout.addWidget(welcome, 1)

    def _set_sandbox_content(self, widget: QWidget):
        """Replace sandbox content with a new widget"""
        self._clear_sandbox()
        self.sandbox_layout.insertWidget(0, widget, 1)

    # ========================================================================
    # LAYOUT EXPERIMENTS
    # ========================================================================

    def _test_flex_layout(self):
        """Test flexible/responsive layout"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(10)

        title = QLabel("Flexible Layout - Responsive Spacing")
        title.setFont(QFont("Arial", 13, QFont.Bold))
        layout.addWidget(title)

        # Row 1: Equal width
        row1_label = QLabel("Row 1: Equal width buttons (1:1:1)")
        row1_label.setStyleSheet("font-weight: bold; color: #666;")
        layout.addWidget(row1_label)

        row1 = QHBoxLayout()
        for i in range(3):
            btn = QPushButton(f"Button {i+1}")
            row1.addWidget(btn)
        layout.addLayout(row1)

        # Row 2: With stretch
        row2_label = QLabel("Row 2: Buttons with center stretch")
        row2_label.setStyleSheet("font-weight: bold; color: #666;")
        layout.addWidget(row2_label)

        row2 = QHBoxLayout()
        row2.addWidget(QPushButton("Left"))
        row2.addStretch()
        row2.addWidget(QLineEdit("Centered"))
        row2.addStretch()
        row2.addWidget(QPushButton("Right"))
        layout.addLayout(row2)

        # Row 3: Custom ratios
        row3_label = QLabel("Row 3: Custom ratios (1:2:3)")
        row3_label.setStyleSheet("font-weight: bold; color: #666;")
        layout.addWidget(row3_label)

        row3 = QHBoxLayout()
        for i, ratio in enumerate([1, 2, 3]):
            btn = QPushButton(f"Ratio {ratio}x")
            row3.addWidget(btn, ratio)
        layout.addLayout(row3)

        # Info
        info = QTextEdit()
        info.setReadOnly(True)
        info.setMaximumHeight(120)
        info.setText("""
FLEX LAYOUT PATTERNS:
• addStretch() - Fills available space
• layout.addWidget(widget, stretch_factor) - Custom ratios
• Resize window to see responsive behavior

Use for: Toolbars, button groups, responsive UIs
        """)
        layout.addWidget(info)

        layout.addStretch()
        self._set_sandbox_content(container)

    def _test_grid_layout(self):
        """Test grid layout"""
        container = QWidget()
        layout = QGridLayout(container)
        layout.setSpacing(8)

        title = QLabel("Grid Layout - Structured Positioning")
        title.setFont(QFont("Arial", 13, QFont.Bold))
        layout.addWidget(title, 0, 0, 1, 4)

        # 4x3 grid
        for row in range(1, 4):
            for col in range(4):
                btn = QPushButton(f"({row},{col})")
                layout.addWidget(btn, row, col)

        # Spanning cell
        spanning = QLabel("Spanning 2x2 cells")
        spanning.setStyleSheet("""
            QLabel {
                background-color: #e3f2fd;
                border: 2px solid #2196F3;
                padding: 20px;
                font-weight: bold;
                text-align: center;
                border-radius: 4px;
            }
        """)
        layout.addWidget(spanning, 4, 1, 2, 2)

        # Info
        info = QTextEdit()
        info.setReadOnly(True)
        info.setMaximumHeight(100)
        info.setText("""
GRID LAYOUT FEATURES:
• addWidget(widget, row, col, row_span, col_span)
• Regular cells and spanning cells
• Consistent spacing with setSpacing()

Use for: Data tables, dashboards, control panels
        """)
        layout.addWidget(info, 6, 0, 1, 4)

        self._set_sandbox_content(container)

    def _test_form_layout(self):
        """Test form layout"""
        container = QWidget()
        layout = QVBoxLayout(container)

        title = QLabel("Form Layout - Data Entry")
        title.setFont(QFont("Arial", 13, QFont.Bold))
        layout.addWidget(title)

        # Group 1
        group1 = QGroupBox("Personal Information")
        form1 = QFormLayout()
        form1.addRow("First Name:", QLineEdit("John"))
        form1.addRow("Last Name:", QLineEdit("Doe"))
        form1.addRow("Email:", QLineEdit("john@example.com"))
        form1.addRow("Age:", QSpinBox())
        group1.setLayout(form1)
        layout.addWidget(group1)

        # Group 2
        group2 = QGroupBox("Preferences")
        form2 = QFormLayout()

        theme = QComboBox()
        theme.addItems(["Light", "Dark", "Auto"])
        form2.addRow("Theme:", theme)

        lang = QComboBox()
        lang.addItems(["English", "Spanish", "French"])
        form2.addRow("Language:", lang)

        form2.addRow("Notifications:", QCheckBox("Enabled"))
        group2.setLayout(form2)
        layout.addWidget(group2)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(QPushButton("Save"))
        btn_layout.addWidget(QPushButton("Cancel"))
        layout.addLayout(btn_layout)

        # Info
        info = QTextEdit()
        info.setReadOnly(True)
        info.setMaximumHeight(80)
        info.setText("""
FORM LAYOUT ADVANTAGES:
• Automatic label-field alignment
• Clean two-column presentation
• Easy to group related fields
• Professional appearance
        """)
        layout.addWidget(info)

        layout.addStretch()
        self._set_sandbox_content(container)

    def _test_stacked_layout(self):
        """Test stacked/tabbed layout"""
        container = QWidget()
        layout = QVBoxLayout(container)

        title = QLabel("Stacked Layout - Multi-View Pages")
        title.setFont(QFont("Arial", 13, QFont.Bold))
        layout.addWidget(title)

        # Navigation
        nav = QHBoxLayout()
        nav.setSpacing(5)

        stack = QStackedLayout()

        # Create pages
        colors = ["#ffebee", "#e8f5e9", "#e3f2fd"]
        page_titles = ["Page 1: Red", "Page 2: Green", "Page 3: Blue"]

        for i, (color, page_title) in enumerate(zip(colors, page_titles)):
            page = QFrame()
            page.setStyleSheet(
                f"background-color: {color}; border-radius: 5px;")
            page_layout = QVBoxLayout(page)

            page_label = QLabel(page_title)
            page_label.setFont(QFont("Arial", 14, QFont.Bold))
            page_layout.addWidget(page_label)

            page_layout.addWidget(QLabel(f"This is content for {page_title}"))
            page_layout.addWidget(QTextEdit(f"Editable area {i+1}"))
            page_layout.addStretch()

            stack.addWidget(page)

            # Create button
            btn = QPushButton(f"→ {page_title}")
            btn.clicked.connect(
                lambda checked, idx=i: stack.setCurrentIndex(idx))
            nav.addWidget(btn)

        layout.addLayout(nav)
        layout.addLayout(stack, 1)

        stack.setCurrentIndex(0)

        # Info
        info = QTextEdit()
        info.setReadOnly(True)
        info.setMaximumHeight(80)
        info.setText("""
STACKED LAYOUT USES:
• Multi-step wizards
• Tabbed interfaces (without QTabWidget)
• Only active view is visible (memory efficient)
• Smooth page transitions possible
        """)
        layout.addWidget(info)

        self._set_sandbox_content(container)

    def _test_splitter(self):
        """Test splitter widget"""
        container = QWidget()
        layout = QVBoxLayout(container)

        title = QLabel("Splitter - Resizable Panels")
        title.setFont(QFont("Arial", 13, QFont.Bold))
        layout.addWidget(title)

        splitter = QSplitter(Qt.Horizontal)

        # Left panel
        left = QFrame()
        left.setStyleSheet("background-color: #fff3e0; border-radius: 4px;")
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(QLabel("Left Panel (1x)"))
        left_layout.addWidget(QTextEdit("Drag divider to resize"))

        # Center panel
        center = QFrame()
        center.setStyleSheet("background-color: #f3e5f5; border-radius: 4px;")
        center_layout = QVBoxLayout(center)
        center_layout.addWidget(QLabel("Center Panel (2x)"))
        center_layout.addWidget(QTextEdit("Main content area"))

        # Right panel
        right = QFrame()
        right.setStyleSheet("background-color: #e0f2f1; border-radius: 4px;")
        right_layout = QVBoxLayout(right)
        right_layout.addWidget(QLabel("Right Panel (1x)"))
        right_layout.addWidget(QTextEdit("Side information"))

        splitter.addWidget(left)
        splitter.addWidget(center)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 1)

        layout.addWidget(splitter, 1)

        # Info
        info = QTextEdit()
        info.setReadOnly(True)
        info.setMaximumHeight(80)
        info.setText("""
SPLITTER FEATURES:
• Drag dividers to resize panels
• Save/restore splitter state
• Multiple panels supported
• Collapsible panels (with custom code)
        """)
        layout.addWidget(info)

        self._set_sandbox_content(container)

    def _test_responsive_grid(self):
        """Test responsive grid"""
        container = QWidget()
        layout = QVBoxLayout(container)

        title = QLabel("Responsive Grid - Auto-Wrapping Items")
        title.setFont(QFont("Arial", 13, QFont.Bold))
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(10)

        # Create items
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1",
                  "#FFA07A", "#98D8C8", "#F7DC6F"]
        for i, color in enumerate(colors):
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border-radius: 8px;
                    padding: 20px;
                }}
            """)
            card_layout = QVBoxLayout(card)
            label = QLabel(f"Card {i+1}")
            label.setFont(QFont("Arial", 11, QFont.Bold))
            label.setStyleSheet("color: white;")
            card_layout.addWidget(label)

            # Calculate position (3 columns)
            row = i // 3
            col = i % 3
            grid.addWidget(card, row, col)

        layout.addLayout(grid)

        # Info
        info = QTextEdit()
        info.setReadOnly(True)
        info.setMaximumHeight(80)
        info.setText("""
RESPONSIVE GRID PATTERN:
• Fixed number of columns
• Items arrange in rows
• Equal-sized cells
• Good for card-based UIs
        """)
        layout.addWidget(info)

        layout.addStretch()
        self._set_sandbox_content(container)

    def _test_cards_layout(self):
        """Test card-based layout"""
        container = QWidget()
        layout = QVBoxLayout(container)

        title = QLabel("Cards Layout - Content Cards with Icons")
        title.setFont(QFont("Arial", 13, QFont.Bold))
        layout.addWidget(title)

        cards_grid = QGridLayout()
        cards_grid.setSpacing(15)

        cards = [
            ("📊 Analytics", "View system metrics"),
            ("⚙️ Settings", "Configure options"),
            ("📁 Files", "Manage documents"),
            ("🔍 Search", "Find information"),
            ("📧 Messages", "View notifications"),
            ("👥 Users", "Manage team"),
        ]

        for i, (icon_title, desc) in enumerate(cards):
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 15px;
                }
                QFrame:hover {
                    border: 2px solid #2196F3;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }
            """)

            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(8)

            # Title with icon
            title_label = QLabel(icon_title)
            title_label.setFont(QFont("Arial", 12, QFont.Bold))
            card_layout.addWidget(title_label)

            # Description
            desc_label = QLabel(desc)
            desc_label.setStyleSheet("color: #666; font-size: 10pt;")
            card_layout.addWidget(desc_label)

            # Button
            btn = QPushButton("Open →")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px;
                }
            """)
            card_layout.addWidget(btn)

            row = i // 3
            col = i % 3
            cards_grid.addWidget(card, row, col)

        layout.addLayout(cards_grid)

        # Info
        info = QTextEdit()
        info.setReadOnly(True)
        info.setMaximumHeight(80)
        info.setText("""
CARD LAYOUT PATTERN:
• Self-contained content units
• Icon + title + description
• Call-to-action button
• Hover effects for interactivity
• Great for dashboards and portals
        """)
        layout.addWidget(info)

        layout.addStretch()
        self._set_sandbox_content(container)

    def _test_dashboard(self):
        """Test dashboard layout"""
        container = QWidget()
        layout = QVBoxLayout(container)

        title = QLabel("Dashboard Layout - Mixed Widget Sizes")
        title.setFont(QFont("Arial", 13, QFont.Bold))
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(10)

        # Create panels
        panels = [
            ("📈 Performance", "#FF6B6B", 0, 0, 1, 1),
            ("🎯 Goals", "#4ECDC4", 0, 1, 1, 2),
            ("💰 Budget", "#45B7D1", 1, 0, 1, 1),
            ("📊 Analytics", "#FFA07A", 1, 1, 2, 1),
            ("⚡ Activity", "#98D8C8", 1, 2, 1, 1),
            ("📝 Notes", "#F7DC6F", 2, 0, 1, 2),
        ]

        for title_text, color, row, col, row_span, col_span in panels:
            panel = QFrame()
            panel.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border-radius: 8px;
                    padding: 15px;
                }}
            """)

            panel_layout = QVBoxLayout(panel)
            panel_title = QLabel(title_text)
            panel_title.setFont(QFont("Arial", 11, QFont.Bold))
            panel_title.setStyleSheet("color: white;")
            panel_layout.addWidget(panel_title)

            # Content
            if row_span > 1 or col_span > 1:
                panel_layout.addWidget(QTextEdit("Large panel content"), 1)
            else:
                panel_layout.addWidget(QLabel("Metric: 1,234"), 1)

            grid.addWidget(panel, row, col, row_span, col_span)

        layout.addLayout(grid, 1)

        # Info
        info = QTextEdit()
        info.setReadOnly(True)
        info.setMaximumHeight(80)
        info.setText("""
DASHBOARD PATTERN:
• Mixed widget sizes (1x1, 1x2, 2x1)
• Color-coded sections
• At-a-glance metrics
• Responsive grid system
• Perfect for status displays
        """)
        layout.addWidget(info)

        self._set_sandbox_content(container)

    def _test_plugin_manager(self):
        """Test plugin manager layout with categorized list and details panel"""
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Plugin Manager - Master/Detail Layout")
        title.setFont(QFont("Arial", 13, QFont.Bold))
        main_layout.addWidget(title)

        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)

        # === LEFT PANEL: Plugin List ===
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # Plugin list with sections
        plugin_list = QListWidget()
        plugin_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                background: #fafafa;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background: #2196F3;
                color: white;
            }
            QListWidget::item:hover:!selected {
                background: #e3f2fd;
            }
        """)

        # Sample plugin data
        plugins = {
            "Starred": [
                {"name": "Data Validator", "version": "2.1.0", "starred": True},
                {"name": "Auto Formatter", "version": "1.5.2", "starred": True},
            ],
            "Local": [
                {"name": "Custom Exporter", "version": "1.0.0", "starred": False},
                {"name": "Debug Helper", "version": "0.9.1", "starred": False},
                {"name": "Theme Manager", "version": "2.0.0", "starred": False},
            ],
            "Global": [
                {"name": "PDF Generator", "version": "3.2.1", "starred": False},
                {"name": "API Connector", "version": "1.8.0", "starred": False},
                {"name": "Report Builder", "version": "2.4.0", "starred": False},
                {"name": "Data Sync", "version": "1.1.0", "starred": False},
            ],
        }

        # Store plugin details for lookup
        self._plugin_details = {}

        for section, items in plugins.items():
            # Section header
            header_item = QListWidgetItem(f"  {section}")
            header_item.setFlags(Qt.NoItemFlags)  # Non-selectable
            header_font = QFont()
            header_font.setBold(True)
            header_font.setPointSize(10)
            header_item.setFont(header_font)
            header_item.setBackground(QColor("#e0e0e0"))
            plugin_list.addItem(header_item)

            # Section items
            for plugin in items:
                if section == "Starred":
                    display_text = f"    * {plugin['name']}"
                elif section == "Local":
                    display_text = f"    {plugin['name']}"
                else:
                    display_text = f"    {plugin['name']}"

                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, plugin['name'])  # Store plugin name for lookup
                plugin_list.addItem(item)

                # Store details
                self._plugin_details[plugin['name']] = {
                    "name": plugin['name'],
                    "version": plugin['version'],
                    "section": section,
                    "starred": plugin.get('starred', False),
                    "requirements": self._get_mock_requirements(plugin['name']),
                    "parameters": self._get_mock_parameters(plugin['name']),
                }

        left_layout.addWidget(plugin_list)
        splitter.addWidget(left_panel)

        # === RIGHT PANEL: Plugin Details ===
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 0, 0, 0)

        # Details header
        self._plugin_title = QLabel("Select a plugin")
        self._plugin_title.setFont(QFont("Arial", 14, QFont.Bold))
        right_layout.addWidget(self._plugin_title)

        self._plugin_version = QLabel("")
        self._plugin_version.setStyleSheet("color: #666; font-style: italic;")
        right_layout.addWidget(self._plugin_version)

        # Star button for local plugins
        self._star_btn = QPushButton("Add to Starred")
        self._star_btn.setVisible(False)
        self._star_btn.setStyleSheet("""
            QPushButton {
                background: #FFC107;
                color: #333;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #FFB300;
            }
        """)
        self._star_btn.setMaximumWidth(150)
        right_layout.addWidget(self._star_btn)

        right_layout.addSpacing(15)

        # Requirements section
        req_label = QLabel("Requirements")
        req_label.setFont(QFont("Arial", 11, QFont.Bold))
        right_layout.addWidget(req_label)

        self._requirements_list = QListWidget()
        self._requirements_list.setMaximumHeight(120)
        self._requirements_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
            }
            QListWidget::item {
                padding: 4px 8px;
            }
        """)
        right_layout.addWidget(self._requirements_list)

        right_layout.addSpacing(10)

        # Parameters section
        param_label = QLabel("Parameters")
        param_label.setFont(QFont("Arial", 11, QFont.Bold))
        right_layout.addWidget(param_label)

        self._parameters_widget = QWidget()
        self._parameters_layout = QFormLayout(self._parameters_widget)
        self._parameters_layout.setContentsMargins(0, 0, 0, 0)

        params_scroll = QScrollArea()
        params_scroll.setWidget(self._parameters_widget)
        params_scroll.setWidgetResizable(True)
        params_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
            }
        """)
        right_layout.addWidget(params_scroll, 1)

        splitter.addWidget(right_panel)

        # Set splitter proportions
        splitter.setSizes([250, 450])

        main_layout.addWidget(splitter, 1)

        # Connect selection signal
        plugin_list.currentItemChanged.connect(self._on_plugin_selected)

        # Info
        info = QTextEdit()
        info.setReadOnly(True)
        info.setMaximumHeight(60)
        info.setText("""
PLUGIN MANAGER PATTERN: Categorized list (Starred/Local/Global) with master-detail layout.
Click a plugin to see its requirements and configurable parameters.
        """)
        main_layout.addWidget(info)

        self._set_sandbox_content(container)

    def _on_plugin_selected(self, current, previous):
        """Handle plugin selection"""
        if current is None:
            return

        plugin_name = current.data(Qt.UserRole)
        if plugin_name is None:
            return  # Section header clicked

        details = self._plugin_details.get(plugin_name)
        if not details:
            return

        # Update header
        self._plugin_title.setText(details['name'])
        self._plugin_version.setText(f"Version {details['version']} - {details['section']}")

        # Show/hide star button for Local plugins
        if details['section'] == 'Local' and not details['starred']:
            self._star_btn.setVisible(True)
        else:
            self._star_btn.setVisible(False)

        # Update requirements
        self._requirements_list.clear()
        for req in details['requirements']:
            item = QListWidgetItem(f"  {req['name']} {req['version']}")
            if req.get('installed'):
                item.setForeground(QColor("#4CAF50"))
            else:
                item.setForeground(QColor("#F44336"))
            self._requirements_list.addItem(item)

        # Update parameters
        # Clear existing
        while self._parameters_layout.count():
            child = self._parameters_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for param in details['parameters']:
            label = QLabel(param['name'])
            if param['type'] == 'text':
                widget = QLineEdit(param.get('default', ''))
            elif param['type'] == 'number':
                widget = QSpinBox()
                widget.setValue(param.get('default', 0))
            elif param['type'] == 'bool':
                widget = QCheckBox()
                widget.setChecked(param.get('default', False))
            elif param['type'] == 'select':
                widget = QComboBox()
                widget.addItems(param.get('options', []))
            else:
                widget = QLineEdit()

            self._parameters_layout.addRow(label, widget)

    def _get_mock_requirements(self, plugin_name):
        """Generate mock requirements for a plugin"""
        requirements_map = {
            "Data Validator": [
                {"name": "pandas", "version": ">=2.0.0", "installed": True},
                {"name": "jsonschema", "version": ">=4.0.0", "installed": True},
            ],
            "Auto Formatter": [
                {"name": "black", "version": ">=23.0.0", "installed": True},
                {"name": "isort", "version": ">=5.0.0", "installed": False},
            ],
            "Custom Exporter": [
                {"name": "openpyxl", "version": ">=3.0.0", "installed": True},
            ],
            "Debug Helper": [
                {"name": "rich", "version": ">=13.0.0", "installed": True},
                {"name": "icecream", "version": ">=2.0.0", "installed": False},
            ],
            "Theme Manager": [
                {"name": "qt-material", "version": ">=2.0.0", "installed": True},
            ],
            "PDF Generator": [
                {"name": "reportlab", "version": ">=4.0.0", "installed": True},
                {"name": "PyPDF2", "version": ">=3.0.0", "installed": True},
            ],
            "API Connector": [
                {"name": "requests", "version": ">=2.28.0", "installed": True},
                {"name": "httpx", "version": ">=0.24.0", "installed": False},
            ],
            "Report Builder": [
                {"name": "jinja2", "version": ">=3.0.0", "installed": True},
                {"name": "weasyprint", "version": ">=59.0", "installed": False},
            ],
            "Data Sync": [
                {"name": "sqlalchemy", "version": ">=2.0.0", "installed": True},
            ],
        }
        return requirements_map.get(plugin_name, [])

    def _get_mock_parameters(self, plugin_name):
        """Generate mock parameters for a plugin"""
        parameters_map = {
            "Data Validator": [
                {"name": "Strict Mode", "type": "bool", "default": True},
                {"name": "Max Errors", "type": "number", "default": 100},
                {"name": "Output Format", "type": "select", "options": ["JSON", "CSV", "HTML"]},
            ],
            "Auto Formatter": [
                {"name": "Line Length", "type": "number", "default": 88},
                {"name": "Skip Magic Trailing Comma", "type": "bool", "default": False},
            ],
            "Custom Exporter": [
                {"name": "Output Path", "type": "text", "default": "./exports"},
                {"name": "Include Headers", "type": "bool", "default": True},
            ],
            "Debug Helper": [
                {"name": "Log Level", "type": "select", "options": ["DEBUG", "INFO", "WARNING", "ERROR"]},
                {"name": "Pretty Print", "type": "bool", "default": True},
            ],
            "Theme Manager": [
                {"name": "Theme", "type": "select", "options": ["Light", "Dark", "System"]},
                {"name": "Accent Color", "type": "text", "default": "#2196F3"},
            ],
            "PDF Generator": [
                {"name": "Page Size", "type": "select", "options": ["A4", "Letter", "Legal"]},
                {"name": "Orientation", "type": "select", "options": ["Portrait", "Landscape"]},
                {"name": "Include TOC", "type": "bool", "default": False},
            ],
            "API Connector": [
                {"name": "Base URL", "type": "text", "default": "https://api.example.com"},
                {"name": "Timeout (s)", "type": "number", "default": 30},
                {"name": "Retry Count", "type": "number", "default": 3},
            ],
            "Report Builder": [
                {"name": "Template", "type": "select", "options": ["Standard", "Compact", "Detailed"]},
                {"name": "Include Charts", "type": "bool", "default": True},
            ],
            "Data Sync": [
                {"name": "Sync Interval (min)", "type": "number", "default": 15},
                {"name": "Conflict Resolution", "type": "select", "options": ["Local Wins", "Remote Wins", "Manual"]},
            ],
        }
        return parameters_map.get(plugin_name, [])

    def _test_draggable_cards(self):
        """Test draggable cards in a flowing layout"""
        from PySide6.QtCore import Qt, QMimeData, QSize
        from PySide6.QtGui import QDrag, QPixmap, QColor

        container = QWidget()
        layout = QVBoxLayout(container)

        title = QLabel("Draggable Cards - Flow Layout")
        title.setFont(QFont("Arial", 13, QFont.Bold))
        layout.addWidget(title)

        # Instructions
        instructions = QLabel("💡 Drag cards around to reorder them")
        instructions.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(instructions)

        # Scrollable area for cards
        scroll_area = QWidget()
        cards_layout = QHBoxLayout(scroll_area)
        cards_layout.setSpacing(10)
        cards_layout.setContentsMargins(10, 10, 10, 10)

        # Create draggable cards
        card_data = [
            ("📊 Analytics", "#FF6B6B", "View metrics"),
            ("⚙️ Settings", "#4ECDC4", "Configure app"),
            ("📁 Files", "#45B7D1", "Manage files"),
            ("🔍 Search", "#FFA07A", "Find data"),
            ("📧 Messages", "#98D8C8", "Communications"),
            ("👥 Users", "#F7DC6F", "Team members"),
        ]

        for title_text, color, desc in card_data:
            card = self._create_draggable_card(title_text, color, desc)
            cards_layout.addWidget(card)

        cards_layout.addStretch()

        layout.addWidget(scroll_area, 1)

        # Info
        info = QTextEdit()
        info.setReadOnly(True)
        info.setMaximumHeight(120)
        info.setText("""
DRAGGABLE CARDS FEATURES:
• Drag cards with mouse
• Reorder items freely
• Smooth visual feedback
• Click to select
• Perfect for:
  - Kanban boards
  - Dashboard customization
  - Priority management
  - Workflow design
        """)
        layout.addWidget(info)

        self._set_sandbox_content(container)

    def _create_draggable_card(self, title: str, color: str, description: str) -> QFrame:
        """Create a draggable card widget"""
        from PySide6.QtCore import Qt, QMimeData
        from PySide6.QtGui import QDrag, QPixmap

        card = DraggableCard(title, color, description)
        return card

    def _test_file_drop_zone(self):
        """Test file drop zone with dynamic box appearance"""
        container = QWidget()
        layout = QVBoxLayout(container)

        title = QLabel("File Drop Zone - Dynamic Box")
        title.setFont(QFont("Arial", 13, QFont.Bold))
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "💡 Drag files over the window to see a drop zone appear")
        instructions.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(instructions)

        # Drop zone (initially hidden)
        drop_zone = DynamicFileDropZone()
        layout.addWidget(drop_zone, 1)

        # Info
        info = QTextEdit()
        info.setReadOnly(True)
        info.setMaximumHeight(120)
        info.setText("""
DYNAMIC DROP ZONE FEATURES:
• Box appears when dragging files over window
• Box disappears when drag leaves
• Shows file count when dropped
• Visual feedback with colors
• Animated appearance/disappearance
• Perfect for:
  - File uploads
  - Document import
  - Configuration loading
  - Batch processing
        """)
        layout.addWidget(info)

        self._set_sandbox_content(container)

    def _test_document_manager(self):
        """Test three-column document management layout"""
        container = QWidget()
        layout = QVBoxLayout(container)

        title = QLabel("Document Manager - Three-Column Layout (1:4:2)")
        title.setFont(QFont("Arial", 13, QFont.Bold))
        layout.addWidget(title)

        # Main three-column layout
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)

        # Column 1: Document Library (1 unit)
        col1 = DocumentLibrary()
        main_layout.addWidget(col1, 1)

        # Column 2: Document Groups (4 units)
        col2 = DocumentGroups()
        main_layout.addWidget(col2, 4)

        # Column 3: Document Details (2 units, hidden by default)
        col3 = DocumentDetails()
        col3.setVisible(False)
        main_layout.addWidget(col3, 2)

        # Connect signals
        col1.document_selected.connect(
            lambda doc: col2.add_to_group(doc, "inbox"))
        col2.document_clicked.connect(
            lambda doc: self._show_document_details(col3, doc))
        col3.close_requested.connect(lambda: col3.setVisible(False))

        layout.addLayout(main_layout, 1)

        self._set_sandbox_content(container)

    def _show_document_details(self, panel, doc):
        """Show document details in the details panel"""
        panel.set_document(doc)
        panel.setVisible(True)


class DraggableCard(QFrame):
    """A draggable card widget with title and description"""

    def __init__(self, title: str, color: str, description: str):
        super().__init__()
        self.title_text = title
        self.color = color
        self.description = description
        self.is_selected = False

        self.setFixedSize(200, 200)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 12px;
                padding: 15px;
                border: 2px solid transparent;
            }}
            QFrame:hover {{
                border: 2px solid #333;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }}
        """)

        self.setCursor(Qt.OpenHandCursor)
        self.setAcceptDrops(True)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Arial", 10))
        desc_label.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Spacer
        layout.addStretch()

        # Drag handle indicator
        handle = QLabel("≡ Drag")
        handle.setFont(QFont("Arial", 9))
        handle.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
        layout.addWidget(handle)

    def mousePressEvent(self, event):
        """Start drag on mouse press"""
        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.pos()
            # Visual feedback
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.color};
                    border-radius: 12px;
                    padding: 15px;
                    border: 2px solid #333;
                    opacity: 0.8;
                }}
            """)

    def mouseMoveEvent(self, event):
        """Handle drag movement"""
        if event.buttons() == Qt.LeftButton:
            distance = (event.pos() - self.drag_start_pos).manhattanLength()
            if distance > 5:  # Minimum drag distance
                self._start_drag(event)

    def _start_drag(self, event):
        """Start the drag operation"""
        from PySide6.QtGui import QDrag, QPixmap, QColor

        # Create pixmap for drag image
        pixmap = QPixmap(self.size())
        pixmap.fill(QColor("transparent"))
        self.render(pixmap)

        # Create drag object
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(self.title_text)
        drag.setMimeData(mime_data)
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())

        # Execute drag
        drag.exec_(Qt.MoveAction)

        # Reset visual feedback
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.color};
                border-radius: 12px;
                padding: 15px;
                border: 2px solid transparent;
            }}
            QFrame:hover {{
                border: 2px solid #333;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }}
        """)

    def mouseReleaseEvent(self, event):
        """Reset styling on mouse release"""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.color};
                border-radius: 12px;
                padding: 15px;
                border: 2px solid transparent;
            }}
            QFrame:hover {{
                border: 2px solid #333;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }}
        """)

    def dragEnterEvent(self, event):
        """Accept drag enter events"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.color};
                    border-radius: 12px;
                    padding: 15px;
                    border: 3px solid #fff;
                    box-shadow: 0 6px 16px rgba(0,0,0,0.3);
                }}
            """)

    def dragLeaveEvent(self, event):
        """Reset on drag leave"""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.color};
                border-radius: 12px;
                padding: 15px;
                border: 2px solid transparent;
            }}
            QFrame:hover {{
                border: 2px solid #333;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }}
        """)

    def dropEvent(self, event):
        """Handle drop events"""
        if event.mimeData().hasText():
            dropped_text = event.mimeData().text()
            print(f"Dropped {dropped_text} onto {self.title_text}")
            event.acceptProposedAction()


class FileDropZone(QFrame):
    """A drop zone that shows visual feedback when files are dragged over it"""

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.is_dragging_over = False
        self.dropped_files = []

        self.setStyleSheet("""
            QFrame {
                border: 3px dashed #999;
                border-radius: 8px;
                background-color: #f9f9f9;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Main label
        self.main_label = QLabel("📁 Drag files here")
        self.main_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.main_label.setStyleSheet("color: #666;")
        self.main_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.main_label, 1)

        # File list (hidden initially)
        self.file_list = QTextEdit()
        self.file_list.setReadOnly(True)
        self.file_list.setMaximumHeight(200)
        self.file_list.setVisible(False)
        self.file_list.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                padding: 10px;
            }
        """)
        layout.addWidget(self.file_list)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #2196F3; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

        # Clear button
        self.clear_btn = QPushButton("🔄 Clear")
        self.clear_btn.clicked.connect(self.clear_files)
        self.clear_btn.setMaximumWidth(100)
        self.clear_btn.setVisible(False)
        layout.addWidget(self.clear_btn, alignment=Qt.AlignCenter)

    def dragEnterEvent(self, event):
        """Handle drag enter - show visual feedback"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.is_dragging_over = True
            self._update_drag_style(True)

    def dragLeaveEvent(self, event):
        """Handle drag leave - remove visual feedback"""
        self.is_dragging_over = False
        self._update_drag_style(False)

    def dragMoveEvent(self, event):
        """Allow drag movement"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Handle file drop"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.is_dragging_over = False
            self._update_drag_style(False)

            # Extract file paths
            urls = event.mimeData().urls()
            files = [url.toLocalFile() for url in urls]
            self._handle_files(files)

    def _update_drag_style(self, dragging: bool):
        """Update styling based on drag state"""
        if dragging:
            self.setStyleSheet("""
                QFrame {
                    border: 4px dashed #2196F3;
                    border-radius: 8px;
                    background-color: #e3f2fd;
                }
            """)
            self.main_label.setStyleSheet("color: #2196F3; font-weight: bold;")
            self.main_label.setText("📂 Drop files here!")
        else:
            self.setStyleSheet("""
                QFrame {
                    border: 3px dashed #999;
                    border-radius: 8px;
                    background-color: #f9f9f9;
                }
            """)
            self.main_label.setStyleSheet("color: #666;")
            if not self.dropped_files:
                self.main_label.setText("📁 Drag files here")

    def _handle_files(self, files: list):
        """Process dropped files"""
        self.dropped_files = files

        # Show file list
        self.main_label.setText(f"✓ {len(files)} file(s) dropped")
        self.main_label.setStyleSheet(
            "color: #4CAF50; font-weight: bold; font-size: 14pt;")

        # Build file list display
        file_text = "Dropped Files:\n" + "=" * 40 + "\n\n"
        for i, filepath in enumerate(files, 1):
            from pathlib import Path
            filename = Path(filepath).name
            file_text += f"{i}. {filename}\n   Path: {filepath}\n\n"

        self.file_list.setText(file_text)
        self.file_list.setVisible(True)
        self.status_label.setText(f"Ready to process {len(files)} file(s)")
        self.status_label.setVisible(True)
        self.clear_btn.setVisible(True)

        print(f"Files dropped: {files}")

    def clear_files(self):
        """Clear the dropped files display"""
        self.dropped_files = []
        self.main_label.setText("📁 Drag files here")
        self.main_label.setStyleSheet("color: #666;")
        self.file_list.setVisible(False)
        self.status_label.setVisible(False)
        self.clear_btn.setVisible(False)
        print("File drop zone cleared")


class DynamicFileDropZone(QFrame):
    """A drop zone that appears/disappears when files are dragged"""

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.dropped_files = []

        # Initially hidden
        self.setVisible(False)

        self.setStyleSheet("""
            QFrame {
                border: 4px dashed #2196F3;
                border-radius: 12px;
                background-color: #e3f2fd;
                padding: 30px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Main label
        self.main_label = QLabel("📂 Drop files here!")
        self.main_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.main_label.setStyleSheet("color: #2196F3;")
        self.main_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.main_label, 1)

        # File list (hidden initially)
        self.file_list = QTextEdit()
        self.file_list.setReadOnly(True)
        self.file_list.setMaximumHeight(200)
        self.file_list.setVisible(False)
        self.file_list.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                padding: 10px;
            }
        """)
        layout.addWidget(self.file_list)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(
            "color: #4CAF50; font-weight: bold; font-size: 12pt;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

        # Clear button
        self.clear_btn = QPushButton("🔄 Clear & Hide")
        self.clear_btn.clicked.connect(self.clear_and_hide)
        self.clear_btn.setMaximumWidth(120)
        self.clear_btn.setVisible(False)
        layout.addWidget(self.clear_btn, alignment=Qt.AlignCenter)

    def dragEnterEvent(self, event):
        """Handle drag enter - show the drop zone"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            if not self.isVisible():
                self.setVisible(True)

    def dragLeaveEvent(self, event):
        """Handle drag leave - hide if no files dropped"""
        if not self.dropped_files:
            self.setVisible(False)

    def dragMoveEvent(self, event):
        """Allow drag movement"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Handle file drop"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

            # Extract file paths
            urls = event.mimeData().urls()
            files = [url.toLocalFile() for url in urls]
            self._handle_files(files)

    def _handle_files(self, files: list):
        """Process dropped files"""
        self.dropped_files = files

        # Show file list
        self.main_label.setText(f"✓ {len(files)} file(s) dropped!")
        self.main_label.setStyleSheet(
            "color: #4CAF50; font-weight: bold; font-size: 18pt;")

        # Build file list display
        file_text = "Dropped Files:\n" + "=" * 40 + "\n\n"
        for i, filepath in enumerate(files, 1):
            from pathlib import Path
            filename = Path(filepath).name
            file_text += f"{i}. {filename}\n   Path: {filepath}\n\n"

        self.file_list.setText(file_text)
        self.file_list.setVisible(True)
        self.status_label.setText(f"Ready to process {len(files)} file(s)")
        self.status_label.setVisible(True)
        self.clear_btn.setVisible(True)

        print(f"Files dropped: {files}")


class DocumentLibrary(QFrame):
    """Left column: Document library with search and list"""

    document_selected = Signal(dict)

    # Sample documents
    DOCUMENTS = [
        {"id": 1, "name": "Q4 Budget.xlsx", "type": "excel", "icon": "📊"},
        {"id": 2, "name": "Project Plan.docx", "type": "word", "icon": "📝"},
        {"id": 3, "name": "Design System.figma", "type": "figma", "icon": "🎨"},
        {"id": 4, "name": "Presentation.pptx", "type": "powerpoint", "icon": "🎬"},
        {"id": 5, "name": "Report.pdf", "type": "pdf", "icon": "📄"},
        {"id": 6, "name": "README.md", "type": "markdown", "icon": "📖"},
        {"id": 7, "name": "Analysis.xlsx", "type": "excel", "icon": "📊"},
        {"id": 8, "name": "Contract.pdf", "type": "pdf", "icon": "📋"},
    ]

    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Title
        title = QLabel("Document Library")
        title.setFont(QFont("Arial", 11, QFont.Bold))
        layout.addWidget(title)

        # Add Document button
        add_btn = QPushButton("➕ Add Document")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
        """)
        layout.addWidget(add_btn)

        # Search box
        search = QLineEdit()
        search.setPlaceholderText("🔍 Search documents...")
        layout.addWidget(search)

        # Document list
        self.doc_list = QListWidget()
        self.doc_list.setStyleSheet("""
            QListWidget {
                border: none;
                outline: none;
            }
            QListWidget::item:hover {
                background-color: #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #2196F3;
            }
        """)

        for doc in self.DOCUMENTS:
            item_text = f"{doc['icon']} {doc['name']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, doc)
            self.doc_list.addItem(item)

        self.doc_list.itemClicked.connect(self._on_document_clicked)
        layout.addWidget(self.doc_list)

        # Connect search
        search.textChanged.connect(lambda text: self._filter_documents(text))

    def _filter_documents(self, text: str):
        """Filter documents by search text"""
        for i in range(self.doc_list.count()):
            item = self.doc_list.item(i)
            doc = item.data(Qt.UserRole)
            item.setHidden(text.lower() not in doc['name'].lower())

    def _on_document_clicked(self, item):
        """Emit document selected signal"""
        doc = item.data(Qt.UserRole)
        self.document_selected.emit(doc)


class DocumentGroups(QFrame):
    """Middle column: Document groups with collapsible sections"""

    document_clicked = Signal(dict)

    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #fafafa;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Title
        title = QLabel("Document Groups")
        title.setFont(QFont("Arial", 11, QFont.Bold))
        layout.addWidget(title)

        # Groups
        self.groups = {}
        group_configs = [
            ("📥 Inbox", "#FFE082"),
            ("⭐ Priority", "#EF9A9A"),
            ("👀 In Review", "#90CAF9"),
            ("✓ Completed", "#A5D6A7"),
            ("📦 Archive", "#B0BEC5"),
        ]

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(
            "QScrollArea { border: none; background-color: transparent; }")

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(8)

        for group_name, color in group_configs:
            group_widget = DocumentGroup(group_name, color)
            group_widget.document_clicked.connect(self.document_clicked.emit)
            scroll_layout.addWidget(group_widget)
            self.groups[group_name] = group_widget

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

    def add_to_group(self, doc: dict, group_name: str):
        """Add document to a group"""
        # Add to first group by default for demo
        first_group = list(self.groups.values())[0]
        first_group.add_document(doc)


class DocumentGroup(QFrame):
    """Collapsible group of documents"""

    document_clicked = Signal(dict)

    def __init__(self, name: str, color: str):
        super().__init__()
        self.name = name
        self.color = color
        self.documents = {}
        self.is_expanded = True

        self.setStyleSheet(f"""
            QFrame {{
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                padding: 5px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Header
        header = QHBoxLayout()

        # Chevron
        self.chevron_btn = QPushButton("▼")
        self.chevron_btn.setMaximumWidth(30)
        self.chevron_btn.setFlat(True)
        self.chevron_btn.clicked.connect(self._toggle_expanded)
        header.addWidget(self.chevron_btn)

        # Group name with count
        self.group_label = QLabel(name)
        self.group_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.group_label.setStyleSheet(f"color: {color};")
        header.addWidget(self.group_label)

        # Count badge
        self.count_label = QLabel("0")
        self.count_label.setStyleSheet("""
            QLabel {
                background-color: #e0e0e0;
                border-radius: 10px;
                padding: 2px 6px;
                font-weight: bold;
                font-size: 9pt;
            }
        """)
        header.addWidget(self.count_label)
        header.addStretch()

        layout.addLayout(header)

        # Grid for documents
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(8)

        self.content_widget = QWidget()
        self.content_widget.setLayout(self.grid_layout)
        layout.addWidget(self.content_widget)

    def add_document(self, doc: dict):
        """Add document to this group"""
        doc_id = doc['id']
        if doc_id not in self.documents:
            self.documents[doc_id] = doc
            self._update_grid()

    def remove_document(self, doc_id: int):
        """Remove document from this group"""
        if doc_id in self.documents:
            del self.documents[doc_id]
            self._update_grid()

    def _update_grid(self):
        """Update the document grid display"""
        # Clear existing widgets
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add documents in 3-column grid
        for i, (doc_id, doc) in enumerate(self.documents.items()):
            row = i // 3
            col = i % 3

            card = DocumentCard(doc)
            card.clicked.connect(lambda d=doc: self.document_clicked.emit(d))
            card.removed.connect(
                lambda doc_id=doc_id: self.remove_document(doc_id))

            self.grid_layout.addWidget(card, row, col)

        # Update count
        self.count_label.setText(str(len(self.documents)))

    def _toggle_expanded(self):
        """Toggle group expansion"""
        self.is_expanded = not self.is_expanded
        self.chevron_btn.setText("▼" if self.is_expanded else "▶")
        self.content_widget.setVisible(self.is_expanded)


class DocumentCard(QFrame):
    """Document card in a group"""

    clicked = Signal()
    removed = Signal()

    def __init__(self, doc: dict):
        super().__init__()
        self.doc = doc
        self.setCursor(Qt.PointingHandCursor)

        self.setStyleSheet("""
            QFrame {
                border: 1px solid #ddd;
                border-radius: 6px;
                background-color: #f9f9f9;
                padding: 8px;
            }
            QFrame:hover {
                border: 1px solid #999;
                background-color: white;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)

        # Icon and title
        title_layout = QHBoxLayout()

        icon_label = QLabel(doc['icon'])
        icon_label.setFont(QFont("Arial", 14))
        title_layout.addWidget(icon_label)

        name_label = QLabel(doc['name'])
        name_label.setFont(QFont("Arial", 9, QFont.Bold))
        name_label.setWordWrap(True)
        title_layout.addWidget(name_label, 1)

        # Remove button (hidden on hover)
        self.remove_btn = QPushButton("✕")
        self.remove_btn.setMaximumWidth(20)
        self.remove_btn.setFlat(True)
        self.remove_btn.setStyleSheet("""
            QPushButton {
                color: #999;
                border: none;
                padding: 0px;
            }
            QPushButton:hover {
                color: #d32f2f;
            }
        """)
        self.remove_btn.clicked.connect(self.removed.emit)
        title_layout.addWidget(self.remove_btn)

        layout.addLayout(title_layout)

        # Metadata
        meta_label = QLabel(f"Type: {doc['type']}")
        meta_label.setStyleSheet("color: #999; font-size: 8pt;")
        layout.addWidget(meta_label)

        # Tags
        tags_label = QLabel("📌 Sample 📋 Demo")
        tags_label.setStyleSheet("color: #2196F3; font-size: 7pt;")
        tags_label.setWordWrap(True)
        layout.addWidget(tags_label)

    def mousePressEvent(self, event):
        """Emit clicked signal"""
        self.clicked.emit()


class DocumentDetails(QFrame):
    """Right panel: Document details"""

    close_requested = Signal()

    def __init__(self):
        super().__init__()
        self.current_doc = None

        self.setStyleSheet("""
            QFrame {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header with close button
        header = QHBoxLayout()

        header_title = QLabel("Document Details")
        header_title.setFont(QFont("Arial", 11, QFont.Bold))
        header.addWidget(header_title)

        header.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setMaximumWidth(30)
        close_btn.setFlat(True)
        close_btn.clicked.connect(self.close_requested.emit)
        header.addWidget(close_btn)

        layout.addLayout(header)

        # Content
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout, 1)

    def set_document(self, doc: dict):
        """Display document details"""
        self.current_doc = doc

        # Clear previous content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Icon and name
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)

        icon = QLabel(doc['icon'])
        icon.setFont(QFont("Arial", 32))
        title_layout.addWidget(icon)

        name = QLabel(doc['name'])
        name.setFont(QFont("Arial", 12, QFont.Bold))
        name.setWordWrap(True)
        title_layout.addWidget(name, 1)

        self.content_layout.addLayout(title_layout)

        # Details
        details = [
            ("Type:", doc.get('type', 'Unknown')),
            ("Size:", "2.4 MB"),
            ("Modified:", "Nov 28, 2025"),
            ("Author:", "John Doe"),
            ("Pages:", "12"),
        ]

        for label, value in details:
            row = QHBoxLayout()
            row.setSpacing(10)

            label_widget = QLabel(label)
            label_widget.setStyleSheet("font-weight: bold; color: #666;")
            label_widget.setMaximumWidth(80)
            row.addWidget(label_widget)

            value_widget = QLabel(value)
            row.addWidget(value_widget, 1)

            self.content_layout.addLayout(row)

        # Tags
        tags_label = QLabel("Tags:")
        tags_label.setStyleSheet(
            "font-weight: bold; color: #666; margin-top: 10px;")
        self.content_layout.addWidget(tags_label)

        tags_layout = QHBoxLayout()
        for tag in ["Sample", "Demo", "Important", "Review"]:
            tag_widget = QLabel(f"• {tag}")
            tag_widget.setStyleSheet("""
                QLabel {
                    background-color: #e3f2fd;
                    padding: 4px 8px;
                    border-radius: 3px;
                    color: #2196F3;
                }
            """)
            tags_layout.addWidget(tag_widget)
        tags_layout.addStretch()
        self.content_layout.addLayout(tags_layout)

        self.content_layout.addStretch()


def main():
    """Run the layout experiment"""
    app = QApplication(sys.argv)

    # Set app style
    app.setStyle('Fusion')

    window = LayoutExperimentWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
