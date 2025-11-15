"""
Document Scanner Search View
"""
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton,
                               QLineEdit, QTreeView, QProgressBar, QTextEdit,
                               QWidget, QScrollArea, QFrame, QSizePolicy)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem, QCursor
from ...ui.base_sub_tab_view import BaseTabView
from ...ui.components import StandardLabel, TextStyle, StandardGroupBox
from ...document_scanner.search_result import SearchResult, Context
from ...core.config import UI_COLORS
from typing import List, Dict


class SearchView(BaseTabView):
    """View for document search functionality"""

    # Signals
    search_requested = Signal(str)  # search_term
    reload_requested = Signal()  # reload all documents
    open_document_requested = Signal(str)  # document_name

    def __init__(self, parent=None):
        super().__init__(parent)
        self.results_model = None
        self._setup_ui_content()

    def _setup_ui_content(self):
        """Setup the search UI"""
        # Update header
        self.header_frame.setFixedHeight(100)
        header_layout = QVBoxLayout(self.header_frame)
        header_layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title_label = StandardLabel("Document Search", style=TextStyle.TITLE)
        header_layout.addWidget(title_label)

        # Search input row
        search_row = QHBoxLayout()

        search_row.addWidget(StandardLabel(
            "Search Term:", style=TextStyle.LABEL))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search term...")
        self.search_input.returnPressed.connect(self._on_search)
        search_row.addWidget(self.search_input)

        self.search_btn = QPushButton("🔍 Search All Documents")
        self.search_btn.clicked.connect(self._on_search)
        search_row.addWidget(self.search_btn)

        self.reload_btn = QPushButton("🔄 Reload All Documents")
        self.reload_btn.clicked.connect(self._on_reload_requested)
        self.reload_btn.setToolTip(
            "Reload all documents from disk to pick up any changes")
        search_row.addWidget(self.reload_btn)

        header_layout.addLayout(search_row)

        # Status label
        self.status_label = StandardLabel(
            "Ready - Configure documents in Configuration tab", style=TextStyle.STATUS)
        header_layout.addWidget(self.status_label)

        # Results table in left content
        results_layout = QVBoxLayout(self.left_content_frame)
        results_layout.setContentsMargins(10, 10, 10, 10)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        results_layout.addWidget(self.progress_bar)

        # Results tree view (collapsible by document)
        self.results_tree = QTreeView()
        self.results_tree.setAlternatingRowColors(True)
        self.results_tree.setSelectionBehavior(QTreeView.SelectRows)
        self.results_tree.setExpandsOnDoubleClick(
            False)  # We'll handle double-click ourselves
        self.results_tree.setToolTip(
            "Double-click a result to open the source document")
        self.results_tree.setContextMenuPolicy(Qt.CustomContextMenu)

        # Setup results model
        self.results_model = QStandardItemModel()
        self.results_model.setHorizontalHeaderLabels(['Results'])
        self.results_tree.setModel(self.results_model)
        self.results_tree.header().setStretchLastSection(True)

        # Connect signals
        self.results_tree.selectionModel().selectionChanged.connect(
            self._on_selection_changed)
        self.results_tree.doubleClicked.connect(self._on_result_double_clicked)
        self.results_tree.customContextMenuRequested.connect(
            self._on_context_menu)

        results_layout.addWidget(self.results_tree)

        # Store results for context display
        self.all_results = []  # List[SearchResult]

        # Replace context_box with scrollable collapsible widget area
        # Find the context_box in the parent layout and replace it
        context_frame = self.context_box.parent()
        context_layout_parent = context_frame.layout()

        # Remove the old context_box
        for i in range(context_layout_parent.count()):
            item = context_layout_parent.itemAt(i)
            if item and item.widget() == self.context_box:
                context_layout_parent.removeWidget(self.context_box)
                self.context_box.deleteLater()
                break

        # Create new scrollable area
        self.context_scroll = QScrollArea()
        self.context_scroll.setWidgetResizable(True)
        self.context_scroll.setFrameShape(QFrame.NoFrame)
        self.context_scroll.setStyleSheet(
            f"background-color: {UI_COLORS['section_background']};")

        self.context_content = QWidget()
        self.context_layout = QVBoxLayout(self.context_content)
        self.context_layout.setContentsMargins(5, 5, 5, 5)
        self.context_layout.setSpacing(5)
        self.context_layout.addStretch()

        self.context_scroll.setWidget(self.context_content)

        # Add to the context frame layout
        context_layout_parent.addWidget(self.context_scroll)

    def _on_search(self):
        """Handle search button click"""
        search_term = self.search_input.text().strip()

        if not search_term:
            self.status_label.setText("Please enter a search term")
            self.status_label.setStyleSheet("color: orange; font-size: 10pt;")
            return

        self.search_requested.emit(search_term)

    def _on_reload_requested(self):
        """Handle reload button click"""
        self.reload_requested.emit()

    def _on_selection_changed(self):
        """Handle result selection - display with collapsible contexts"""
        selection = self.results_tree.selectionModel()
        if not selection.hasSelection():
            return

        index = selection.selectedRows()[0]
        item = self.results_model.itemFromIndex(index)

        # Check if item has user data (SearchResult object)
        result = item.data(Qt.UserRole)

        # Check if this is a document header (contains string, not SearchResult)
        if isinstance(result, str) or not hasattr(result, 'matched_row_data'):
            # Document header or other non-result item - clear context panel
            self._clear_context_layout()
            return

        # Clear previous context widgets
        self._clear_context_layout()

        # Show each context as a collapsible section
        if result.has_contexts():
            for ctx in result.contexts:
                self._create_collapsible_context(ctx)
        else:
            # Show message if no context available
            no_context_label = StandardLabel(
                "No additional context available for this result",
                style=TextStyle.LABEL
            )
            no_context_label.setStyleSheet("color: gray; font-style: italic;")
            self.context_layout.addWidget(no_context_label)

        # Add stretch at the end
        self.context_layout.addStretch()

    def _on_result_double_clicked(self, index):
        """Handle double-click on a result - open the source document

        Args:
            index: QModelIndex of the clicked item
        """
        item = self.results_model.itemFromIndex(index)
        if not item:
            return

        # Check if this is a document header
        item_type = item.data(Qt.UserRole + 1)
        if item_type == "document_header":
            # Document header clicked - get document name and open
            doc_name = item.data(Qt.UserRole)
            if doc_name:
                print(f"📂 Double-clicked document header: {doc_name}")
                self.open_document_requested.emit(doc_name)
            return

        # Otherwise, check if it's a result row
        result = item.data(Qt.UserRole)
        if result:
            # Result row clicked - open its document
            self._open_document(result)
        elif item.hasChildren():
            # Some other item with children - expand/collapse it
            if self.results_tree.isExpanded(index):
                self.results_tree.collapse(index)
            else:
                self.results_tree.expand(index)

    def _open_document(self, result: SearchResult):
        """Open the source document in the default application

        Args:
            result: SearchResult containing document information
        """
        print(f"📂 Double-clicked: {result.document_name}")

        # Emit signal for presenter to handle (it has access to document paths)
        self.open_document_requested.emit(result.document_name)

    def _on_context_menu(self, position):
        """Show context menu on right-click

        Args:
            position: Position where the context menu was requested
        """
        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QAction

        # Get the item at the clicked position
        index = self.results_tree.indexAt(position)
        if not index.isValid():
            return

        item = self.results_model.itemFromIndex(index)
        if not item:
            return

        # Check what was clicked
        item_type = item.data(Qt.UserRole + 1)
        result = item.data(Qt.UserRole)

        # Create context menu
        menu = QMenu(self)

        if item_type == "document_header":
            # Document header - offer to open document
            doc_name = result  # For headers, UserRole contains the document name
            if doc_name:
                open_action = QAction(f"📂 Open {doc_name}", self)
                open_action.triggered.connect(
                    lambda: self.open_document_requested.emit(doc_name))
                menu.addAction(open_action)
        elif result and hasattr(result, 'document_name'):
            # Result row - offer to open its document
            open_action = QAction(f"📂 Open {result.document_name}", self)
            open_action.triggered.connect(
                lambda: self.open_document_requested.emit(result.document_name))
            menu.addAction(open_action)

        # Show menu if it has actions
        if not menu.isEmpty():
            menu.exec(self.results_tree.viewport().mapToGlobal(position))

    def _clear_context_layout(self):
        """Remove all widgets from context layout"""
        while self.context_layout.count() > 0:
            item = self.context_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _create_collapsible_context(self, context: Context):
        """Create a collapsible context section using StandardGroupBox"""
        # Create title with term if available
        title = context.context_owner
        if context.term:
            title += f" • '{context.term}'"

        # Use collapsible StandardGroupBox
        group = StandardGroupBox(title, collapsible=True)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(8, 5, 8, 5)
        content_layout.setSpacing(3)

        # Add data if available
        if context.has_data():
            for key, value in context.data_context.items():
                row = QHBoxLayout()
                row.setSpacing(5)

                key_label = StandardLabel(f"{key}:", style=TextStyle.LABEL)
                key_label.setStyleSheet("font-weight: bold;")
                row.addWidget(key_label)

                value_label = StandardLabel(str(value), style=TextStyle.LABEL)
                value_label.setWordWrap(True)
                row.addWidget(value_label, 1)

                content_layout.addLayout(row)

        # Add callback buttons as hyperlinks
        if context.has_callbacks():
            buttons_layout = QHBoxLayout()
            buttons_layout.setSpacing(8)
            buttons_layout.setContentsMargins(0, 5, 0, 0)

            for callback_info in context.callbacks:
                btn = QPushButton(callback_info.label)
                btn.setCursor(QCursor(Qt.PointingHandCursor))
                btn.setFlat(True)
                btn.setStyleSheet("""
                    QPushButton {
                        color: #4a90e2;
                        border: none;
                        text-decoration: underline;
                        padding: 2px 4px;
                        font-size: 9pt;
                        text-align: left;
                        background: transparent;
                    }
                    QPushButton:hover {
                        color: #357abd;
                        font-weight: bold;
                    }
                """)

                if callback_info.tooltip:
                    btn.setToolTip(callback_info.tooltip)

                btn.clicked.connect(callback_info.callback)
                buttons_layout.addWidget(btn)

            buttons_layout.addStretch()
            content_layout.addLayout(buttons_layout)

        group.setLayout(content_layout)
        self.context_layout.addWidget(group)

    def show_progress(self, visible: bool):
        """Show or hide progress bar"""
        self.progress_bar.setVisible(visible)

    def update_progress(self, value: int):
        """Update progress bar value"""
        self.progress_bar.setValue(value)

    def clear_results(self):
        """Clear all results"""
        self.results_model.removeRows(0, self.results_model.rowCount())
        self._clear_context_layout()
        self.all_results = []

    def display_results(self, results: List[SearchResult]):
        """Display search results grouped by document with separate tables per document

        Each document gets its own collapsible section with a table showing only
        the columns that are relevant to that document.

        Args:
            results: List of search results to display
        """
        self.results_model.clear()

        if not results:
            return

        # Group results by document
        grouped: Dict[str, List[SearchResult]] = {}
        for result in results:
            doc_name = result.document_name
            if doc_name not in grouped:
                grouped[doc_name] = []
            grouped[doc_name].append(result)

        # Find maximum number of columns needed across all documents
        max_columns = 0
        for doc_results in grouped.values():
            if doc_results:
                # +1 for row number
                num_cols = len(doc_results[0].matched_row_data.keys()) + 1
                max_columns = max(max_columns, num_cols)

        # Set up model with enough columns
        headers = [""] * max_columns
        self.results_model.setHorizontalHeaderLabels(headers)

        # Create separate table for each document
        for doc_name, doc_results in grouped.items():
            # Document header (collapsible parent)
            doc_header_items = []
            doc_item = QStandardItem(
                f"📄 {doc_name} ({len(doc_results)} result{'s' if len(doc_results) != 1 else ''})")
            doc_item.setEditable(False)
            font = doc_item.font()
            font.setBold(True)
            doc_item.setFont(font)
            # Store document name in UserRole for easy access
            doc_item.setData(doc_name, Qt.UserRole)
            # Mark as document header
            doc_item.setData("document_header", Qt.UserRole + 1)
            doc_item.setToolTip(f"Double-click to open {doc_name}")
            doc_header_items.append(doc_item)

            # Fill remaining columns with empty items
            for _ in range(max_columns - 1):
                empty = QStandardItem("")
                empty.setEditable(False)
                doc_header_items.append(empty)

            self.results_model.appendRow(doc_header_items)

            # Get column names from first result for THIS document
            if doc_results:
                column_names = list(doc_results[0].matched_row_data.keys())

                # Create header row for this document's table
                header_row = []
                header_item = QStandardItem("#")
                header_item.setEditable(False)
                font = header_item.font()
                font.setBold(True)
                header_item.setFont(font)
                header_row.append(header_item)

                for col_name in column_names:
                    col_item = QStandardItem(col_name)
                    col_item.setEditable(False)
                    font = col_item.font()
                    font.setBold(True)
                    col_item.setFont(font)
                    header_row.append(col_item)

                # Fill remaining columns with empty items
                while len(header_row) < max_columns:
                    empty = QStandardItem("")
                    empty.setEditable(False)
                    header_row.append(empty)

                doc_item.appendRow(header_row)

                # Add data rows for this document
                for idx, result in enumerate(doc_results, 1):
                    row = []

                    # Row number with context indicator
                    row_num_text = str(idx)
                    if result.has_contexts():
                        row_num_text += f" 🔍"  # Indicator for results with context
                    num_item = QStandardItem(row_num_text)
                    num_item.setEditable(False)
                    num_item.setData(result, Qt.UserRole)
                    if result.has_contexts():
                        num_item.setToolTip(
                            f"This result has {len(result.contexts)} context item(s)")
                    row.append(num_item)

                    # Data columns (only the columns for THIS document)
                    for col_name in column_names:
                        value = result.matched_row_data.get(col_name, '')
                        value_item = QStandardItem(str(value))
                        value_item.setEditable(False)
                        value_item.setData(result, Qt.UserRole)
                        row.append(value_item)

                    # Fill remaining columns with empty items
                    while len(row) < max_columns:
                        empty = QStandardItem("")
                        empty.setEditable(False)
                        empty.setData(result, Qt.UserRole)
                        row.append(empty)

                    doc_item.appendRow(row)

        # Expand all groups and resize columns
        self.results_tree.expandAll()
        for i in range(max_columns):
            self.results_tree.resizeColumnToContents(i)

    def update_result(self, idx: int, result: SearchResult):
        """Update a specific result in the display (e.g., after context enrichment)

        This is more efficient than redisplaying all results when only one changes.

        Args:
            idx: Index of the result in the all_results list
            result: Updated SearchResult object
        """
        # Update stored result
        if idx < len(self.all_results):
            self.all_results[idx] = result

            # Update the tree display to show context indicator
            self._update_tree_item_for_result(result)

            # If this result is currently selected, update the context display
            current_result = self._get_selected_result()
            if current_result and current_result.search_id == result.search_id:
                self._display_result_details(result)

    def _get_selected_result(self) -> SearchResult:
        """Get the currently selected result

        Returns:
            Selected SearchResult or None
        """
        selection = self.results_tree.selectionModel()
        if not selection.hasSelection():
            return None

        index = selection.selectedRows()[0]
        item = self.results_model.itemFromIndex(index)
        return item.data(Qt.UserRole) if item else None

    def _display_result_details(self, result: SearchResult):
        """Redisplay details for a specific result (used when context updates)

        Args:
            result: SearchResult to display
        """
        # Clear and rebuild context display
        self._clear_context_layout()

        # Show each context as a collapsible section
        if result.has_contexts():
            for ctx in result.contexts:
                self._create_collapsible_context(ctx)
        else:
            # Show message if no context available
            no_context_label = StandardLabel(
                "No additional context available for this result",
                style=TextStyle.LABEL
            )
            no_context_label.setStyleSheet("color: gray; font-style: italic;")
            self.context_layout.addWidget(no_context_label)

        # Add stretch at the end
        self.context_layout.addStretch()

    def _update_tree_item_for_result(self, result: SearchResult):
        """Update the tree item display for a result (e.g., to show context indicator)

        Args:
            result: SearchResult that was updated
        """
        # Walk through all items in the tree to find matching result
        for doc_idx in range(self.results_model.rowCount()):
            doc_item = self.results_model.item(doc_idx, 0)
            if not doc_item:
                continue

            # Check all rows under this document
            for row_idx in range(doc_item.rowCount()):
                # Skip header row (row 0)
                if row_idx == 0:
                    continue

                # Get first column item (row number column)
                row_item = doc_item.child(row_idx, 0)
                if not row_item:
                    continue

                # Check if this is our result
                stored_result = row_item.data(Qt.UserRole)
                if stored_result and stored_result.search_id == result.search_id:
                    # Update the row number text to include context indicator
                    current_text = row_item.text()
                    # Remove existing emoji if present
                    base_num = current_text.split()[0]

                    if result.has_contexts():
                        new_text = f"{base_num} 🔍"
                        row_item.setText(new_text)
                        row_item.setToolTip(
                            f"This result has {len(result.contexts)} context item(s)")
                    else:
                        row_item.setText(base_num)
                        row_item.setToolTip("")

                    return  # Found and updated

    def add_result(self, search_term: str, document: str, matched_data: str):
        """DEPRECATED: Use display_results() instead

        Args:
            search_term: The search term used
            document: Document name where match was found
            matched_data: The matched data (formatted string of column: value pairs)
        """
        # Keep for backward compatibility but log warning
        print("⚠️  add_result() is deprecated, use display_results() instead")

    def update_status(self, message: str, color: str = "gray"):
        """Update status label

        Args:
            message: Status message
            color: Text color (gray, green, orange, red)
        """
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color}; font-size: 10pt;")

    def update_document_count(self, count: int):
        """Update status with document count"""
        if count == 0:
            self.update_status(
                "No documents configured - Go to Configuration tab", "orange")
            self.search_btn.setEnabled(False)
            self.reload_btn.setEnabled(False)
        else:
            self.update_status(
                f"Ready - {count} document(s) configured", "green")
            self.search_btn.setEnabled(True)
            self.reload_btn.setEnabled(True)
