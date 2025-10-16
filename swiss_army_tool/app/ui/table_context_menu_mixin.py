"""
Mixin class for adding context menu functionality to table views
"""
from PySide6.QtWidgets import QMenu, QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from typing import List, Tuple, Callable, Optional


class TableContextMenuMixin:
    """
    Mixin to add right-click context menu functionality to views with tables.

    Usage:
        class MyView(BaseTabView, TableContextMenuMixin):
            def __init__(self):
                super().__init__()
                self.setup_table_context_menu(
                    self.table,
                    actions=[("Action 1", self._handler1), ("Action 2", self._handler2)],
                    include_copy_row=True
                )
    """

    def setup_table_context_menu(
        self,
        table_view,
        actions: Optional[List[Tuple[str, Callable]]] = None,
        include_copy_row: bool = True
    ):
        """
        Enable context menu for a table view

        Args:
            table_view: QTableView instance to add context menu to
            actions: List of (action_name, callback) tuples for custom menu items
            include_copy_row: Whether to include the default "Copy Row" action
        """
        self.table = table_view
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        self.context_actions = actions or []
        self.include_copy_row = include_copy_row

    def _show_context_menu(self, position):
        """Show context menu on right-click in the table"""
        # Get the index at the position
        index = self.table.indexAt(position)
        if not index.isValid():
            return

        # Get row and column information
        row = index.row()
        column = index.column()

        # Create context menu
        menu = QMenu(self)

        # Add default "Copy Row" action if enabled
        if self.include_copy_row:
            copy_part_action = QAction("Copy Row", self)
            copy_part_action.triggered.connect(
                lambda: self._on_copy_row(index, row, column))
            menu.addAction(copy_part_action)

            # Add separator if there are custom actions
            if self.context_actions:
                menu.addSeparator()

        # Add custom context actions
        for action_name, action_callback in self.context_actions:
            action = QAction(action_name, self)
            action.triggered.connect(
                lambda _, cb=action_callback: cb(index, row, column))
            menu.addAction(action)

        # Show menu at cursor position
        menu.exec(self.table.viewport().mapToGlobal(position))

    def _on_copy_row(self, index, row, column):
        """
        Handle Copy Row action - copies entire row as tab-separated values for Excel

        Args:
            index: QModelIndex of the selected cell
            row: Row number of the selected cell
            column: Column number of the selected cell
        """
        model = self.table.model()

        if not model:
            print(f"No model available for row {row}")
            return

        # Collect all column values for this row
        row_data = []
        for col_idx in range(model.columnCount()):
            cell_data = model.data(model.index(row, col_idx))
            # Convert None to empty string, otherwise use string representation
            row_data.append(str(cell_data) if cell_data is not None else "")

        # Join with tabs for Excel compatibility
        row_text = "\t".join(row_data)

        # Copy to clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(row_text)

        # Update status if available
        if hasattr(self, 'footer_box'):
            self.footer_box.setText(
                f"Copied row {row + 1} to clipboard ({len(row_data)} columns)")

        print(f"Copied row {row} to clipboard: {len(row_data)} columns")
