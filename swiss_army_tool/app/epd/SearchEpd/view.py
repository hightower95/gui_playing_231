from PySide6.QtWidgets import QWidget, QLineEdit, QHBoxLayout, QPushButton, QLabel, QTextEdit, QTableView, QVBoxLayout
from PySide6.QtCore import Signal
from app.ui.base_sub_tab_view import BaseTabView


class SearchEpdView(BaseTabView):
    searchEPDTriggered = Signal(str)
    rowSelected = Signal(dict)

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

        # Replace placeholder left pane with a QTableView

        # self.set_results_widget(self.table)

        # # Replace placeholder right panes with text boxes
        # self.context_box = QTextEdit()
        # self.context_box.setPlaceholderText("Context info will appear here")
        # self.context_box.setReadOnly(True)
        # self.set_context_widget(self.context_box)

        # self.footer_box = QTextEdit()
        # self.footer_box.setPlaceholderText("Footer info for selected EPD")
        # self.footer_box.setReadOnly(True)
        # self.set_right_footer_widget(self.footer_box)

        # --- Connect UI signals ---
        # self.search_button.clicked.connect(self._emit_search)
        # self.search_input.returnPressed.connect(self._emit_search)

    def _setup_header(self):
        # Add search bar and button inside header_frame
        layout = QHBoxLayout(self.header_frame)
        self.search_input = QLineEdit()
        self.search_button = QPushButton("Search")

        # Create a container widget for the search controls
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)

        # Add the container and stretch to control width
        layout.addWidget(search_container)
        layout.addStretch()  # This pushes the search controls to the left

        # Set size policy to limit width to 45%
        search_container.setMaximumWidth(int(self.header_frame.width() * 0.65))

        self.search_button.clicked.connect(self._emit_search)
        self.search_input.returnPressed.connect(self._emit_search)
        self.search_input.textChanged.connect(self._emit_search)

    def _setup_results_area(self):
        left_layout = QVBoxLayout(self.left_content_frame)
        self.table = QTableView()
        left_layout.addWidget(self.table)
        self.results_box = self.left_layout

        self.context_box.setPlaceholderText("Context info will appear here")
        self.context_box.setReadOnly(True)

        self.footer_box.setPlaceholderText("Footer info for selected EPD")
        self.footer_box.setReadOnly(True)

    def _emit_search(self):
        text = self.search_input.text().strip()
        self.search_input.blockSignals(True)
        self.search_input.setText(text)  # Clean up whitespace
        self.search_input.blockSignals(False)
        self.searchEPDTriggered.emit(text)

    def display_context(self, context_text: str):
        self.context_box.setPlainText(context_text)

    def display_footer(self, footer_text: str):
        self.footer_box.setPlainText(footer_text)
