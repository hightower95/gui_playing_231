"""
Check Multiple View - Batch process multiple connectors from file import
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QTableView, QFrame, QDialog, QFileDialog, QComboBox,
                               QCheckBox, QScrollArea, QGridLayout, QSizePolicy, QLineEdit,
                               QHeaderView, QStyleOptionHeader, QStyle, QMenu, QTreeWidget,
                               QTreeWidgetItem, QRadioButton)
from PySide6.QtCore import Signal, Qt, QSize, QRect
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QCursor, QPainter, QColor
from app.ui.base_sub_tab_view import BaseTabView
from app.ui.components.label import StandardLabel, TextStyle
from app.ui.table_context_menu_mixin import TableContextMenuMixin
from app.core.config import UI_COLORS, UI_STYLES
from app.connector.CheckMultiple.config import SUPPORTED_FILE_EXTENSIONS, PREVIEW_ROWS, BATCH_OPERATIONS
from app.connector.Lookup.config import (
    FAMILIES, SHELL_TYPES, SHELL_SIZES, INSERT_ARRANGEMENTS,
    SOCKET_TYPES, KEYINGS, MATERIALS
)
import pandas as pd
from pathlib import Path


class ClickableHeaderView(QHeaderView):
    """Custom header view that highlights selected columns"""

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.selected_sections = set()
        self.setSectionsClickable(True)

    def paintSection(self, painter: QPainter, rect: QRect, logicalIndex: int):
        """Custom paint for header sections to show selection"""
        painter.save()

        # Draw background
        if logicalIndex in self.selected_sections:
            # Selected - use highlight color
            painter.fillRect(rect, QColor(
                UI_COLORS['section_highlight_primary']))
            text_color = QColor('white')
        else:
            # Normal - use standard background
            painter.fillRect(rect, QColor(UI_COLORS['section_background']))
            text_color = QColor(UI_COLORS['highlight_text'])

        # Draw border
        painter.setPen(QColor(UI_COLORS['frame_border']))
        painter.drawRect(rect.adjusted(0, 0, -1, -1))

        # Draw text
        painter.setPen(text_color)
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)

        # Get the text from the model
        text = self.model().headerData(logicalIndex, self.orientation(), Qt.DisplayRole)
        painter.drawText(rect, Qt.AlignCenter, str(text))

        painter.restore()


class FileUploadDialog(QDialog):
    """Dialog for drag-and-drop file upload and column selection"""

    # Signals
    # file_path, search_column, context_columns
    file_selected = Signal(str, str, list)
    # Request list of available E3 projects
    request_e3_projects_available = Signal()
    e3_projects_available = Signal(list)  # List of available E3 projects
    # Request list of available cache files
    request_e3_project_caches_available = Signal()
    e3_project_caches_available = Signal(list)  # List of available cache files

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import File")
        self.setMinimumSize(700, 500)
        self.df = None
        self.file_path = None

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # === Drop Zone ===
        self.drop_zone = QFrame()
        self.drop_zone.setFrameShape(QFrame.StyledPanel)
        self.drop_zone.setAcceptDrops(True)
        self.drop_zone.setMinimumHeight(150)
        self.drop_zone.setStyleSheet(f"""
            QFrame {{
                border: 3px dashed {UI_COLORS['section_highlight_primary']};
                border-radius: 10px;
                background-color: {UI_COLORS['section_background']};
            }}
            QFrame:hover {{
                background-color: {UI_COLORS['dark_border']};
            }}
        """)

        # Override drag/drop events
        self.drop_zone.dragEnterEvent = self._drag_enter_event
        self.drop_zone.dragMoveEvent = self._drag_move_event
        self.drop_zone.dropEvent = self._drop_event

        drop_layout = QVBoxLayout(self.drop_zone)
        drop_layout.setAlignment(Qt.AlignCenter)

        drop_label = StandardLabel(
            "📁 Drop CSV, XLSX, or TXT file here\n\nor", style=TextStyle.TITLE)
        drop_label.setAlignment(Qt.AlignCenter)

        self.browse_btn = QPushButton("Browse Files")
        self.browse_btn.setMinimumHeight(40)
        self.browse_btn.setMaximumWidth(200)
        self.browse_btn.clicked.connect(self._browse_file)
        self.browse_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {UI_COLORS['section_highlight_primary']};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {UI_COLORS['filter_pill_hover']};
            }}
        """)

        drop_layout.addWidget(drop_label)
        drop_layout.addWidget(self.browse_btn, alignment=Qt.AlignCenter)

        layout.addWidget(self.drop_zone)

        # === E3 Data Loading Section ===
        self.e3_frame = QFrame()
        self.e3_frame.setStyleSheet(f"""
            QFrame {{
                border: 1px solid {UI_COLORS['frame_border']};
                border-radius: 5px;
                background-color: {UI_COLORS['section_background']};
                padding: 10px;
            }}
        """)
        e3_layout = QVBoxLayout(self.e3_frame)

        # E3 Title
        e3_title = StandardLabel("⚡ Load E3 Data", style=TextStyle.SECTION)
        e3_layout.addWidget(e3_title)

        # E3 Options
        e3_options_layout = QVBoxLayout()
        e3_options_layout.setSpacing(10)

        # Option 1: Connect to Existing Project
        self.e3_connect_radio = QRadioButton("Connect to Existing Project")
        self.e3_connect_radio.setStyleSheet(
            f"color: {UI_COLORS['highlight_text']};")
        self.e3_connect_radio.toggled.connect(self._on_e3_option_changed)
        e3_options_layout.addWidget(self.e3_connect_radio)

        # Project selection (indented)
        project_container = QWidget()
        project_layout = QVBoxLayout(project_container)
        project_layout.setContentsMargins(30, 0, 0, 10)

        project_label = StandardLabel(
            "Select Projects:", style=TextStyle.LABEL)
        project_layout.addWidget(project_label)

        # Use multiselect for projects
        from app.ui.dual_column_multiselect import DualColumnMultiselect
        self.e3_project_multiselect = DualColumnMultiselect([
            "Project_Alpha_Rev3",
            "Project_Beta_Final",
            "Connector_Library_Master",
            "System_Integration_2024",
            "Prototype_Assembly_v2"
        ])
        self.e3_project_multiselect.setEnabled(False)
        self.e3_project_multiselect.setMaximumHeight(150)
        project_layout.addWidget(self.e3_project_multiselect)

        e3_options_layout.addWidget(project_container)

        # Warning label
        self.e3_warning_label = StandardLabel(
            "⚠️ This operation can take several minutes", style=TextStyle.NOTES)
        self.e3_warning_label.setVisible(False)
        e3_options_layout.addWidget(self.e3_warning_label)

        # Option 2: Load from Cache
        self.e3_cache_radio = QRadioButton("Load from Cache")
        self.e3_cache_radio.setStyleSheet(
            f"color: {UI_COLORS['highlight_text']};")
        self.e3_cache_radio.toggled.connect(self._on_e3_option_changed)
        e3_options_layout.addWidget(self.e3_cache_radio)

        # Cache file selection (indented)
        cache_container = QWidget()
        cache_layout = QHBoxLayout(cache_container)
        cache_layout.setContentsMargins(30, 0, 0, 0)

        cache_label = StandardLabel("Cache File:", style=TextStyle.LABEL)

        self.e3_cache_path = QLineEdit()
        self.e3_cache_path.setEnabled(False)
        self.e3_cache_path.setPlaceholderText(
            "e3_connector_cache_2024-10-16.csv")
        self.e3_cache_path.setText(
            "e3_connector_cache_2024-10-16.csv")  # Suggested file
        self.e3_cache_path.setMinimumWidth(300)

        cache_browse_btn = QPushButton("Browse...")
        cache_browse_btn.setEnabled(False)
        cache_browse_btn.clicked.connect(self._browse_cache_file)
        self.cache_browse_btn = cache_browse_btn

        cache_layout.addWidget(cache_label)
        cache_layout.addWidget(self.e3_cache_path)
        cache_layout.addWidget(cache_browse_btn)
        cache_layout.addStretch()

        e3_options_layout.addWidget(cache_container)

        # Load E3 Button
        e3_button_layout = QHBoxLayout()
        self.load_e3_btn = QPushButton("📥 Load E3 Data")
        self.load_e3_btn.setEnabled(False)
        self.load_e3_btn.setMinimumHeight(35)
        self.load_e3_btn.setMinimumWidth(150)
        self.load_e3_btn.clicked.connect(self._load_e3_data)
        self.load_e3_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {UI_COLORS['section_highlight_primary']};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
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
        e3_button_layout.addStretch()
        e3_button_layout.addWidget(self.load_e3_btn)

        e3_layout.addLayout(e3_options_layout)
        e3_layout.addLayout(e3_button_layout)

        layout.addWidget(self.e3_frame)

        # === File Info ===
        self.file_info_label = StandardLabel("", style=TextStyle.LABEL)
        self.file_info_label.setVisible(False)
        layout.addWidget(self.file_info_label)

        # === Column Selection Area ===
        self.column_selection_frame = QFrame()
        self.column_selection_frame.setVisible(False)
        column_layout = QVBoxLayout(self.column_selection_frame)

        # Search column selection
        search_row = QHBoxLayout()
        search_label = StandardLabel("Search Column:", style=TextStyle.LABEL)
        self.search_column_combo = QComboBox()
        self.search_column_combo.setMinimumWidth(200)
        search_row.addWidget(search_label)
        search_row.addWidget(self.search_column_combo)
        search_row.addStretch()
        column_layout.addLayout(search_row)

        # Context columns selection - will be shown after preview
        context_label = StandardLabel(
            "Additional Context Columns (optional): Click column headers below to select",
            style=TextStyle.LABEL)
        context_label.setVisible(False)
        self.context_label = context_label
        column_layout.addWidget(context_label)

        # Selected context columns display
        self.selected_context_label = StandardLabel(
            "Selected: None", style=TextStyle.NOTES)
        self.selected_context_label.setVisible(False)
        column_layout.addWidget(self.selected_context_label)

        layout.addWidget(self.column_selection_frame)

        # Track selected context columns
        self.selected_context_columns = set()

        # === Preview Area ===
        preview_label = StandardLabel(
            f"Preview (first {PREVIEW_ROWS} rows):", style=TextStyle.LABEL)
        preview_label.setVisible(False)
        self.preview_label = preview_label
        layout.addWidget(preview_label)

        self.preview_table = QTableView()
        self.preview_table.setVisible(False)
        # Increased from 200 for better visibility
        self.preview_table.setMinimumHeight(250)
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setSelectionMode(
            QTableView.NoSelection)  # Disable row selection
        self.preview_table.verticalHeader().setVisible(False)  # Hide row numbers

        # Use custom clickable header
        self.custom_header = ClickableHeaderView(
            Qt.Horizontal, self.preview_table)
        self.preview_table.setHorizontalHeader(self.custom_header)
        self.custom_header.sectionClicked.connect(
            self._on_column_header_clicked)

        layout.addWidget(self.preview_table)

        # === Buttons ===
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumSize(100, 35)
        self.cancel_btn.clicked.connect(self.reject)

        self.ok_btn = QPushButton("Import")
        self.ok_btn.setMinimumSize(100, 35)
        self.ok_btn.setEnabled(False)
        self.ok_btn.clicked.connect(self._on_import)
        self.ok_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {UI_COLORS['section_highlight_primary']};
                color: white;
                border: none;
                border-radius: 3px;
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

        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.ok_btn)

        layout.addLayout(button_layout)

    def _drag_enter_event(self, event: QDragEnterEvent):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def _drag_move_event(self, event):
        """Handle drag move event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def _drop_event(self, event: QDropEvent):
        """Handle file drop event"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self._load_file(file_path)
            event.acceptProposedAction()

    def _browse_file(self):
        """Open file browser dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File",
            "",
            "Supported Files (*.csv *.xlsx *.txt);;CSV Files (*.csv);;Excel Files (*.xlsx);;Text Files (*.txt)"
        )
        if file_path:
            self._load_file(file_path)

    def _load_file(self, file_path: str):
        """Load and preview file"""
        path = Path(file_path)

        # Validate file extension
        if path.suffix.lower() not in SUPPORTED_FILE_EXTENSIONS:
            self.file_info_label.setText(
                f"❌ Unsupported file type: {path.suffix}")
            self.file_info_label.setStyleSheet(
                f"color: red; font-weight: bold;")
            self.file_info_label.setVisible(True)
            return

        try:
            # Load file based on extension
            if path.suffix.lower() == '.csv':
                self.df = pd.read_csv(file_path)
            elif path.suffix.lower() == '.xlsx':
                self.df = pd.read_excel(file_path)
            elif path.suffix.lower() == '.txt':
                # Try to detect delimiter
                self.df = pd.read_csv(file_path, sep=None, engine='python')

            self.file_path = file_path

            # Hide E3 loading section once file is loaded
            self.e3_frame.setVisible(False)

            # Update UI
            self.file_info_label.setText(
                f"✓ Loaded: {path.name} ({len(self.df)} rows, {len(self.df.columns)} columns)")
            self.file_info_label.setStyleSheet(
                f"color: {UI_COLORS['section_highlight_primary']}; font-weight: bold;")
            self.file_info_label.setVisible(True)

            # Populate column selectors
            self._populate_column_selectors()

            # Show preview
            self._show_preview()

            # Enable OK button
            self.ok_btn.setEnabled(True)

        except Exception as e:
            self.file_info_label.setText(f"❌ Error loading file: {str(e)}")
            self.file_info_label.setStyleSheet(
                f"color: red; font-weight: bold;")
            self.file_info_label.setVisible(True)

    def _populate_column_selectors(self):
        """Populate column selection dropdowns"""
        columns = list(self.df.columns)

        # Populate search column combo
        self.search_column_combo.clear()
        self.search_column_combo.addItems(columns)

        # Auto-detect and select column containing "Part Number" (case-insensitive)
        part_number_col = None
        for col in columns:
            if "part number" in col.lower():
                part_number_col = col
                break

        if part_number_col:
            index = columns.index(part_number_col)
            self.search_column_combo.setCurrentIndex(index)

        # Clear selected context columns
        self.selected_context_columns.clear()

        self.column_selection_frame.setVisible(True)

    def _show_preview(self):
        """Show preview of loaded data"""
        from app.presenters.pandas_table_model import PandasTableModel

        # Show first N rows
        preview_df = self.df.head(PREVIEW_ROWS)

        # Create table model
        model = PandasTableModel(preview_df)
        self.preview_table.setModel(model)

        # Show context selection instruction
        self.context_label.setVisible(True)
        self.selected_context_label.setVisible(True)

        self.preview_label.setVisible(True)
        self.preview_table.setVisible(True)

    def _on_column_header_clicked(self, logical_index: int):
        """Handle column header click to select/deselect context columns"""
        if self.df is None:
            return

        column_name = self.df.columns[logical_index]

        # Toggle selection
        if column_name in self.selected_context_columns:
            self.selected_context_columns.remove(column_name)
            self.custom_header.selected_sections.discard(logical_index)
        else:
            self.selected_context_columns.add(column_name)
            self.custom_header.selected_sections.add(logical_index)

        # Update display
        self._update_selected_context_display()

        # Repaint the header to show updated selection
        self.custom_header.viewport().update()

    def _update_selected_context_display(self):
        """Update the label showing selected context columns"""
        if not self.selected_context_columns:
            self.selected_context_label.setText("Selected: None")
            self.selected_context_label.setStyleSheet(
                f"color: {UI_COLORS['muted_text']}; margin-left: 20px; font-style: italic;")
        else:
            columns_text = ", ".join(sorted(self.selected_context_columns))
            self.selected_context_label.setText(f"Selected: {columns_text}")
            self.selected_context_label.setStyleSheet(
                f"color: {UI_COLORS['section_highlight_primary']}; margin-left: 20px; font-weight: bold;")

    def _on_import(self):
        """Handle import button click"""
        search_column = self.search_column_combo.currentText()

        # Get context columns from the selected set, excluding search column
        context_columns = [
            col for col in self.selected_context_columns if col != search_column]
        print(
            f"DEBUG FILE_UPLOAD: _on_import called with search_column: {search_column}, context_columns: {context_columns}")
        self.file_selected.emit(self.file_path, search_column, context_columns)
        self.accept()

    def _on_e3_option_changed(self):
        """Handle E3 data source option change"""
        if self.e3_connect_radio.isChecked():
            # Enable project selection
            self.e3_project_multiselect.setEnabled(True)
            self.e3_warning_label.setVisible(True)
            # Disable cache selection
            self.e3_cache_path.setEnabled(False)
            self.cache_browse_btn.setEnabled(False)
            # Enable load button
            self.load_e3_btn.setEnabled(True)
            # Request available projects
            self.request_e3_projects_available.emit()
        elif self.e3_cache_radio.isChecked():
            # Disable project selection
            self.e3_project_multiselect.setEnabled(False)
            self.e3_warning_label.setVisible(False)
            # Enable cache selection
            self.e3_cache_path.setEnabled(True)
            self.cache_browse_btn.setEnabled(True)
            # Enable load button
            self.load_e3_btn.setEnabled(True)
            # Request available cache files
            self.request_e3_project_caches_available.emit()
        else:
            # No option selected
            self.e3_project_multiselect.setEnabled(False)
            self.e3_warning_label.setVisible(False)
            self.e3_cache_path.setEnabled(False)
            self.cache_browse_btn.setEnabled(False)
            self.load_e3_btn.setEnabled(False)

    def _browse_cache_file(self):
        """Browse for cache file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select E3 Cache File",
            "",
            "CSV Files (*.csv);;All Files (*.*)"
        )
        if file_path:
            self.e3_cache_path.setText(file_path)

    def populate_e3_projects(self, projects: list):
        """Populate the E3 projects multiselect with available projects

        Args:
            projects: List of project names
        """
        print(f"DEBUG: Populating E3 projects: {projects}")
        # Clear current items and add new ones
        self.e3_project_multiselect.clear_selection()
        # TODO: Would need to enhance DualColumnMultiselect to support updating items dynamically
        # For now, projects are hardcoded in the widget creation

    def populate_e3_caches(self, caches: list):
        """Populate the E3 cache file suggestions

        Args:
            caches: List of cache file paths
        """
        print(f"DEBUG: Populating E3 caches: {caches}")
        if caches:
            # Set the first cache as the suggested file
            self.e3_cache_path.setText(caches[0])

    def _load_e3_data(self):
        """Load E3 data from selected source"""
        if self.e3_connect_radio.isChecked():
            # Connect to E3 project(s)
            selected_projects = self.e3_project_multiselect.get_selected_items()
            if not selected_projects:
                self.file_info_label.setText(
                    "⚠️ Please select at least one project")
                self.file_info_label.setStyleSheet(
                    f"color: orange; font-weight: bold;")
                self.file_info_label.setVisible(True)
                return

            project_names = ", ".join(selected_projects)
            print(f"DEBUG: Loading E3 data from projects: {selected_projects}")

            # Show loading message
            self.file_info_label.setText(
                f"⏳ Connecting to E3 project(s) '{project_names}'... This may take several minutes.")
            self.file_info_label.setStyleSheet(
                f"color: {UI_COLORS['highlight_text']}; font-weight: bold;")
            self.file_info_label.setVisible(True)

            # TODO: Implement actual E3 connection
            # For now, show a message
            self.file_info_label.setText(
                f"⚠️ E3 connection not yet implemented. Please use cache file.")
            self.file_info_label.setStyleSheet(
                f"color: orange; font-weight: bold;")

        elif self.e3_cache_radio.isChecked():
            # Load from cache file
            cache_file = self.e3_cache_path.text()
            print(f"DEBUG: Loading E3 data from cache: {cache_file}")

            # Load the cache file as if it's a normal file
            self._load_file(cache_file)


class FilterDialog(QDialog):
    """Dialog for selecting filter parameters for Find Alternatives and Find Opposites"""

    def __init__(self, parent=None, operation_type='find_alternatives'):
        super().__init__(parent)
        self.operation_type = operation_type
        self.setWindowTitle("Filter Parameters")
        self.setMinimumSize(500, 400)
        self.selected_filters = {}

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Title
        if self.operation_type == 'find_alternatives':
            title_text = "Select filters to apply to alternative search:"
        else:
            title_text = "Select filters to apply to opposite search:"

        title = StandardLabel(title_text, style=TextStyle.SECTION)
        layout.addWidget(title)

        # Scrollable filter area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"border: 1px solid {UI_COLORS['frame_border']};")

        filter_widget = QWidget()
        filter_layout = QVBoxLayout(filter_widget)

        # Create filter selectors
        self.filter_combos = {}

        filters = [
            ('Shell Type', SHELL_TYPES),
            ('Material', MATERIALS),
            ('Shell Size', SHELL_SIZES),
            ('Insert Arrangement', INSERT_ARRANGEMENTS),
            ('Socket Type', SOCKET_TYPES),
            ('Keying', KEYINGS)
        ]

        # Define which fields are locked and which default to "Same"
        if self.operation_type == 'find_alternatives':
            locked_fields = ['shell_size', 'insert_arrangement']
            same_default_fields = ['keying', 'socket_type', 'shell_type']
        else:  # find_opposites
            locked_fields = ['keying', 'insert_arrangement']
            same_default_fields = []  # None default to "Same" for opposites

        for filter_name, filter_options in filters:
            row = QHBoxLayout()

            label = StandardLabel(f"{filter_name}:", style=TextStyle.LABEL)
            label.setMinimumWidth(150)

            filter_key = filter_name.lower().replace(' ', '_')

            combo = QComboBox()

            # Check if this field should be locked
            if filter_key in locked_fields:
                combo.addItem("Same")
                combo.setEnabled(False)
                combo.setStyleSheet(f"""
                    QComboBox {{
                        background-color: {UI_COLORS['section_background']};
                        color: {UI_COLORS['muted_text']};
                    }}
                """)
            else:
                # Set default value based on field type
                if filter_key in same_default_fields:
                    combo.addItem("Same")  # Default option
                    combo.addItem("Any")   # Second option
                    combo.addItems(filter_options)
                else:
                    combo.addItem("Any")   # Default option for others
                    combo.addItem("Same")  # Second option
                    combo.addItems(filter_options)

            combo.setMinimumWidth(200)
            self.filter_combos[filter_key] = combo

            row.addWidget(label)
            row.addWidget(combo)
            row.addStretch()

            filter_layout.addLayout(row)

        scroll.setWidget(filter_widget)
        layout.addWidget(scroll)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumSize(100, 35)
        cancel_btn.clicked.connect(self.reject)

        ok_btn = QPushButton("Apply")
        ok_btn.setMinimumSize(100, 35)
        ok_btn.clicked.connect(self._on_apply)
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {UI_COLORS['section_highlight_primary']};
                color: white;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {UI_COLORS['filter_pill_hover']};
            }}
        """)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

    def _on_apply(self):
        """Collect selected filters"""
        for key, combo in self.filter_combos.items():
            value = combo.currentText()
            # Include all non-"Any" values (including "Same")
            if value not in ["Any"]:
                self.selected_filters[key] = value

        self.accept()

    def get_filters(self) -> dict:
        """Return selected filters"""
        return self.selected_filters


class CheckMultipleConnectorView(BaseTabView, TableContextMenuMixin):
    """View for batch checking multiple connectors from file import"""

    # Signals
    # file_path, search_column, context_columns
    file_imported = Signal(str, str, list)
    operation_requested = Signal(str, dict)  # operation_type, filters
    export_requested = Signal()
    clear_results_requested = Signal()
    remove_data_requested = Signal()
    to_lookup_requested = Signal(list)  # list of search terms to lookup
    filter_requested = Signal()  # Show filter dialog
    group_by_requested = Signal(str)  # group_by_field
    # Emitted when FileUploadDialog is shown
    file_dialog_shown = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.imported_data = None
        self.original_imported_data = None  # Store the original imported data
        self.search_column = None
        self.context_columns = []
        self.current_grouping = None  # Track current grouping field

        self._setup_ui_content()

    def _setup_ui_content(self):
        """Setup the main UI content"""
        # Update header frame
        self.header_frame.setFixedHeight(120)

        header_layout = QVBoxLayout(self.header_frame)
        header_layout.setContentsMargins(10, 10, 10, 10)

        # Title row
        title_row = QHBoxLayout()
        title_label = StandardLabel("Check Multiple", style=TextStyle.TITLE)
        title_row.addWidget(title_label)
        title_row.addStretch()
        title_row.addWidget(self.help_label)

        header_layout.addLayout(title_row)

        # Add Parts button row
        button_row = QHBoxLayout()
        self.add_parts_btn = QPushButton("📁 Add Parts")
        self.add_parts_btn.setMinimumHeight(40)
        self.add_parts_btn.setMaximumWidth(200)
        self.add_parts_btn.clicked.connect(self._on_add_parts)
        self.add_parts_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {UI_COLORS['section_highlight_primary']};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: {UI_COLORS['filter_pill_hover']};
            }}
        """)

        self.clear_results_btn = QPushButton("🔄 Reset Results")
        self.clear_results_btn.setMinimumHeight(40)
        self.clear_results_btn.setMaximumWidth(180)
        self.clear_results_btn.setEnabled(False)
        self.clear_results_btn.clicked.connect(self._on_clear_results)
        self.clear_results_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {UI_COLORS['section_highlight_primary']};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: {UI_COLORS['filter_pill_hover']};
            }}
            QPushButton:disabled {{
                background-color: {UI_COLORS['section_background']};
                color: {UI_COLORS['muted_text']};
            }}
        """)

        self.remove_data_btn = QPushButton("🗑️ Remove Data")
        self.remove_data_btn.setMinimumHeight(40)
        self.remove_data_btn.setMaximumWidth(180)
        self.remove_data_btn.setEnabled(False)
        self.remove_data_btn.clicked.connect(self._on_remove_data)
        self.remove_data_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #d32f2f;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: #b71c1c;
            }}
            QPushButton:disabled {{
                background-color: {UI_COLORS['section_background']};
                color: {UI_COLORS['muted_text']};
            }}
        """)

        self.file_status_label = StandardLabel(
            "No file imported", style=TextStyle.STATUS)

        button_row.addWidget(self.add_parts_btn)
        button_row.addWidget(self.clear_results_btn)
        button_row.addWidget(self.remove_data_btn)
        button_row.addWidget(self.file_status_label)
        button_row.addStretch()

        header_layout.addLayout(button_row)

        # Setup context area with operation buttons
        self._setup_operation_buttons()

        # Setup results table
        self._setup_results_table()

        # Setup enhanced context area
        self._setup_enhanced_context_area()

        # Setup context menu (must be after table is created)
        self._setup_context_menu()

        # Setup footer with export button
        self._setup_footer_controls()

    def _setup_operation_buttons(self):
        """Setup operation buttons in context area"""
        # Clear default context box
        self.context_box.setVisible(False)

        # Get context frame
        context_frame = self.context_box.parent()
        context_layout = context_frame.layout()

        # Remove context box
        context_layout.removeWidget(self.context_box)

        # Create new container
        operations_container = QWidget()
        operations_layout = QVBoxLayout(operations_container)
        operations_layout.setContentsMargins(10, 10, 10, 10)

        # Title
        ops_title = StandardLabel("Batch Operations", style=TextStyle.SECTION)
        operations_layout.addWidget(ops_title)

        # 2-column grid of buttons
        grid = QGridLayout()
        grid.setSpacing(10)

        operations = [
            ('Find Opposites', 'find_opposites'),
            ('Find Alternatives', 'find_alternatives'),
            ('Get Details', 'lookup'),
            ('Get Material', 'get_material'),
            ('Check Status', 'check_status'),
            ('To Lookup', 'to_lookup'),
            ('Filter', 'filter'),
            ('Group By', 'group_by'),  # New Group By button
        ]

        self.operation_buttons = {}

        for idx, (name, op_type) in enumerate(operations):
            if not name:
                continue

            row = idx // 2
            col = idx % 2

            btn = QPushButton(name)
            btn.setMinimumHeight(45)
            btn.setEnabled(False)  # Disabled until file imported

            # Special handling for Group By button with menu
            if op_type == 'group_by':
                # Create menu for Group By options
                group_menu = QMenu(btn)
                group_menu.setStyleSheet(f"""
                    QMenu {{
                        background-color: {UI_COLORS['section_background']};
                        color: {UI_COLORS['highlight_text']};
                        border: 1px solid {UI_COLORS['frame_border']};
                    }}
                    QMenu::item:selected {{
                        background-color: {UI_COLORS['section_highlight_primary']};
                    }}
                """)

                group_options = [
                    ('Material', 'Material'),
                    ('Part Code', 'Part Code'),
                    ('Minified Part Code', 'Minified Part Code'),
                    ('Keying', 'Keying'),
                    ('Insert Arrangement', 'Insert Arrangement'),
                ]

                for option_label, option_field in group_options:
                    action = group_menu.addAction(option_label)
                    action.triggered.connect(
                        lambda checked, field=option_field: self._on_group_by_selected(field))

                btn.setMenu(group_menu)
            else:
                btn.clicked.connect(
                    lambda checked, ot=op_type: self._on_operation_clicked(ot))

            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {UI_COLORS['section_highlight_primary']};
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px;
                    font-weight: bold;
                    font-size: 10pt;
                }}
                QPushButton:hover {{
                    background-color: {UI_COLORS['filter_pill_hover']};
                }}
                QPushButton:disabled {{
                    background-color: {UI_COLORS['section_background']};
                    color: {UI_COLORS['muted_text']};
                }}
                QPushButton::menu-indicator {{
                    width: 0px;  /* Hide the default menu arrow */
                }}
            """)

            grid.addWidget(btn, row, col)
            self.operation_buttons[op_type] = btn

        operations_layout.addLayout(grid)
        operations_layout.addStretch()

        context_layout.addWidget(operations_container)

    def _setup_results_table(self):
        """Setup results table in left content area"""
        self.results_layout = QVBoxLayout(self.left_content_frame)
        self.results_layout.setContentsMargins(0, 0, 0, 0)

        # Create both table view (for normal results) and tree widget (for grouped results)
        self.results_table = QTableView()
        self.results_table.setSortingEnabled(True)
        self.results_table.setSelectionBehavior(QTableView.SelectRows)
        self.results_table.setSelectionMode(QTableView.ExtendedSelection)
        self.results_table.setAlternatingRowColors(True)

        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderHidden(False)
        self.results_tree.setAlternatingRowColors(True)
        self.results_tree.setVisible(False)  # Hidden by default

        self.results_layout.addWidget(self.results_table)
        self.results_layout.addWidget(self.results_tree)

        self.record_count_label.setText("No data loaded")

    def _setup_context_menu(self):
        """Setup right-click context menu for the table"""
        custom_actions = [
            {
                'text': '🔍 To Lookup',
                'callback': self._context_menu_to_lookup,
                'icon': None
            }
        ]

        self.setup_table_context_menu(
            self.results_table,
            actions=custom_actions,
            include_copy_row=True
        )

    def _context_menu_to_lookup(self):
        """Handle 'To Lookup' from context menu - extract Part Numbers from selected rows"""
        selected_rows = self.results_table.selectionModel().selectedRows()

        if not selected_rows:
            return

        model = self.results_table.model()
        if not model:
            return

        # Find the Part Number column
        part_number_col = None
        for col in range(model.columnCount()):
            header = model.headerData(col, Qt.Horizontal, Qt.DisplayRole)
            if 'part number' in header.lower():
                part_number_col = col
                break

        if part_number_col is None:
            print("DEBUG: Part Number column not found in results")

            return

        # Extract Part Numbers from selected rows
        part_numbers = []
        for row_index in selected_rows:
            row = row_index.row()
            part_number = model.data(model.index(
                row, part_number_col), Qt.DisplayRole)
            if part_number and str(part_number).strip() and str(part_number) != 'nan':
                part_numbers.append(str(part_number))

        if not part_numbers:
            print("DEBUG: No valid Part Numbers found in selected rows")
            return

        print(
            f"DEBUG: Context menu - emitting to_lookup_requested with {len(part_numbers)} part numbers")

        # Emit signal with list of part numbers
        # This will be handled by presenter just like the button click
        self.to_lookup_requested.emit(part_numbers)

    def _setup_enhanced_context_area(self):
        """Setup enhanced context area to show selected row details"""
        # The context_box already exists from BaseTabView
        # Just update its styling and make sure it's visible
        self.context_box.setStyleSheet(f"""
            QTextEdit {{
                background-color: {UI_COLORS['section_background']};
                border: 1px solid {UI_COLORS['frame_border']};
                border-radius: 5px;
                padding: 10px;
                color: {UI_COLORS['highlight_text']};
                font-size: 10pt;
            }}
        """)
        self.context_box.setPlaceholderText("Select a row to view details...")

    def _on_selection_changed(self):
        """Update context area when selection changes"""
        selected_rows = self.results_table.selectionModel().selectedRows()

        if not selected_rows:
            self.context_box.clear()
            self.context_box.setPlaceholderText(
                "Select a row to view details...")
            return

        # Show details for first selected row
        row = selected_rows[0].row()
        model = self.results_table.model()

        if not model:
            return

        # Build context text
        context_text = "<h3>Selected Row Details</h3><table>"

        for col in range(model.columnCount()):
            header = model.headerData(col, Qt.Horizontal, Qt.DisplayRole)
            value = model.data(model.index(row, col), Qt.DisplayRole)

            if value is not None and str(value).strip():
                context_text += f"<tr><td style='font-weight: bold; padding-right: 10px;'>{header}:</td><td>{value}</td></tr>"

        context_text += "</table>"

        if len(selected_rows) > 1:
            context_text += f"<p style='margin-top: 10px; font-style: italic;'>({len(selected_rows)} rows selected)</p>"

        self.context_box.setHtml(context_text)

    def _setup_footer_controls(self):
        """Setup footer with export button"""
        # Clear default footer
        if self.footer_box.layout():
            QWidget().setLayout(self.footer_box.layout())

        footer_layout = QHBoxLayout(self.footer_box)
        footer_layout.setContentsMargins(10, 5, 10, 5)

        footer_layout.addStretch()

        self.export_btn = QPushButton("📊 Export Results")
        self.export_btn.setMinimumHeight(35)
        self.export_btn.setMinimumWidth(150)
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(lambda: self.export_requested.emit())
        self.export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {UI_COLORS['section_highlight_primary']};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
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

        footer_layout.addWidget(self.export_btn)

    def _on_add_parts(self):
        """Show file upload dialog"""
        dialog = FileUploadDialog(self)
        dialog.file_selected.connect(self._on_file_imported)

        # Emit signal so presenter can connect E3 signals
        self.file_dialog_shown.emit(dialog)

        dialog.exec()

    def _on_file_imported(self, file_path: str, search_column: str, context_columns: list):
        """Handle file import"""
        self.search_column = search_column
        self.context_columns = context_columns

        # Update status
        file_name = Path(file_path).name
        self.file_status_label.setText(
            f"✓ {file_name} - Column: {search_column}")
        self.file_status_label.setStyleSheet(
            f"color: {UI_COLORS['section_highlight_primary']}; font-weight: bold;")

        # Enable operation buttons and data management buttons
        for btn in self.operation_buttons.values():
            btn.setEnabled(True)
        self.clear_results_btn.setEnabled(True)
        self.remove_data_btn.setEnabled(True)

        # Emit signal
        self.file_imported.emit(file_path, search_column, context_columns)

    def _on_operation_clicked(self, operation_type: str):
        """Handle operation button click"""
        filters = {}

        # Handle "To Lookup" operation
        if operation_type == 'to_lookup':
            self._handle_to_lookup()
            return

        # Handle "Filter" operation
        if operation_type == 'filter':
            self._handle_filter()
            return

        # If Find Alternatives or Find Opposites, show filter dialog
        if operation_type in ['find_alternatives', 'find_opposites']:
            dialog = FilterDialog(self, operation_type=operation_type)
            if dialog.exec() == QDialog.Accepted:
                filters = dialog.get_filters()
            else:
                return  # User cancelled

        # Emit operation request
        self.operation_requested.emit(operation_type, filters)

    def _handle_to_lookup(self):
        """Handle 'To Lookup' operation - extract search terms and emit for lookup"""
        print("DEBUG: _handle_to_lookup called")

        if self.imported_data is None or self.imported_data.empty:
            print("DEBUG: No imported data")
            return

        # Get the search column - it has been prefixed with "Input: " in the presenter
        # Try both the original name and the prefixed version
        search_col = None

        # First try the prefixed version (most likely after import)
        prefixed_col = f"Input: {self.search_column}"
        if prefixed_col in self.imported_data.columns:
            search_col = prefixed_col
        # Fallback to original name
        elif self.search_column in self.imported_data.columns:
            search_col = self.search_column

        if not search_col:
            print(
                f"DEBUG: Search column not found - search_column={self.search_column}, columns={self.imported_data.columns.tolist()}")
            return

        print(f"DEBUG: Using column: {search_col}")

        # Extract unique search terms (these might not be part numbers yet)
        search_terms = self.imported_data[search_col].dropna(
        ).unique().tolist()

        if not search_terms:
            print("DEBUG: No search terms found")
            return

        print(
            f"DEBUG: Emitting to_lookup_requested with {len(search_terms)} search terms")

        # Emit signal with list of search terms - presenter will do the lookup
        # and then extract the actual Part Numbers
        self.to_lookup_requested.emit(search_terms)

    def _handle_filter(self):
        """Handle 'Filter' operation - show filter dialog and apply to current results"""
        if self.imported_data is None or self.imported_data.empty:
            return

        # Show filter dialog (similar to Lookup filters)
        from app.connector.CheckMultiple.view import CheckMultipleFilterDialog

        dialog = CheckMultipleFilterDialog(self)
        if dialog.exec() == QDialog.Accepted:
            filters = dialog.get_filters()
            # Apply filters to current data
            self._apply_filters(filters)

    def _apply_filters(self, filters: dict):
        """Apply filter criteria to current results"""
        if self.imported_data is None or self.imported_data.empty:
            return

        filtered_df = self.imported_data.copy()

        # Apply each filter
        for key, values in filters.items():
            if not values or values == ['Any']:
                continue

            # Map filter keys to column names
            column_mapping = {
                'standard': 'Family',
                'shell_type': 'Shell Type',
                'material': 'Material',
                'shell_size': 'Shell Size',
                'insert_arrangement': 'Insert Arrangement',
                'socket_type': 'Socket Type',
                'keying': 'Keying'
            }

            column_name = column_mapping.get(key)
            if column_name and column_name in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[column_name].isin(
                    values)]

        # Update display
        self.update_results(filtered_df, is_original_import=False)
        self.record_count_label.setText(
            f"Showing {len(filtered_df)} of {len(self.imported_data)} results (filtered)")

    def _on_group_by_selected(self, field: str):
        """Handle group by field selection"""
        print(f"DEBUG: Group by selected: {field}")

        if self.imported_data is None or self.imported_data.empty:
            return

        # Emit signal to trigger grouping
        self.group_by_requested.emit(field)

    def update_results(self, results_df: pd.DataFrame, is_original_import: bool = False):
        """Update results table with data"""
        from app.presenters.pandas_table_model import PandasTableModel

        self.imported_data = results_df

        # Store original data if this is the initial import
        if is_original_import:
            self.original_imported_data = results_df.copy()
            self.current_grouping = None  # Reset grouping on new import

        # Show table view, hide tree view
        self.results_table.setVisible(True)
        self.results_tree.setVisible(False)

        model = PandasTableModel(results_df)
        self.results_table.setModel(model)

        # Connect selection model signal after model is set
        if self.results_table.selectionModel():
            self.results_table.selectionModel().selectionChanged.connect(
                self._on_selection_changed)

        # Update status
        self.record_count_label.setText(f"Showing {len(results_df)} results")

        # Enable export
        self.export_btn.setEnabled(True)

    def update_grouped_results(self, results_df: pd.DataFrame, group_by_field: str):
        """Update results with grouped/collapsible display

        Args:
            results_df: DataFrame with results
            group_by_field: Field name to group by
        """
        self.imported_data = results_df
        self.current_grouping = group_by_field

        # Show tree view, hide table view
        self.results_table.setVisible(False)
        self.results_tree.setVisible(True)

        # Clear existing tree
        self.results_tree.clear()

        # Set up headers from DataFrame columns
        headers = list(results_df.columns)
        self.results_tree.setHeaderLabels(headers)

        # Check if group field exists
        if group_by_field not in results_df.columns:
            self.record_count_label.setText(
                f"Error: '{group_by_field}' column not found")
            return

        # Group data and sort by group size (descending)
        grouped = results_df.groupby(group_by_field)
        group_sizes = grouped.size().sort_values(ascending=False)

        total_rows = 0

        # Create tree items for each group
        for group_value in group_sizes.index:
            group_df = grouped.get_group(group_value)
            group_size = len(group_df)
            total_rows += group_size

            # Create parent item for the group
            group_label = f"{group_by_field}: {group_value} ({group_size})"
            parent_item = QTreeWidgetItem([group_label])
            parent_item.setExpanded(False)  # Collapsed by default

            # Style the parent item
            font = parent_item.font(0)
            font.setBold(True)
            parent_item.setFont(0, font)
            parent_item.setBackground(
                0, QColor(UI_COLORS['section_highlight_primary']))
            parent_item.setForeground(0, QColor('white'))

            # Add child items for each row in the group
            for _, row in group_df.iterrows():
                row_values = [str(val) if pd.notna(val) else "" for val in row]
                child_item = QTreeWidgetItem(row_values)
                parent_item.addChild(child_item)

            self.results_tree.addTopLevelItem(parent_item)

        # Resize columns to content
        for i in range(len(headers)):
            self.results_tree.resizeColumnToContents(i)

        # Update status
        self.record_count_label.setText(
            f"Showing {total_rows} results grouped by {group_by_field} ({len(group_sizes)} groups)")

        # Enable export
        self.export_btn.setEnabled(True)

    def show_loading(self, visible: bool):
        """Show/hide loading indicator"""
        if visible:
            self.record_count_label.setText("Processing...")
        else:
            if self.imported_data is not None:
                self.record_count_label.setText(
                    f"Showing {len(self.imported_data)} results")

    def show_error(self, error_message: str):
        """Display error message"""
        self.record_count_label.setText(f"Error: {error_message}")
        self.record_count_label.setStyleSheet(f"color: red;")

    def _on_clear_results(self):
        """Reset to showing just the original imported data"""
        if self.original_imported_data is not None:
            self.update_results(self.original_imported_data)
            self.record_count_label.setText(
                f"Showing {len(self.original_imported_data)} results (original data)")

    def _on_remove_data(self):
        """Remove all imported data and reset the view"""
        # Clear all data
        self.imported_data = None
        self.original_imported_data = None
        self.search_column = None
        self.context_columns = []

        # Clear the table
        self.results_table.setModel(None)

        # Reset status labels
        self.file_status_label.setText("No file imported")
        self.file_status_label.setStyleSheet(
            f"color: {UI_COLORS['muted_text']};")
        self.record_count_label.setText("No data loaded")
        self.record_count_label.setStyleSheet("")

        # Disable buttons
        for btn in self.operation_buttons.values():
            btn.setEnabled(False)
        self.clear_results_btn.setEnabled(False)
        self.remove_data_btn.setEnabled(False)
        self.export_btn.setEnabled(False)

        # Emit signal if needed for cleanup
        self.remove_data_requested.emit()


class CheckMultipleFilterDialog(QDialog):
    """Dialog for filtering current results with Lookup-style filters"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filter Results")
        self.setMinimumSize(900, 600)
        self.filter_widgets = {}
        self._setup_ui()

    def _setup_ui(self):
        from app.ui.dual_column_multiselect import DualColumnMultiselect

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Filter Current Results")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 14pt;
                font-weight: bold;
                color: {UI_COLORS['highlight_text']};
                margin-bottom: 10px;
            }}
        """)
        layout.addWidget(title)

        # Description
        desc = QLabel(
            "Select filter criteria to narrow down your results. Leave filters unselected to include all values.")
        desc.setStyleSheet(
            f"color: {UI_COLORS['muted_text']}; margin-bottom: 20px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Create filter grid (4 columns x 2 rows like Lookup)
        filter_grid = QGridLayout()
        filter_grid.setHorizontalSpacing(15)
        filter_grid.setVerticalSpacing(15)

        filters = [
            ('Standard', 'standard', FAMILIES),
            ('Shell Type', 'shell_type', SHELL_TYPES),
            ('Shell Size', 'shell_size', SHELL_SIZES),
            ('Insert Arrangement', 'insert_arrangement', INSERT_ARRANGEMENTS),
            ('Socket Type', 'socket_type', SOCKET_TYPES),
            ('Keying', 'keying', KEYINGS),
            ('Material', 'material', MATERIALS),
        ]

        for idx, (label_text, filter_key, items) in enumerate(filters):
            row = idx // 4
            col = idx % 4

            # Create container
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(5)

            # Label
            label = QLabel(label_text)
            label.setStyleSheet(f"""
                QLabel {{
                    font-weight: bold;
                    color: {UI_COLORS['highlight_text']};
                }}
            """)
            container_layout.addWidget(label)

            # Multiselect widget
            multiselect = DualColumnMultiselect(items)
            container_layout.addWidget(multiselect)

            # Store reference
            self.filter_widgets[filter_key] = multiselect

            filter_grid.addWidget(container, row, col)

        layout.addLayout(filter_grid)
        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        clear_btn = QPushButton("Clear All")
        clear_btn.setMinimumSize(100, 35)
        clear_btn.clicked.connect(self._clear_all_filters)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumSize(100, 35)
        cancel_btn.clicked.connect(self.reject)

        apply_btn = QPushButton("Apply Filters")
        apply_btn.setMinimumSize(120, 35)
        apply_btn.clicked.connect(self.accept)
        apply_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {UI_COLORS['section_highlight_primary']};
                color: white;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {UI_COLORS['filter_pill_hover']};
            }}
        """)

        button_layout.addWidget(clear_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(apply_btn)

        layout.addLayout(button_layout)

    def _clear_all_filters(self):
        """Clear all filter selections"""
        for widget in self.filter_widgets.values():
            widget.clear_selection()

    def get_filters(self) -> dict:
        """Get selected filter values"""
        filters = {}
        for key, widget in self.filter_widgets.items():
            selected = widget.get_selected_items()
            if selected:
                filters[key] = selected
        return filters
