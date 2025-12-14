"""Debug Button Widget - Standalone debug commands widget for left panel

Shows a debug button that opens a popup menu with debug commands.
"""
from typing import Optional, List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QSpinBox, QComboBox
from PySide6.QtCore import Qt, Signal


class DebugCommandsMenu(QFrame):
    """Debug commands popup menu"""

    # Signals
    show_count_requested = Signal(int, int)  # count, total
    hide_count_requested = Signal()
    topic_selected = Signal(str)  # topic name

    def __init__(self, parent: Optional[QWidget] = None, available_topics: List[str] = None):
        """Initialize debug commands menu

        Args:
            parent: Parent widget
            available_topics: List of available topic names for selection
        """
        super().__init__(parent)
        self.available_topics = available_topics or []
        self._setup_ui()

    def _setup_ui(self):
        """Setup debug menu UI"""
        self.setWindowFlags(Qt.WindowType.Window |
                            Qt.WindowType.FramelessWindowHint |
                            Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        self.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Title
        title = QLabel("Debug Commands")
        title.setStyleSheet("""
            QLabel {
                color: #4fc3f7;
                font-size: 11pt;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(title)

        # Show Count section
        count_section = QFrame()
        count_section.setStyleSheet("""
            QFrame {
                background-color: rgba(79, 195, 247, 0.05);
                border: 1px solid rgba(79, 195, 247, 0.2);
                border-radius: 6px;
                padding: 8px;
            }
        """)
        count_section.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground, True)

        count_layout = QVBoxLayout(count_section)
        count_layout.setSpacing(8)

        count_label = QLabel("Results Count")
        count_label.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                font-size: 9pt;
                font-weight: 500;
                background: transparent;
                border: none;
            }
        """)
        count_layout.addWidget(count_label)

        # Count inputs
        count_inputs = QHBoxLayout()
        count_inputs.setSpacing(8)

        shown_label = QLabel("Shown:")
        shown_label.setStyleSheet(
            "color: #909090; font-size: 9pt; background: transparent; border: none;")
        count_inputs.addWidget(shown_label)

        self.shown_spin = QSpinBox()
        self.shown_spin.setRange(0, 10000)
        self.shown_spin.setValue(15)
        self.shown_spin.setStyleSheet("""
            QSpinBox {
                background-color: #1e1e1e;
                color: #E0E0E0;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 4px;
                min-width: 60px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #2a2a2a;
                border: 1px solid #4a4a4a;
            }
        """)
        count_inputs.addWidget(self.shown_spin)

        total_label = QLabel("Total:")
        total_label.setStyleSheet(
            "color: #909090; font-size: 9pt; background: transparent; border: none;")
        count_inputs.addWidget(total_label)

        self.total_spin = QSpinBox()
        self.total_spin.setRange(0, 10000)
        self.total_spin.setValue(42)
        self.total_spin.setStyleSheet("""
            QSpinBox {
                background-color: #1e1e1e;
                color: #E0E0E0;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 4px;
                min-width: 60px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #2a2a2a;
                border: 1px solid #4a4a4a;
            }
        """)
        count_inputs.addWidget(self.total_spin)

        count_layout.addLayout(count_inputs)

        # Show/Hide buttons
        count_buttons = QHBoxLayout()
        count_buttons.setSpacing(8)

        show_btn = QPushButton("Show Count")
        show_btn.setStyleSheet("""
            QPushButton {
                background-color: #4fc3f7;
                color: #1e1e1e;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #6dd5fa;
            }
        """)
        show_btn.clicked.connect(self._on_show_count)
        count_buttons.addWidget(show_btn)

        hide_btn = QPushButton("Hide Count")
        hide_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #E0E0E0;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
        """)
        hide_btn.clicked.connect(self._on_hide_count)
        count_buttons.addWidget(hide_btn)

        count_layout.addLayout(count_buttons)

        layout.addWidget(count_section)

        # Topic Selection section
        topic_section = QFrame()
        topic_section.setStyleSheet("""
            QFrame {
                background-color: rgba(79, 195, 247, 0.05);
                border: 1px solid rgba(79, 195, 247, 0.2);
                border-radius: 6px;
                padding: 8px;
            }
        """)
        topic_section.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground, True)

        topic_layout = QVBoxLayout(topic_section)
        topic_layout.setSpacing(8)

        topic_label = QLabel("Select Topic")
        topic_label.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                font-size: 9pt;
                font-weight: 500;
                background: transparent;
                border: none;
            }
        """)
        topic_layout.addWidget(topic_label)

        # Topic dropdown
        self.topic_combo = QComboBox()
        self.topic_combo.addItem("-- Select Topic --")
        self.topic_combo.addItems(self.available_topics)
        self.topic_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e1e1e;
                color: #E0E0E0;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 6px;
                min-width: 200px;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #2a2a2a;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #E0E0E0;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2a2a;
                color: #E0E0E0;
                border: 1px solid #4a4a4a;
                selection-background-color: #4fc3f7;
                selection-color: #1e1e1e;
            }
        """)
        topic_layout.addWidget(self.topic_combo)

        # Select button
        select_btn = QPushButton("Select Topic")
        select_btn.setStyleSheet("""
            QPushButton {
                background-color: #4fc3f7;
                color: #1e1e1e;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #6dd5fa;
            }
        """)
        select_btn.clicked.connect(self._on_select_topic)
        topic_layout.addWidget(select_btn)

        layout.addWidget(topic_section)

        self.setFixedWidth(280)

    def _on_show_count(self):
        """Emit signal to show count"""
        self.show_count_requested.emit(
            self.shown_spin.value(), self.total_spin.value())

    def _on_hide_count(self):
        """Emit signal to hide count"""
        self.hide_count_requested.emit()

    def _on_select_topic(self):
        """Emit signal to select topic"""
        topic = self.topic_combo.currentText()
        if topic and topic != "-- Select Topic --":
            self.topic_selected.emit(topic)

    def update_available_topics(self, topics: List[str]):
        """Update the list of available topics

        Args:
            topics: List of topic names
        """
        self.available_topics = topics
        current_selection = self.topic_combo.currentText()
        self.topic_combo.clear()
        self.topic_combo.addItem("-- Select Topic --")
        self.topic_combo.addItems(topics)
        # Restore selection if still valid
        if current_selection in topics:
            self.topic_combo.setCurrentText(current_selection)


class DebugWidget(QWidget):
    """Debug widget for left panel - shows debug button"""

    # Signals
    show_count_requested = Signal(int, int)
    hide_count_requested = Signal()
    topic_selected = Signal(str)  # topic name

    def __init__(self, parent: Optional[QWidget] = None, available_topics: List[str] = None):
        """Initialize debug widget

        Args:
            parent: Parent widget
            available_topics: List of available topic names
        """
        super().__init__(parent)
        self.available_topics = available_topics or []
        self.menu_visible = False
        self._setup_ui()

    def _setup_ui(self):
        """Setup debug widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Button
        self.button = QPushButton("🔧 Debug")
        self.button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 165, 0, 0.1);
                color: #FFA500;
                border: 1px solid rgba(255, 165, 0, 0.3);
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 9pt;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(255, 165, 0, 0.2);
                border: 1px solid rgba(255, 165, 0, 0.5);
            }
        """)
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button.clicked.connect(self._toggle_menu)
        layout.addWidget(self.button)

        # Create menu
        self.menu = DebugCommandsMenu(self, self.available_topics)
        self.menu.setVisible(False)
        self.menu.show_count_requested.connect(self.show_count_requested.emit)
        self.menu.hide_count_requested.connect(self.hide_count_requested.emit)
        self.menu.topic_selected.connect(self.topic_selected.emit)

    def update_available_topics(self, topics: List[str]):
        """Update the list of available topics

        Args:
            topics: List of topic names
        """
        self.available_topics = topics
        self.menu.update_available_topics(topics)

    def _toggle_menu(self):
        """Toggle menu visibility"""
        self.menu_visible = not self.menu_visible

        if self.menu_visible:
            # Position menu as separate window to the right of button
            # Get button position in global coordinates
            button_pos = self.button.mapToGlobal(self.button.rect().topRight())

            # Position to right with spacing
            menu_x = button_pos.x() + 10
            menu_y = button_pos.y()

            # Ensure menu stays on screen
            from PySide6.QtGui import QGuiApplication
            screen = QGuiApplication.primaryScreen().geometry()
            menu_width = 280  # Approximate menu width
            menu_height = 350  # Approximate menu height

            # Adjust if would go off right edge
            if menu_x + menu_width > screen.right():
                menu_x = button_pos.x() - menu_width - 10  # Position to left instead

            # Adjust if would go off bottom
            if menu_y + menu_height > screen.bottom():
                menu_y = screen.bottom() - menu_height - 10

            self.menu.move(menu_x, menu_y)
            self.menu.setVisible(True)
            self.menu.raise_()
            self.menu.activateWindow()
        else:
            self.menu.setVisible(False)
