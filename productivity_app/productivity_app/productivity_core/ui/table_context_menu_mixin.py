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

        # Get number of selected rows
        selected_rows = self.table.selectionModel(
        ).selectedRows() if self.table.selectionModel() else []
        num_selected = len(selected_rows)

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
        for action_config in self.context_actions:
            # Support both tuple format (old) and dict format (new)
            if isinstance(action_config, dict):
                action_name = action_config['text']
                action_callback = action_config['callback']
            else:
                # Tuple format: (action_name, action_callback)
                action_name, action_callback = action_config

            action = QAction(action_name, self)
            # For dict format callbacks, don't pass index/row/column
            if isinstance(action_config, dict):
                action.triggered.connect(action_callback)
            else:
                action.triggered.connect(
                    lambda _, cb=action_callback: cb(index, row, column))

            # Disable "Find Alternative" and "Find Opposite" if multiple rows selected
            if action_name in ["Find Alternative", "Find Opposite"] and num_selected != 1:
                action.setEnabled(False)
                action.setToolTip("Select exactly one row to use this action")

            menu.addAction(action)

        # Show menu at cursor position
        menu.exec(self.table.viewport().mapToGlobal(position))

    def _on_copy_row(self, index, row, column):
        """
        Handle Copy Row action - copies all selected rows with headers as tab-separated values for Excel

        Args:
            index: QModelIndex of the selected cell
            row: Row number of the selected cell (not used when multiple rows selected)
            column: Column number of the selected cell
        """
        model = self.table.model()

        if not model:
            print(f"No model available")
            return

        # Get all selected rows
        selected_rows = self.table.selectionModel(
        ).selectedRows() if self.table.selectionModel() else []

        if not selected_rows:
            # Fallback to single row if no selection
            selected_rows = [model.index(row, 0)]

        # Get row numbers and sort them
        row_numbers = sorted([idx.row() for idx in selected_rows])

        # Get column count
        col_count = model.columnCount()

        # Build header row
        headers = []
        for col_idx in range(col_count):
            header_data = model.headerData(col_idx, Qt.Horizontal)
            headers.append(
                str(header_data) if header_data is not None else f"Column {col_idx + 1}")

        # Start with header row
        output_lines = ["\t".join(headers)]

        # Add each selected row
        for row_num in row_numbers:
            row_data = []
            for col_idx in range(col_count):
                cell_data = model.data(model.index(row_num, col_idx))
                # Convert None to empty string, otherwise use string representation
                row_data.append(
                    str(cell_data) if cell_data is not None else "")

            output_lines.append("\t".join(row_data))

        # Join all lines with newlines
        output_text = "\n".join(output_lines)

        # Copy to clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(output_text)

        # Update status if available
        num_rows = len(row_numbers)
        if hasattr(self, 'footer_box'):
            self.footer_box.setText(
                f"Copied {num_rows} row{'s' if num_rows != 1 else ''} with headers to clipboard ({col_count} columns)")

        print(
            f"Copied {num_rows} row(s) with headers to clipboard: {col_count} columns")
