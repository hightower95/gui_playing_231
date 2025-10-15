"""
Mixin class for adding context menu functionality to table views
"""
from PySide6.QtWidgets import QMenu
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
                self.setup_table_context_menu(self.table)
    """

    def setup_table_context_menu(self, table_view, context_actions: Optional[List[Tuple[str, Callable]]] = None):
        """
        Enable context menu for a table view

        Args:
            table_view: QTableView instance to add context menu to
        """
        self.table = table_view
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        self.context_actions = context_actions

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

        # Add menu actions
        open_pdf_action = QAction("Open PDF", self)
        open_pdf_action.triggered.connect(
            lambda: self._on_open_pdf(index, row, column))
        menu.addAction(open_pdf_action)

        # Add custom context actions
        if self.context_actions:
            menu.addSeparator()
            for action_name, action_callback in self.context_actions:
                action = QAction(action_name, self)
                action.triggered.connect(
                    lambda _, cb=action_callback: cb(index, row, column))
                menu.addAction(action)

        menu.addSeparator()

        # Add placeholder TBD actions
        tbd_action1 = QAction("TBD Action 1", self)
        tbd_action1.triggered.connect(
            lambda: self._on_tbd_action(index, row, column, "Action 1"))
        menu.addAction(tbd_action1)

        tbd_action2 = QAction("TBD Action 2", self)
        tbd_action2.triggered.connect(
            lambda: self._on_tbd_action(index, row, column, "Action 2"))
        menu.addAction(tbd_action2)

        tbd_action3 = QAction("TBD Action 3", self)
        tbd_action3.triggered.connect(
            lambda: self._on_tbd_action(index, row, column, "Action 3"))
        menu.addAction(tbd_action3)

        # Show menu at cursor position
        menu.exec(self.table.viewport().mapToGlobal(position))

    def _on_open_pdf(self, index, row, column):
        """
        Handle Open PDF action - override in subclass if needed

        Args:
            index: QModelIndex of the selected cell
            row: Row number of the selected cell
            column: Column number of the selected cell
        """
        model = self.table.model()

        # Get column name if header is available
        column_name = "Unknown"
        if model and hasattr(model, 'headerData'):
            from PySide6.QtCore import Qt
            header_data = model.headerData(column, Qt.Orientation.Horizontal)
            if header_data:
                column_name = header_data

        # Get status label if it exists
        if hasattr(self, 'status_label'):
            self.status_label.setText(
                f"Open PDF for row {row}, column '{column_name}' - Not yet implemented")

        print(
            f"Open PDF requested for row: {row}, column: {column} ({column_name})")

    def _on_tbd_action(self, index, row, column, action_name):
        """
        Handle TBD placeholder actions - override in subclass if needed

        Args:
            index: QModelIndex of the selected cell
            row: Row number of the selected cell
            column: Column number of the selected cell
            action_name: Name of the action being performed
        """
        model = self.table.model()

        # Get column name if header is available
        column_name = "Unknown"
        if model and hasattr(model, 'headerData'):
            from PySide6.QtCore import Qt
            header_data = model.headerData(column, Qt.Orientation.Horizontal)
            if header_data:
                column_name = header_data

        # Get status label if it exists
        if hasattr(self, 'status_label'):
            self.status_label.setText(
                f"{action_name} for row {row}, column '{column_name}' - Not yet implemented")

        print(
            f"{action_name} requested for row: {row}, column: {column} ({column_name})")
