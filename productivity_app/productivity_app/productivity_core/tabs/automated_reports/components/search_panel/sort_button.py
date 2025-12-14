"""Sort Dropdown - Single select dropdown for sorting

Shows current sort option and allows selection from dropdown.
"""
from typing import Optional, List, Dict, Tuple
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import Qt, Signal, QByteArray


class SortDropdown(QFrame):
    """Dropdown for sort options with click selection"""

    selection_changed = Signal(str, bool)  # Emits (sort_id, ascending)

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize sort dropdown"""
        super().__init__(parent)
        self.options = []  # List of dicts: {id, label, ascending, icon}
        self._setup_ui()

    def _setup_ui(self):
        """Setup dropdown UI"""
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

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(4)

        self.setFixedWidth(200)

    def set_options(self, options: List[Dict], selected_id: str = None, selected_ascending: bool = True):
        """Set available sort options

        Args:
            options: List of dicts with keys: id, label, ascending, icon (svg filename)
            selected_id: Currently selected option ID
            selected_ascending: Currently selected ascending state
        """
        # Clear layout
        while self.main_layout.count() > 0:
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.options = options

        # Get icon directory
        icon_dir = Path(__file__).parent

        # Add new options
        for option in options:
            is_selected = (option['id'] == selected_id and
                           option['ascending'] == selected_ascending)

            option_widget = QWidget()
            option_widget.setCursor(Qt.CursorShape.PointingHandCursor)
            option_widget.setProperty('sort_id', option['id'])
            option_widget.setProperty('ascending', option['ascending'])

            # Apply selection highlighting like topic items and filter buttons
            if is_selected:
                option_widget.setStyleSheet("""
                    QWidget {
                        background-color: rgba(79, 195, 247, 0.15);
                        border-radius: 4px;
                    }
                    QWidget:hover {
                        background-color: rgba(79, 195, 247, 0.2);
                    }
                """)
            else:
                option_widget.setStyleSheet("""
                    QWidget {
                        background: transparent;
                    }
                    QWidget:hover {
                        background-color: rgba(79, 195, 247, 0.1);
                        border-radius: 4px;
                    }
                """)
            option_widget.setAttribute(
                Qt.WidgetAttribute.WA_StyledBackground, True)

            # Connect click to selection
            option_widget.mousePressEvent = lambda e, opt=option: self._on_option_clicked(
                opt)

            option_layout = QHBoxLayout(option_widget)
            option_layout.setContentsMargins(6, 6, 6, 6)
            option_layout.setSpacing(8)

            # SVG Icon
            if option.get('icon'):
                icon_path = icon_dir / option['icon']
                if icon_path.exists():
                    with open(icon_path, 'rb') as f:
                        icon_data = QByteArray(f.read())

                    icon_widget = QSvgWidget()
                    icon_widget.load(icon_data)
                    icon_widget.setFixedSize(18, 18)
                    icon_widget.setStyleSheet(
                        "background: transparent; border: none;")
                    option_layout.addWidget(icon_widget)

            # Label
            label = QLabel(option['label'])
            label.setStyleSheet("""
                QLabel {
                    color: #E0E0E0;
                    font-size: 9pt;
                    background: transparent;
                    border: none;
                }
            """)
            option_layout.addWidget(label)
            self.main_layout.addWidget(option_widget)

    def _on_option_clicked(self, option: Dict):
        """Handle option click

        Args:
            option: The option dict that was clicked
        """
        self.selection_changed.emit(option['id'], option['ascending'])
        self.hide()


class SortButton(QWidget):
    """Sort button with dropdown selection"""

    # Signals
    sort_changed = Signal(str, bool)  # Emits (sort_id, ascending)

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize sort button"""
        super().__init__(parent)
        self.current_sort_id = "name"
        self.current_ascending = True
        self.dropdown_visible = False
        self._setup_ui()

    def _setup_ui(self):
        """Setup sort button UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Button container
        self.button_container = QWidget()
        self.button_container.setObjectName("sortButtonContainer")
        self.button_container.setStyleSheet("""
            QWidget#sortButtonContainer {
                padding: 0px;
                border: 1px solid #3a3a3a;
                border-radius: 9px;
                background-color: #2a2a2a;
            }
            QWidget#sortButtonContainer:hover {
                border: 1px solid #4a4a4a;
                background-color: #2d2d2d;
            }
        """)
        self.button_container.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button_container.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground, True)

        button_layout = QHBoxLayout(self.button_container)
        button_layout.setContentsMargins(10, 4, 10, 4)
        button_layout.setSpacing(4)

        # Label
        self.button_label = QLabel()
        self.button_label.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                font-size: 10pt;
                background: transparent;
                border: none;
                padding: 0px;
            }
        """)

        button_layout.addWidget(self.button_label)

        # Down arrow
        icon_dir = Path(__file__).parent.parent / "left_panel"
        arrow_path = icon_dir / "keyboard_arrow_down_22dp_E3E3E3_FILL0_wght100_GRAD200_opsz24.svg"

        with open(arrow_path, 'rb') as f:
            arrow_data = QByteArray(f.read())

        self.arrow_icon = QSvgWidget()
        self.arrow_icon.load(arrow_data)
        self.arrow_icon.setContentsMargins(0, 2, 0, 0)
        self.arrow_icon.setStyleSheet("background: transparent; border: none;")
        button_layout.addWidget(self.arrow_icon)

        layout.addWidget(self.button_container)

        # Create dropdown
        self.dropdown = SortDropdown(self)
        self.dropdown.setVisible(False)
        self.dropdown.set_options([
            {'id': 'name', 'label': 'Name (A-Z)', 'ascending': True,
             'icon': 'sort_by_alpha_28dp_E3E3E3_FILL0_wght200_GRAD0_opsz24.svg'},
            {'id': 'name', 'label': 'Name (Z-A)', 'ascending': False,
             'icon': 'sort_by_alpha_28dp_E3E3E3_FILL0_wght200_GRAD0_opsz24.svg'},
            {'id': 'date', 'label': 'Date Modified (Newest)', 'ascending': False,
             'icon': 'calendar_today_28dp_E3E3E3_FILL0_wght200_GRAD0_opsz24.svg'},
            {'id': 'date', 'label': 'Date Modified (Oldest)', 'ascending': True,
             'icon': 'calendar_today_28dp_E3E3E3_FILL0_wght200_GRAD0_opsz24.svg'},
            {'id': 'usage', 'label': 'Most Used', 'ascending': False, 'icon': None}
        ], self.current_sort_id, self.current_ascending)
        self.dropdown.selection_changed.connect(
            self._on_sort_selection_changed)
        self._update_label()
        # Make clickable
        self.button_container.mousePressEvent = lambda e: self._toggle_dropdown()

    def _update_label(self):
        """Update button label text"""
        # Find matching option to get display label
        for option in self.dropdown.options:
            if option['id'] == self.current_sort_id and option['ascending'] == self.current_ascending:
                self.button_label.setText(f"Sort: {option['label']}")
                return
        # Fallback
        self.button_label.setText("Sort")

    def _toggle_dropdown(self):
        """Toggle dropdown visibility"""
        self.dropdown_visible = not self.dropdown_visible

        if self.dropdown_visible:
            # Position dropdown below button
            button_pos = self.button_container.mapToGlobal(
                self.button_container.rect().bottomLeft())
            button_pos.setY(button_pos.y() + 8)
            self.dropdown.move(button_pos)
            self.dropdown.setVisible(True)
            self.dropdown.raise_()
        else:
            self.dropdown.setVisible(False)

    def _on_sort_selection_changed(self, sort_id: str, ascending: bool):
        """Handle sort selection change

        Args:
            sort_id: Sort field ID (name, date, usage)
            ascending: Whether to sort in ascending order
        """
        self.current_sort_id = sort_id
        self.current_ascending = ascending
        self.dropdown.set_options(self.dropdown.options, sort_id, ascending)
        self._update_label()

        # Debug output
        print(f"Sort changed: id='{sort_id}', ascending={ascending}")

        self.sort_changed.emit(sort_id, ascending)
        self.dropdown_visible = False

    def focusOutEvent(self, event):
        """Close dropdown when focus is lost"""
        if self.dropdown_visible:
            self.dropdown_visible = False
            self.dropdown.setVisible(False)
        super().focusOutEvent(event)
