"""Debug Commands Menu - Debug panel for testing UI states

Shows a popup menu with debug commands for testing various UI states.
"""
from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QSpinBox
from PySide6.QtCore import Qt, Signal


class DebugCommandsMenu(QFrame):
    """Debug commands popup menu"""

    # Signals
    show_count_requested = Signal(int, int)  # count, total
    hide_count_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize debug commands menu"""
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup debug menu UI"""
        self.setWindowFlags(Qt.WindowType.Popup |
                            Qt.WindowType.FramelessWindowHint)
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

        self.setFixedWidth(280)

    def _on_show_count(self):
        """Emit signal to show count"""
        self.show_count_requested.emit(
            self.shown_spin.value(), self.total_spin.value())

    def _on_hide_count(self):
        """Emit signal to hide count"""
        self.hide_count_requested.emit()


class DebugButton(QWidget):
    """Debug button that opens debug commands menu"""

    # Signals
    show_count_requested = Signal(int, int)
    hide_count_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize debug button"""
        super().__init__(parent)
        self.menu_visible = False
        self._setup_ui()

    def _setup_ui(self):
        """Setup debug button UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Button
        self.button = QPushButton("🔧 Debug Commands")
        self.button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 165, 0, 0.1);
                color: #FFA500;
                border: 1px solid rgba(255, 165, 0, 0.3);
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 9pt;
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
        self.menu = DebugCommandsMenu(self)
        self.menu.setVisible(False)
        self.menu.show_count_requested.connect(self.show_count_requested.emit)
        self.menu.hide_count_requested.connect(self.hide_count_requested.emit)

    def _toggle_menu(self):
        """Toggle menu visibility"""
        self.menu_visible = not self.menu_visible

        if self.menu_visible:
            # Position menu above button
            button_pos = self.button.mapToGlobal(self.button.rect().topLeft())
            menu_x = button_pos.x()
            menu_y = button_pos.y() - self.menu.height() - 8
            self.menu.move(menu_x, menu_y)
            self.menu.setVisible(True)
            self.menu.raise_()
        else:
            self.menu.setVisible(False)
