# from PySide6.QtWidgets import (
#     QWidget, QVBoxLayout, QHBoxLayout, QTableView, QLabel, QLineEdit, QPushButton, QTextEdit, QFrame, QSplitter, QSizePolicy
# )
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSplitter,
    QTextEdit, QFrame, QTableView, QSizePolicy
)
from PySide6.QtCore import Signal, Qt


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
        self._setup_ui(parent)

    def _setup_ui(self, header_widget: QWidget = None):
        # === HEADER (Search/Input Area) ===
        self.header_frame = QFrame()
        self.header_frame.setFrameShape(QFrame.StyledPanel)
        self.header_frame.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.header_frame.setFixedHeight(80)  # approx 10% of a 800px window

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
        output_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                font-weight: bold;
                padding: 2px;
                border-bottom: 1px solid #ccc;
            }
        """)
        output_label.setText("Results")
        output_label.setFixedHeight(22)

        # self.results_table = QTableView()
        left_layout.addWidget(output_label)
        self.left_content_frame = QFrame()
        self.left_content_frame.setFrameShape(QFrame.StyledPanel)
        self.left_layout.addWidget(self.left_content_frame)
        # self.left_layout.setStretchFactor(self.left_content_frame, 1)
        # left_layout.addWidget(self.results_table)

        # --- RIGHT: Context + Footer Pane ---
        right_splitter = QSplitter(Qt.Vertical)

        self.context_box = QTextEdit()
        self.context_box.setPlaceholderText("Context information...")
        self.context_box.setFrameShape(QFrame.StyledPanel)

        self.footer_box = QTextEdit()
        self.footer_box.setPlaceholderText("Additional details / logs...")
        self.footer_box.setFrameShape(QFrame.StyledPanel)

        right_splitter.addWidget(self.context_box)
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
        footer_label = QLabel("Contact Administrator for support")
        footer_label.setFixedHeight(24)
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("color: gray; font-size: 10pt;")
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.addWidget(footer_label)
        footer_frame.setFixedHeight(30)

        # === COMPOSE ALL ===
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.header_frame)  # 10%
        layout.addWidget(main_splitter, 1)   # 80%
        layout.addWidget(footer_frame)       # thin footer
        self.setLayout(layout)

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
