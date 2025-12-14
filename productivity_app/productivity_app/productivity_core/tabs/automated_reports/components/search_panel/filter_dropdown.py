"""
Filter Dropdown - Popup checkbox list for filter selection

Provides a popup panel with checkboxes for multi-select filtering.
"""
from typing import Optional, List, Set
from PySide6.QtWidgets import QFrame, QVBoxLayout, QCheckBox, QScrollArea, QWidget
from PySide6.QtCore import Qt, Signal


class FilterDropdown(QFrame):
    """Popup dropdown with checkbox list for filter options"""

    # Signals
    selection_changed = Signal(set)  # Emits set of selected items

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize filter dropdown

        Args:
            parent: Parent widget
        """
        super().__init__(parent, Qt.WindowType.Popup)
        self.options: List[str] = []
        self.selected_items: Set[str] = set()
        self._setup_ui()

    def _setup_ui(self):
        """Setup the dropdown UI"""
        self.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #4a4a4a;
                border-radius: 8px;
            }
        """)
        self.setMinimumWidth(200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Scroll area for options (only scrolls after 10 items)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
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

        self.scroll.setWidget(self.options_widget)
        layout.addWidget(self.scroll)

    def set_options(self, options: List[str], selected: Set[str] = None):
        """Set available options and selected items

        Args:
            options: List of available options
            selected: Set of currently selected items
        """
        self.options = options
        self.selected_items = selected or set()
        self._populate_options()
        self._update_scroll_height()

    def _populate_options(self):
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
                    spacing: 12px;
                    background-color: transparent;
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
                    background-color: transparent;
                }
                QCheckBox::indicator:checked {
                    background-color: #4fc3f7;
                    border: 1px solid #4fc3f7;
                    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTAiIHZpZXdCb3g9IjAgMCAxMiAxMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMSA1TDQuNSA4LjUgMTEgMSIgc3Ryb2tlPSIjMWUxZTFlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPjwvc3ZnPg==);
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

    def _update_scroll_height(self):
        """Update scroll area height based on number of options"""
        # Each checkbox is approximately 32px (padding + text)
        item_height = 32
        num_items = len(self.options)

        if num_items <= 10:
            # Show all items without scrolling
            self.scroll.setMaximumHeight(num_items * item_height + 20)
        else:
            # Show 10 items and enable scrolling
            self.scroll.setMaximumHeight(10 * item_height + 20)

    def _on_checkbox_changed(self, option: str, state: int):
        """Handle checkbox state change

        Args:
            option: Option that was toggled
            state: Checkbox state
        """
        if state == Qt.CheckState.Checked.value:
            self.selected_items.add(option)
        else:
            self.selected_items.discard(option)

        self.selection_changed.emit(self.selected_items)

    def get_selected(self) -> Set[str]:
        """Get currently selected items

        Returns:
            Set of selected item names
        """
        return self.selected_items.copy()

    def clear_selection(self):
        """Clear all selected items"""
        self.selected_items.clear()
        self._populate_options()
