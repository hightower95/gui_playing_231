"""
Dual Column Multiselect Widget - Reusable component for filter selections
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QListWidget, QListWidgetItem, QApplication
from PySide6.QtCore import Qt, Signal
from ..core.config import UI_COLORS


class DualColumnMultiselect(QWidget):
    """A two-column multiselect list widget with synchronized scrolling"""

    # Signal emitted when selection changes
    selection_changed = Signal()

    def __init__(self, items: list = None, parent=None):
        super().__init__(parent)
        self.items = items or []
        self.left_list = None
        self.right_list = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup the dual-column UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        if not self.items:
            return

        # Split items into two columns - balance them evenly
        mid_point = (len(self.items) + 1) // 2
        left_items = self.items[:mid_point]
        right_items = self.items[mid_point:]

        # If odd number of items, add padding for synchronized scrolling
        if len(self.items) % 2 == 1:
            left_items = left_items + ["", ""]
            right_items = right_items + [""]

        # Determine width based on content length
        max_length = max(len(item) for item in self.items) if self.items else 0
        width = 55 if max_length <= 5 else 110
        right_border_style = "1px solid #555555" if width == 55 else "none"

        # Style for left list
        left_style = f"""
            QListWidget {{
                background-color: {UI_COLORS['section_background']};
                color: {UI_COLORS['highlight_text']};
                border: 1px solid {UI_COLORS['frame_border']};
                border-right: {right_border_style};
                border-top-left-radius: 3px;
                border-bottom-left-radius: 3px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                min-width: 110px;
                max-width: 110px;
                min-height: 95px;
                max-height: 95px;
                padding: 0px;
                margin: 0px;
            }}
            QListWidget::item {{
                padding: 3px;
                min-height: 25px;
            }}
            QListWidget::item:selected {{
                background-color: {UI_COLORS['section_highlight_primary']};
                color: white;
            }}
            QScrollBar:vertical {{
                width: 0px;
            }}
        """

        # Style for right list
        right_style = f"""
            QListWidget {{
                background-color: {UI_COLORS['section_background']};
                color: {UI_COLORS['highlight_text']};
                border: 1px solid {UI_COLORS['frame_border']};
                border-left: {right_border_style};
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
                min-width: 110px;
                max-width: 110px;
                min-height: 95px;
                max-height: 95px;
                padding: 0px;
                margin: 0px;
            }}
            QListWidget::item {{
                padding: 3px;
                min-height: 25px;
            }}
            QListWidget::item:selected {{
                background-color: {UI_COLORS['section_highlight_primary']};
                color: white;
            }}
            QScrollBar:vertical {{
                border: 1px solid {UI_COLORS['frame_border']};
                background: {UI_COLORS['section_background']};
                width: 12px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {UI_COLORS['section_highlight_primary']};
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {UI_COLORS['filter_pill_hover']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """

        # Create left list
        self.left_list = QListWidget()
        self.left_list.setSelectionMode(QListWidget.MultiSelection)
        for item in left_items:
            list_item = QListWidgetItem(item)
            list_item.setToolTip(item)
            self.left_list.addItem(list_item)
            if item == "":
                idx = self.left_list.count() - 1
                item_widget = self.left_list.item(idx)
                if item_widget:
                    item_widget.setFlags(Qt.NoItemFlags)
                    item_widget.setToolTip("")
        self.left_list.setStyleSheet(left_style)
        self.left_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.left_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.left_list.setContentsMargins(0, 0, 0, 0)

        # Create right list
        self.right_list = QListWidget()
        self.right_list.setSelectionMode(QListWidget.MultiSelection)
        for item in right_items:
            list_item = QListWidgetItem(item)
            list_item.setToolTip(item)
            self.right_list.addItem(list_item)
            if item == "":
                idx = self.right_list.count() - 1
                item_widget = self.right_list.item(idx)
                if item_widget:
                    item_widget.setFlags(Qt.NoItemFlags)
                    item_widget.setToolTip("")
        self.right_list.setStyleSheet(right_style)
        self.right_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.right_list.setContentsMargins(0, 0, 0, 0)

        # Synchronize scrolling
        self.left_list.verticalScrollBar().valueChanged.connect(
            self.right_list.verticalScrollBar().setValue
        )
        self.right_list.verticalScrollBar().valueChanged.connect(
            self.left_list.verticalScrollBar().setValue
        )

        # Connect selection change signals
        self.left_list.itemSelectionChanged.connect(
            self.selection_changed.emit)
        self.right_list.itemSelectionChanged.connect(
            self.selection_changed.emit)

        # Handle double-click to select only that item
        def make_exclusive_handler(this_list, other_list):
            def on_double_click(item):
                other_list.clearSelection()
                this_list.clearSelection()
                item.setSelected(True)
            return on_double_click

        # Handle Ctrl+Click to select all items
        def make_ctrl_click_handler(this_list, other_list):
            def on_item_clicked(item):
                modifiers = QApplication.keyboardModifiers()
                if modifiers == Qt.ControlModifier:
                    this_list.selectAll()
                    other_list.selectAll()
            return on_item_clicked

        self.left_list.itemDoubleClicked.connect(
            make_exclusive_handler(self.left_list, self.right_list))
        self.right_list.itemDoubleClicked.connect(
            make_exclusive_handler(self.right_list, self.left_list))

        self.left_list.itemClicked.connect(
            make_ctrl_click_handler(self.left_list, self.right_list))
        self.right_list.itemClicked.connect(
            make_ctrl_click_handler(self.right_list, self.left_list))

        layout.addWidget(self.left_list)
        layout.addWidget(self.right_list)

    def get_selected_items(self) -> list:
        """Get list of selected item texts"""
        selected = []
        if self.left_list:
            for item in self.left_list.selectedItems():
                if item.text():  # Skip empty padding items
                    selected.append(item.text())
        if self.right_list:
            for item in self.right_list.selectedItems():
                if item.text():  # Skip empty padding items
                    selected.append(item.text())
        return selected

    def set_selected_items(self, items: list):
        """Set selected items by their text values"""
        if not self.left_list or not self.right_list:
            return

        # Clear current selection
        self.left_list.clearSelection()
        self.right_list.clearSelection()

        # Select matching items
        for item_text in items:
            # Check left list
            for i in range(self.left_list.count()):
                item = self.left_list.item(i)
                if item.text() == item_text:
                    item.setSelected(True)
            # Check right list
            for i in range(self.right_list.count()):
                item = self.right_list.item(i)
                if item.text() == item_text:
                    item.setSelected(True)

    def clear_selection(self):
        """Clear all selections"""
        if self.left_list:
            self.left_list.clearSelection()
        if self.right_list:
            self.right_list.clearSelection()

    def select_all(self):
        """Select all items"""
        if self.left_list:
            self.left_list.selectAll()
        if self.right_list:
            self.right_list.selectAll()
