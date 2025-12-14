"""Filter Button - Modern filter button with checkbox dropdown

Provides a button that shows selected count and opens a checkbox list on click.
"""
from typing import Optional, List, Set
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import Qt, Signal, QByteArray
from .filter_dropdown import FilterDropdown


class FilterButton(QWidget):
    """Modern filter button with dropdown checkbox list"""

    # Configuration constants for easy adjustment
    BUTTON_PADDING_VERTICAL = 4
    BUTTON_PADDING_HORIZONTAL = 10
    BUTTON_BORDER_RADIUS = 9
    ARROW_SIZE = 16
    ARROW_TOP_OFFSET = 2

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
        self.button_container.setObjectName("buttonContainer")
        self._update_button_style()
        self.button_container.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button_container.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground, True)

        button_layout = QHBoxLayout(self.button_container)
        button_layout.setContentsMargins(self.BUTTON_PADDING_HORIZONTAL, self.BUTTON_PADDING_VERTICAL,
                                         self.BUTTON_PADDING_HORIZONTAL, self.BUTTON_PADDING_VERTICAL)
        button_layout.setSpacing(4)

        # Text label
        self.button_label = QLabel()
        self.button_label.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                font-size: 10pt;
                background: transparent;
                border: none;
                padding: 0px;
                padding-bottom: 2px;
            }
        """)
        self._update_button_text()
        button_layout.addWidget(self.button_label)

        # Down arrow icon (SVG)
        icon_dir = Path(__file__).parent.parent / "left_panel"
        arrow_path = icon_dir / "keyboard_arrow_down_22dp_E3E3E3_FILL0_wght100_GRAD200_opsz24.svg"

        with open(arrow_path, 'rb') as f:
            arrow_data = QByteArray(f.read())

        self.arrow_icon = QSvgWidget()
        self.arrow_icon.load(arrow_data)
        self.arrow_icon.setContentsMargins(0, self.ARROW_TOP_OFFSET, 0, 0)
        self.arrow_icon.setStyleSheet("background: transparent; border: none;")
        button_layout.addWidget(self.arrow_icon)

        main_layout.addWidget(self.button_container)

        # Create dropdown widget
        self.dropdown = FilterDropdown(self)
        self.dropdown.setVisible(False)
        self.dropdown.set_options(self.options, self.selected_items)
        self.dropdown.selection_changed.connect(self._on_selection_changed)

        # Make button clickable
        self.button_container.mousePressEvent = lambda e: self._toggle_dropdown()

    def _on_selection_changed(self, selected_items: Set[str]):
        """Handle selection changes from dropdown

        Args:
            selected_items: Set of selected items
        """
        self.selected_items = selected_items
        self._update_button_text()
        self._update_button_style()
        self.selection_changed.emit(self.filter_name, self.selected_items)

    def _update_button_style(self):
        """Update button style based on whether filters are active"""
        has_selection = len(self.selected_items) > 0

        if has_selection:
            # Blue tint when filters active
            self.button_container.setStyleSheet(f"""
                QWidget#buttonContainer {{
                    padding: 0px;
                    border: 1px solid #4fc3f7;
                    border-radius: {self.BUTTON_BORDER_RADIUS}px;
                    background-color: rgba(79, 195, 247, 0.15);
                }}
                QWidget#buttonContainer:hover {{
                    border: 1px solid #4fc3f7;
                    background-color: rgba(79, 195, 247, 0.2);
                }}
            """)
        else:
            # Default style
            self.button_container.setStyleSheet(f"""
                QWidget#buttonContainer {{
                    padding: 0px;
                    border: 1px solid #3a3a3a;
                    border-radius: {self.BUTTON_BORDER_RADIUS}px;
                    background-color: #2a2a2a;
                }}
                QWidget#buttonContainer:hover {{
                    border: 1px solid #4a4a4a;
                    background-color: #2d2d2d;
                }}
            """)

    def _toggle_dropdown(self):
        """Toggle dropdown visibility and position it below button"""
        self.dropdown_visible = not self.dropdown_visible

        if self.dropdown_visible:
            # Position dropdown below the button container with 8px gap
            button_pos = self.button_container.mapToGlobal(
                self.button_container.rect().bottomLeft())
            button_pos.setY(button_pos.y() + 8)  # Add 8px gap
            self.dropdown.move(button_pos)
            self.dropdown.setVisible(True)
            self.dropdown.raise_()
        else:
            self.dropdown.setVisible(False)

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
        self.dropdown.set_options(options, self.selected_items)

    def clear_selection(self):
        """Clear all selected items"""
        self.selected_items.clear()
        self.dropdown.clear_selection()
        self._update_button_text()
        self._update_button_style()
        self.selection_changed.emit(self.filter_name, self.selected_items)

    def remove_item(self, item: str):
        """Remove a specific item from selection

        Args:
            item: Item to remove
        """
        if item in self.selected_items:
            self.selected_items.remove(item)
            self._update_button_text()
            self._update_button_style()
            self.dropdown.set_options(self.options, self.selected_items)
            # Emit signal to notify of change
            self.selection_changed.emit(self.filter_name, self.selected_items)

    def get_selected(self) -> Set[str]:
        """Get currently selected items

        Returns:
            Set of selected item names
        """
        return self.selected_items.copy()
