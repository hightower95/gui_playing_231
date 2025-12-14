"""Add Button - Button with dropdown menu for adding reports

Shows "+ Add" with dropdown menu on click.
"""
from typing import Optional, Callable
from pathlib import Path
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import Qt, Signal, QByteArray
from .add_button_menu import AddButtonMenu


class AddButton(QWidget):
    """Add button with dropdown menu"""

    # Signal emitted with option ID
    option_clicked = Signal(str)  # Emits option ID

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize add button"""
        super().__init__(parent)
        self.menu_visible = False
        self._setup_ui()

    def register_callback(self, option_id: str, callback: Callable):
        """Register a callback for a menu option

        Args:
            option_id: ID of the menu option
            callback: Callback function to execute
        """
        self.menu.register_callback(option_id, callback)

    def _setup_ui(self):
        """Setup add button UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Button container
        self.button_container = QWidget()
        self.button_container.setObjectName("addButtonContainer")
        self.button_container.setStyleSheet("""
            QWidget#addButtonContainer {
                padding: 6px 5px;
                border: 1px solid #3a3a3a;
                border-radius: 9px;
                background-color: #2a2a2a;
            }
            QWidget#addButtonContainer:hover {
                border: 1px solid #4a4a4a;
                background-color: #2d2d2d;
            }
        """)
        self.button_container.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button_container.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground, True)

        button_layout = QHBoxLayout(self.button_container)
        button_layout.setContentsMargins(8, 0, 8, 0)
        button_layout.setSpacing(6)

        # Plus icon
        plus_label = QLabel("+")
        plus_label.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                font-size: 12pt;
                font-weight: bold;
                background: transparent;
                border: none;
                padding-bottom: 2px;
            }
        """)
        button_layout.addWidget(plus_label)

        # "Add" text
        text_label = QLabel("Add")
        text_label.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                font-size: 10pt;
                background: transparent;
                border: none;
            }
        """)
        button_layout.addWidget(text_label)

        # Down arrow
        icon_dir = Path(__file__).parent.parent / "left_panel"
        arrow_path = icon_dir / "keyboard_arrow_down_22dp_E3E3E3_FILL0_wght100_GRAD200_opsz24.svg"

        with open(arrow_path, 'rb') as f:
            arrow_data = QByteArray(f.read())

        arrow_icon = QSvgWidget()
        arrow_icon.load(arrow_data)
        arrow_icon.setFixedSize(16, 16)
        arrow_icon.setStyleSheet("background: transparent; border: none;")
        button_layout.addWidget(arrow_icon)

        layout.addWidget(self.button_container)

        # Create menu
        self.menu = AddButtonMenu(self)
        self.menu.setVisible(False)
        self.menu.option_clicked.connect(self._on_option_clicked)

        # Make clickable
        self.button_container.mousePressEvent = lambda e: self._toggle_menu()

    def _on_option_clicked(self, option_id: str):
        """Handle menu option click

        Args:
            option_id: ID of the clicked option
        """
        self.option_clicked.emit(option_id)

    def _toggle_menu(self):
        """Toggle menu visibility"""
        self.menu_visible = not self.menu_visible

        if self.menu_visible:
            # Position menu below button, aligned to right edge
            button_pos = self.button_container.mapToGlobal(
                self.button_container.rect().bottomRight())
            menu_x = button_pos.x() - self.menu.width()
            menu_y = button_pos.y() + 8
            self.menu.move(menu_x, menu_y)
            self.menu.setVisible(True)
            self.menu.raise_()
        else:
            self.menu.setVisible(False)

    def focusOutEvent(self, event):
        """Close menu when focus is lost"""
        if self.menu_visible:
            self.menu_visible = False
            self.menu.setVisible(False)
        super().focusOutEvent(event)
