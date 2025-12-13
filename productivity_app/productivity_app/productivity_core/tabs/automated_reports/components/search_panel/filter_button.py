
"""Filter Button - Modern filter button with checkbox dropdown

Provides a button that shows selected count and opens a checkbox list on click.
"""
from typing import Optional, List, Set
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QFrame, QHBoxLayout,
                               QCheckBox, QScrollArea, QLabel)
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import Qt, Signal, QByteArray


class FilterButton(QWidget):
    """Modern filter button with dropdown checkbox list"""

    # Signals
    selection_changed = Signal(str, set)  # Emits (filter_name, selected_items)

    def __init__(
        self,
        filter_name: str,
        options: List[str] = None,
        parent: Optional[QWidget] = None
    ):
        """Initialize filter button

        Args:
            filter_name: Name of this filter (e.g., "Project")
            options: List of available options
            parent: Parent widget
        """
        super().__init__(parent)
        self.filter_name = filter_name
        self.options = options or []
        self.selected_items: Set[str] = set()
        self.dropdown_visible = False
        self._setup_ui()

    def _setup_ui(self):
        """Setup the filter button UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Button container with text and arrow
        self.button_container = QWidget()
        self.button_container.setStyleSheet("""
            QWidget {
                padding: 8px 14px;
                border: 1px solid #3a3a3a;
                border-radius: 12px;
                background-color: #2a2a2a;
            }
            QWidget:hover {
                border: 1px solid #4a4a4a;
                background-color: #2d2d2d;
            }
        """)
        self.button_container.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button_container.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground, True)

        button_layout = QHBoxLayout(self.button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(8)

        # Text label
        self.button_label = QLabel()
        self.button_label.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                font-size: 10pt;
                background: transparent;
                border: none;
            }
        """)
        self._update_button_text()
        button_layout.addWidget(self.button_label)

        # Down arrow icon (SVG)
        icon_dir = Path(__file__).parent.parent / "left_panel"
        arrow_path = icon_dir / "arrow_forward_ios_22dp_E3E3E3_FILL0_wght100_GRAD200_opsz24.svg"

        # Cache and rotate arrow to point down
        with open(arrow_path, 'rb') as f:
            arrow_data = QByteArray(f.read())

        self.arrow_icon = QSvgWidget()
        self.arrow_icon.load(arrow_data)
        self.arrow_icon.setFixedSize(12, 12)
        # Rotate 90 degrees to point down
        self.arrow_icon.setStyleSheet(
            "QWidget { transform: rotate(90deg); background: transparent; }")
        button_layout.addWidget(self.arrow_icon)

        main_layout.addWidget(self.button_container)

        # Make clickable
        self.button_container.mousePressEvent = lambda e: self._toggle_dropdown()

        # Dropdown panel (positioned absolutely, initially hidden)
        # Create as child but with WindowFlags to position on top
        self.dropdown = QFrame(self, Qt.WindowType.Popup)
        self.dropdown.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #4a4a4a;
                border-radius: 8px;
            }
        """)
        self.dropdown.setVisible(False)
        self.dropdown.setMinimumWidth(200)

        dropdown_layout = QVBoxLayout(self.dropdown)
        dropdown_layout.setContentsMargins(8, 8, 8, 8)
        dropdown_layout.setSpacing(4)

        # Scroll area for options
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(250)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #4a4a4a;
                border-radius: 4px;
            }
        """)

        # Container for checkboxes
        self.options_widget = QWidget()
        self.options_layout = QVBoxLayout(self.options_widget)
        self.options_layout.setContentsMargins(4, 4, 4, 4)
        self.options_layout.setSpacing(2)

        # self._populate_options()

        scroll.setWidget(self.options_widget)
        dropdown_layout.addWidget(scroll)

    def _toggle_dropdown(self):
        """Toggle dropdown visibility and position it below button"""
        self.dropdown_visible = not self.dropdown_visible

        if self.dropdown_visible:
            # Position dropdown below the button container
            button_pos = self.button_container.mapToGlobal(
                self.button_container.rect().bottomLeft())
            self.dropdown.move(button_pos)
            self.dropdown.setVisible(True)
            self.dropdown.raise_()
        else:
            self.dropdown.setVisible(False)
        """Populate the checkbox options"""
        # Clear existing
        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add checkboxes
        for option in self.options:
            checkbox = QCheckBox(option)
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: #E0E0E0;
                    font-size: 10pt;
                    padding: 6px;
                    spacing: 8px;
                }
                QCheckBox:hover {
                    background-color: #353535;
                    border-radius: 4px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border: 1px solid #4a4a4a;
                    border-radius: 3px;
                    background-color: #1e1e1e;
                }
                QCheckBox::indicator:checked {
                    background-color: #4fc3f7;
                    border: 1px solid #4fc3f7;
                }
                QCheckBox::indicator:checked:hover {
                    background-color: #3ab0e0;
                }
            """)
            checkbox.setChecked(option in self.selected_items)
            checkbox.stateChanged.connect(
                lambda state, opt=option: self._on_checkbox_changed(opt, state))
            self.options_layout.addWidget(checkbox)

        self.options_layout.addStretch()

    def _on_checkbox_changed(self, option: str, state: int):
        """Handle checkbox state change

        Args:
            option: Option that was toggled
            state: Checkbox state (Qt.CheckState)
        """
        if state == Qt.CheckState.Checked.value:
            self.selected_items.add(option)
        else:
            self.selected_items.discard(option)

        self._update_button_text()
        self.selection_changed.emit(self.filter_name, self.selected_items)

    def _update_button_text(self):
        """Update button text to show filter name and count"""
        count = len(self.selected_items)
        if count == 0:
            text = self.filter_name
        else:
            text = f"{self.filter_name} ({count})"
        if hasattr(self, 'button_label'):
            self.button_label.setText(text)

    def focusOutEvent(self, event):
        """Close dropdown when focus is lost"""
        # Close dropdown when clicking outside
        if self.dropdown_visible:
            self.dropdown_visible = False
            self.dropdown.setVisible(False)
        super().focusOutEvent(event)

    def set_options(self, options: List[str]):
        """Update available options

        Args:
            options: New list of options
        """
        self.options = options
        self._populate_options()

    def clear_selection(self):
        """Clear all selected items"""
        self.selected_items.clear()
        self._populate_options()
        self._update_button_text()
        self.selection_changed.emit(self.filter_name, self.selected_items)

    def get_selected(self) -> Set[str]:
        """Get currently selected items

        Returns:
            Set of selected item names
        """
        return self.selected_items.copy()
