"""Add Button Menu - Dropdown menu with options for adding reports

Shows a menu with configurable options for adding reports, groups, plugins, etc.
"""
from typing import Optional, List, Callable, Dict
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor


class AddMenuOption(QWidget):
    """Single menu option with icon, title, and description"""

    clicked = Signal()

    def __init__(self, icon_text: str, title: str, description: str, parent: Optional[QWidget] = None):
        """Initialize menu option

        Args:
            icon_text: Emoji or text for icon placeholder
            title: Option title
            description: Option description
            parent: Parent widget
        """
        super().__init__(parent)
        self.title_text = title
        self._setup_ui(icon_text, title, description)

    def _setup_ui(self, icon_text: str, title: str, description: str):
        """Setup menu option UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)

        # Icon placeholder (will be replaced with actual icons)
        icon_label = QLabel(icon_text)
        icon_label.setStyleSheet("""
            QLabel {
                color: #4fc3f7;
                font-size: 18pt;
                background: transparent;
                border: none;
                min-width: 32px;
                max-width: 32px;
            }
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Text container
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                font-size: 10pt;
                font-weight: 500;
                background: transparent;
                border: none;
            }
        """)
        text_layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                color: #909090;
                font-size: 8pt;
                background: transparent;
                border: none;
            }
        """)
        text_layout.addWidget(desc_label)

        layout.addLayout(text_layout)

        # Style the option container
        self.setStyleSheet("""
            AddMenuOption {
                background-color: transparent;
                border-radius: 6px;
            }
            AddMenuOption:hover {
                background-color: rgba(79, 195, 247, 0.1);
            }
        """)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        """Handle click"""
        self.clicked.emit()
        super().mousePressEvent(event)


class AddButtonMenu(QFrame):
    """Dropdown menu for Add button with multiple options"""

    # Signal emitted with option ID when clicked
    option_clicked = Signal(str)  # Emits option ID

    def __init__(self, parent: Optional[QWidget] = None, options: List[Dict] = None):
        """Initialize add button menu

        Args:
            parent: Parent widget
            options: List of option dicts with keys: 'id', 'icon', 'title', 'description'
        """
        super().__init__(parent)
        self.options = options or self._get_default_options()
        self.callbacks: Dict[str, Callable] = {}
        self._setup_ui()

    def _get_default_options(self) -> List[Dict]:
        """Get default menu options

        Returns:
            List of option dictionaries
        """
        return [
            {
                'id': 'load_report',
                'icon': '📄',
                'title': 'Load New Report',
                'description': 'Import report config file'
            },
            {
                'id': 'create_group',
                'icon': '📚',
                'title': 'Create Report Group',
                'description': 'Bundle existing reports'
            },
            {
                'id': 'load_plugins',
                'icon': '🔌',
                'title': 'Load Plugins',
                'description': 'Load and configure plugins'
            }
        ]

    def register_callback(self, option_id: str, callback: Callable):
        """Register a callback for an option

        Args:
            option_id: ID of the option
            callback: Callback function to execute
        """
        self.callbacks[option_id] = callback

    def _setup_ui(self):
        """Setup menu UI"""
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
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        # Create options from array
        for option_data in self.options:
            option_widget = AddMenuOption(
                option_data['icon'],
                option_data['title'],
                option_data['description']
            )
            option_widget.clicked.connect(
                lambda opt_id=option_data['id']: self._on_option_clicked(
                    opt_id)
            )
            layout.addWidget(option_widget)

        self.setFixedWidth(250)

    def _on_option_clicked(self, option_id: str):
        """Handle option click

        Args:
            option_id: ID of clicked option
        """
        self.hide()

        # Execute registered callback if exists
        if option_id in self.callbacks:
            self.callbacks[option_id]()

        # Emit signal
        self.option_clicked.emit(option_id)
