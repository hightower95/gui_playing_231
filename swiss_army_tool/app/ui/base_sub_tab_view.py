# from PySide6.QtWidgets import (
#     QWidget, QVBoxLayout, QHBoxLayout, QTableView, QLabel, QLineEdit, QPushButton, QTextEdit, QFrame, QSplitter, QSizePolicy
# )
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSplitter,
    QTextEdit, QFrame, QTableView, QSizePolicy, QDialog, QPushButton, QScrollArea
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QCursor
from ..core.config import UI_COLORS, UI_STYLES


class BaseTabView(QWidget):
    """Reusable base layout for all sub-tabs."""

    """
    A base layout:
      - Header area for user input controls.
      - Main content area split into:
          Left: Results pane
          Right: Context + Footer (vertical split)
      - Narrow bottom footer.
    """

    def __init__(self, parent: QWidget = None):
        super().__init__()
        self._help_content = ""  # Override in subclass to provide custom help
        self._setup_ui(parent)

    def _setup_ui(self, header_widget: QWidget = None):
        # === HEADER (Search/Input Area) ===
        self.header_frame = QFrame()
        self.header_frame.setFrameShape(QFrame.StyledPanel)
        self.header_frame.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.header_frame.setFixedHeight(80)  # approx 10% of a 800px window

        # Create help label (to be added by subclass in their title row)
        self.help_label = QLabel("? Help")
        self.help_label.setStyleSheet(f"""
            QLabel {{
                color: {UI_COLORS['section_highlight_primary']};
                font-size: 10pt;
                font-weight: bold;
                padding: 2px 5px;
            }}
            QLabel:hover {{
                color: {UI_COLORS['filter_pill_hover']};
                text-decoration: underline;
            }}
        """)
        self.help_label.setCursor(QCursor(Qt.PointingHandCursor))
        self.help_label.mousePressEvent = lambda event: self._show_help_dialog()

        # === MAIN SPLITTER (Left/Right) ===
        main_splitter = QSplitter(Qt.Horizontal)

        # --- LEFT: Results Pane ---
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout = left_layout

        # Add slim "Output" banner
        output_label = QLabel("Output")
        output_label.setAlignment(Qt.AlignCenter)
        output_label.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {UI_COLORS['section_highlight_primary']}, 
                    stop:1 {UI_COLORS['section_highlight_secondary']});
                color: {UI_COLORS['highlight_text']};
                font-weight: {UI_STYLES['section_banner']['font_weight']};
                font-size: {UI_STYLES['section_banner']['font_size']};
                padding: {UI_STYLES['section_banner']['padding']};
                border: 1px solid {UI_COLORS['section_border']};
                border-radius: {UI_STYLES['section_banner']['border_radius']};
            }}
        """)
        output_label.setText("Results")
        output_label.setFixedHeight(UI_STYLES['section_banner']['height'])

        # self.results_table = QTableView()
        left_layout.addWidget(output_label)
        self.left_content_frame = QFrame()
        self.left_content_frame.setFrameShape(QFrame.StyledPanel)
        self.left_layout.addWidget(
            self.left_content_frame, 1)  # Stretch factor 1

        # Add record count label at bottom of left pane
        self.record_count_label = QLabel("Ready")
        self.record_count_label.setStyleSheet(f"""
            QLabel {{
                color: gray;
                font-size: 10px;
                padding: 5px;
                border-top: 1px solid {UI_COLORS['dark_border']};
            }}
        """)
        self.record_count_label.setFixedHeight(25)
        left_layout.addWidget(self.record_count_label)
        # self.left_layout.setStretchFactor(self.left_content_frame, 1)
        # left_layout.addWidget(self.results_table)

        # --- RIGHT: Context + Footer Pane ---
        right_splitter = QSplitter(Qt.Vertical)

        # Context section with banner
        context_frame = QFrame()
        context_layout = QVBoxLayout(context_frame)
        context_layout.setContentsMargins(0, 0, 0, 0)

        # Add "Context" banner
        context_label = QLabel("Context")
        context_label.setAlignment(Qt.AlignCenter)
        context_label.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {UI_COLORS['section_highlight_primary']}, 
                    stop:1 {UI_COLORS['section_highlight_secondary']});
                color: {UI_COLORS['highlight_text']};
                font-weight: {UI_STYLES['section_banner']['font_weight']};
                font-size: {UI_STYLES['section_banner']['font_size']};
                padding: {UI_STYLES['section_banner']['padding']};
                border: 1px solid {UI_COLORS['section_border']};
                border-radius: {UI_STYLES['section_banner']['border_radius']};
            }}
        """)
        context_label.setFixedHeight(UI_STYLES['section_banner']['height'])

        self.context_box = QTextEdit()
        self.context_box.setPlaceholderText("Context information...")
        self.context_box.setFrameShape(QFrame.StyledPanel)
        self.context_box.setStyleSheet(
            f"""background: {UI_COLORS['section_label_background']};""")

        context_layout.addWidget(context_label)
        context_layout.addWidget(self.context_box)

        self.footer_box = QTextEdit()
        self.footer_box.setPlaceholderText("Additional details / logs...")
        self.footer_box.setFrameShape(QFrame.StyledPanel)

        right_splitter.addWidget(context_frame)
        right_splitter.addWidget(self.footer_box)
        right_splitter.setSizes([400, 100])  # 80/20 vertical split

        # right_splitter.setStretchFactor(0, 4)

        main_splitter.addWidget(left_frame)
        main_splitter.addWidget(right_splitter)
        main_splitter.setSizes([700, 300])  # 70/30 horizontal split
        self.main_splitter = main_splitter
        self.right_splitter = right_splitter

        # === GLOBAL FOOTER ===
        footer_frame = QFrame()
        footer_frame.setFrameShape(QFrame.StyledPanel)

        # Build info layout
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(10, 2, 10, 2)

        # Left side - Contact info
        contact_label = QLabel("Contact Administrator for support")
        contact_label.setStyleSheet("color: gray; font-size: 10pt;")

        # Right side - Build info
        import datetime
        build_date = datetime.datetime.now().strftime("%Y-%m-%d")
        build_info_label = QLabel(
            f"Version 1.0.0 | Build Date: {build_date} | Python 3.x")
        build_info_label.setStyleSheet(
            f"color: {UI_COLORS['muted_text']}; font-size: 9pt;")
        build_info_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        footer_layout.addWidget(contact_label)
        footer_layout.addStretch()
        footer_layout.addWidget(build_info_label)

        footer_frame.setFixedHeight(30)

        # === COMPOSE ALL ===
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.header_frame)  # 10%
        layout.addWidget(main_splitter, 1)   # 80%
        layout.addWidget(footer_frame)       # thin footer
        self.setLayout(layout)

    def _show_help_dialog(self):
        """Show help dialog with tab-specific content"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Help")
        dialog.setMinimumSize(600, 400)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)

        # Scrollable content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Help text
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setFrameShape(QFrame.NoFrame)
        help_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {UI_COLORS['section_background']};
                color: {UI_COLORS['highlight_text']};
                font-size: 11pt;
                border: none;
            }}
        """)

        # Use custom help content if provided, otherwise show default
        if self._help_content:
            help_text.setHtml(self._help_content)
        else:
            help_text.setHtml(self._get_default_help_content())

        content_layout.addWidget(help_text)

        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setMinimumWidth(100)
        close_btn.setMinimumHeight(30)
        close_btn.clicked.connect(dialog.close)
        close_btn.setStyleSheet(f"""
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
        """)

        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        dialog.exec()

    def _get_default_help_content(self) -> str:
        """Return default help content - override in subclass"""
        return """
        <h2>General Help</h2>
        <p>This is a default help screen. Subclasses should override <code>_help_content</code> to provide specific help.</p>
        
        <h3>Navigation</h3>
        <ul>
            <li><b>Tab:</b> Navigate between fields</li>
            <li><b>Enter:</b> Execute search/action</li>
            <li><b>Esc:</b> Clear selection</li>
        </ul>
        """

    def set_help_content(self, html_content: str):
        """Set custom help content for this tab

        Args:
            html_content: HTML formatted help text
        """
        self._help_content = html_content

    def alt(self):

        # === Header ===
        self.header = header_widget or QLabel("Header area (inputs here)")

        # === Left (Results) ===
        self.results_pane = QTextEdit()
        self.results_pane.setPlaceholderText("Results pane")
        self.results_pane.setFrameShape(QFrame.Box)

        # === Right: Context + Footer ===
        self.context_pane = QTextEdit()
        self.context_pane.setPlaceholderText("Context pane")
        self.context_pane.setFrameShape(QFrame.Box)

        self.right_footer_pane = QTextEdit()
        self.right_footer_pane.setPlaceholderText("Right footer pane")
        self.right_footer_pane.setFrameShape(QFrame.Box)

        self.right_splitter = QSplitter(Qt.Vertical)
        self.right_splitter.addWidget(self.context_pane)
        self.right_splitter.addWidget(self.right_footer_pane)
        # default 80% / 20% height split
        self.right_splitter.setSizes([400, 100])

        # === Main horizontal splitter ===
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.addWidget(self.results_pane)
        self.main_splitter.addWidget(self.right_splitter)
        # default 70% / 30% width split
        self.main_splitter.setSizes([700, 300])

        # === Global footer ===
        self.global_footer = QLabel("Contact Administrator for support")
        self.global_footer.setStyleSheet(
            "color: gray; font-size: 11px; padding: 2px;")

        # === Combine into main layout ===
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.header)
        main_layout.addWidget(self.main_splitter)
        main_layout.addWidget(self.global_footer)
        self.setLayout(main_layout)

    # === Optional helpers ===
    def set_results_widget(self, widget: QWidget):
        self.main_splitter.replaceWidget(0, widget)

    def set_context_widget(self, widget: QWidget):
        self.right_splitter.replaceWidget(0, widget)

    def set_right_footer_widget(self, widget: QWidget):
        self.right_splitter.replaceWidget(1, widget)
