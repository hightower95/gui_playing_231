"""
Connector Lookup Presenter - Mediates between model and view
"""
from PySide6.QtCore import QObject, Signal, QSortFilterProxyModel, Qt, QTimer, QThread
from productivity_core.connector.Lookup.view import LookupConnectorView
from productivity_core.connector.Lookup.config import DEFAULT_VISIBLE_COLUMNS
from productivity_core.presenters.pandas_table_model import PandasTableModel
import pandas as pd


class SearchWorker(QObject):
    """Worker class for performing searches in a background thread"""

    finished = Signal(object)  # filtered DataFrame
    error = Signal(str)  # error message

    def __init__(self, df, filters):
        super().__init__()
        self.df = df
        self.filters = filters
        self._is_cancelled = False

    def cancel(self):
        """Cancel the search operation"""
        self._is_cancelled = True

    def run(self):
        """Execute the search in background thread"""
        try:
            if self._is_cancelled:
                return

            # Apply filters to dataframe
            filtered_df = self.df.copy()

            # Text search filter - supports comma-separated terms
            if self.filters.get('search_text'):
                search_text = self.filters['search_text'].strip()

                # Check if comma-separated (multiple search terms)
                if ',' in search_text:
                    # Split by comma and trim each term
                    search_terms = [term.strip().lower()
                                    for term in search_text.split(',') if term.strip()]

                    # Create OR condition - match any term
                    mask = pd.Series([False] * len(filtered_df),
                                     index=filtered_df.index)
                    for term in search_terms:
                        term_mask = filtered_df.apply(lambda row: row.astype(
                            str).str.lower().str.contains(term, regex=False).any(), axis=1)
                        mask = mask | term_mask

                    filtered_df = filtered_df[mask]
                else:
                    # Single search term
                    search_text = search_text.lower()
                    mask = filtered_df.apply(lambda row: row.astype(
                        str).str.lower().str.contains(search_text, regex=False).any(), axis=1)
                    filtered_df = filtered_df[mask]

            # Standard (Family) filter - multiple selections
            if self.filters.get('standard'):
                standards = [s for s in self.filters['standard'] if s.strip()]
                if standards:
                    filtered_df = filtered_df[filtered_df['Family'].isin(
                        standards)]

            # Shell Type filter - multiple selections
            if self.filters.get('shell_type'):
                shell_types = [
                    st for st in self.filters['shell_type'] if st.strip()]
                if shell_types:
                    filtered_df = filtered_df[filtered_df['Shell Type'].isin(
                        shell_types)]

            # Material filter - multiple selections
            if self.filters.get('material'):
                materials = [m for m in self.filters['material'] if m.strip()]
                if materials:
                    filtered_df = filtered_df[filtered_df['Material'].isin(
                        materials)]

            # Shell Size filter - multiple selections
            if self.filters.get('shell_size'):
                shell_sizes = [
                    ss for ss in self.filters['shell_size'] if ss.strip()]
                if shell_sizes:
                    filtered_df = filtered_df[filtered_df['Shell Size'].isin(
                        shell_sizes)]

            # Insert Arrangement filter - multiple selections
            if self.filters.get('insert_arrangement'):
                insert_arrangements = [
                    ia for ia in self.filters['insert_arrangement'] if ia.strip()]
                if insert_arrangements:
                    filtered_df = filtered_df[filtered_df['Insert Arrangement'].isin(
                        insert_arrangements)]

            # Socket Type filter - multiple selections
            if self.filters.get('socket_type'):
                socket_types = [
                    st for st in self.filters['socket_type'] if st.strip()]
                if socket_types:
                    filtered_df = filtered_df[filtered_df['Socket Type'].isin(
                        socket_types)]

            # Keying filter - multiple selections
            if self.filters.get('keying'):
                keyings = [k for k in self.filters['keying'] if k.strip()]
                if keyings:
                    filtered_df = filtered_df[filtered_df['Keying'].isin(
                        keyings)]

            if self._is_cancelled:
                return

            self.finished.emit(filtered_df)

        except Exception as e:
            self.error.emit(f"Search failed: {str(e)}")


class LookupConnectorPresenter(QObject):
    """Presenter for connector lookup functionality"""

    # Signals
    loading_started = Signal()
    loading_progress = Signal(int, str)
    loading_completed = Signal()
    loading_failed = Signal(str)
    data_loaded = Signal(object)

    def __init__(self, context, connector_model):
        super().__init__()
        self.context = context
        self.model = connector_model
        self.view = LookupConnectorView()

        # Data storage
        self.df = None
        self.filtered_df = None
        self.is_loading = False
        self.current_filters = {}  # Track current search filters

        # Search threading
        self._search_worker = None
        self._search_thread = None

        # UI Components
        self.table_model = None
        self.proxy = None

        # Connect model signals
        self._connect_model_signals()

        # Connect view signals
        self.view.search_requested.connect(self.on_search)
        self.view.standards_changed.connect(self.on_standards_changed)
        self.view.clear_filters_requested.connect(self.on_clear_filters)
        self.view.refresh_requested.connect(self.on_refresh)
        self.view.export_requested.connect(self.on_export)
        self.view.reset_requested.connect(self.on_reset)
        self.view.find_alternative_requested.connect(self.on_find_alternative)
        self.view.find_opposite_requested.connect(self.on_find_opposite)

        # Setup UI components
        self._setup_ui_components()

        # Connect internal signals
        self.data_loaded.connect(self._on_data_ready)

        # Connect loading signals to view
        self.loading_started.connect(lambda: self.view.show_loading(True))
        self.loading_progress.connect(self.view.update_loading_progress)
        self.loading_completed.connect(lambda: self.view.show_loading(False))
        self.loading_failed.connect(self.view.show_error)

    def _connect_model_signals(self):
        """Connect to model signals"""
        try:
            if hasattr(self.model, 'data_loaded'):
                self.model.data_loaded.connect(self._on_model_data_loaded)

            if hasattr(self.model, 'loading_progress'):
                self.model.loading_progress.connect(
                    self._on_model_loading_progress)

            if hasattr(self.model, 'loading_failed'):
                self.model.loading_failed.connect(
                    self._on_model_loading_failed)

        except Exception as e:
            print(f"Error connecting model signals: {e}")

    def _on_model_data_loaded(self, data):
        """Handle data loaded from model"""
        print("Connector data loaded from model")
        self.df = self._convert_to_dataframe(data)
        self.data_loaded.emit(self.df)

    def _on_model_loading_progress(self, percent: int, message: str):
        """Forward loading progress"""
        self.loading_progress.emit(percent, message)

    def _on_model_loading_failed(self, error_message: str):
        """Forward loading failure"""
        self.loading_failed.emit(error_message)

    def _setup_ui_components(self):
        """Setup UI components"""
        # Create proxy model for sorting/filtering
        self.proxy = QSortFilterProxyModel()
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy.setFilterKeyColumn(-1)

        # Configure table view
        self.view.table.setModel(self.proxy)

    def _on_data_ready(self, data):
        """Handle when data is ready for UI"""
        # Create table model with loaded data
        self.table_model = PandasTableModel(data)
        self.proxy.setSourceModel(self.table_model)

        # Apply column visibility settings
        self._apply_column_visibility()

        # Connect selection signal
        if self.view.table.selectionModel():
            self.view.table.selectionModel().selectionChanged.connect(self.on_row_selected)
            self.view.table.selectionModel().selectionChanged.connect(self.on_selection_changed)

        # Update stats
        self._update_stats()

    def _apply_column_visibility(self):
        """Apply default column visibility settings"""
        if self.table_model is None:
            return

        # Get all columns from the dataframe
        all_columns = self.table_model._data.columns.tolist()

        # Hide columns that are not in DEFAULT_VISIBLE_COLUMNS
        for col_index, col_name in enumerate(all_columns):
            if col_name not in DEFAULT_VISIBLE_COLUMNS:
                self.view.table.setColumnHidden(col_index, True)
            else:
                self.view.table.setColumnHidden(col_index, False)

    def _convert_to_dataframe(self, data: dict) -> pd.DataFrame:
        """Convert connector data to DataFrame, limiting to first 100 results"""
        if not data or 'connectors' not in data:
            return pd.DataFrame()

        connectors = data['connectors']

        # Limit to 100 connectors to avoid sending too much data to GUI
        limited_connectors = connectors[:100]

        # Log if we're limiting
        if len(connectors) > 100:
            print(
                f"Limited connector data from {len(connectors)} to 100 records for initial display")

        # Connectors is now a list of dictionaries
        return pd.DataFrame(limited_connectors)

    def start_loading(self):
        """Start loading connector data"""
        if self.is_loading:
            return

        self.is_loading = True
        self.loading_started.emit()

        # Trigger model to load data
        if hasattr(self.model, 'load_async'):
            self.model.load_async()
        else:
            # Fallback
            data = self.model.get_all()
            if data:
                self._on_model_data_loaded(data)

    def on_standards_changed(self, selected_standards: list):
        """Handle change in selected standards - update available filter options

        Args:
            selected_standards: List of selected standard names (e.g., ['D38999', 'VG'])
        """
        print(f"Standards changed: {selected_standards}")

        # Get available filter options from model based on selected standards
        if hasattr(self.model, 'get_available_filter_options'):
            filter_options = self.model.get_available_filter_options(
                selected_standards)

            # Update view with new filter options
            self.view.update_filter_options(filter_options)

            print(f"Updated filter options: {filter_options}")
            data = self.model.get_all()
            if data:
                self._on_model_data_loaded(data)

    def on_search(self, filters: dict):
        """Handle search with filters - runs asynchronously"""
        print(f"Searching with filters: {filters}")

        if self.df is None:
            return

        # Store current filters for history tracking
        self.current_filters = filters.copy()

        # Cancel any existing search
        if self._search_worker is not None:
            self._search_worker.cancel()
            if self._search_thread is not None and self._search_thread.isRunning():
                self._search_thread.quit()
                self._search_thread.wait()

        # Create worker and thread for async search
        self._search_worker = SearchWorker(self.df, filters)
        self._search_thread = QThread()

        # Move worker to thread
        self._search_worker.moveToThread(self._search_thread)

        # Connect signals
        self._search_thread.started.connect(self._search_worker.run)
        self._search_worker.finished.connect(self._on_search_finished)
        self._search_worker.error.connect(self._on_search_error)
        self._search_worker.finished.connect(self._search_thread.quit)
        self._search_worker.error.connect(self._search_thread.quit)

        # Start search
        self._search_thread.start()

    def _on_search_finished(self, filtered_df):
        """Handle search completion"""
        self.filtered_df = filtered_df
        if self.table_model:
            self.table_model.update(filtered_df)
            self._update_stats()

            # Add to search history with first result info
            result_count = len(filtered_df)
            first_result = None
            if result_count > 0:
                # Get first row data
                first_row = filtered_df.iloc[0]
                first_result = {
                    'Part Number': first_row.get('Part Number', ''),
                    'Part Code': first_row.get('Part Code', '')
                }

            self.view.add_search_to_history(
                self.current_filters, result_count, first_result)

    def _on_search_error(self, error_message: str):
        """Handle search error"""
        self.view.show_error(error_message)

    def on_clear_filters(self):
        """Handle clear filters"""
        if self.df is not None:
            self.filtered_df = self.df.copy()
            if self.table_model:
                self.table_model.update(self.filtered_df)
                self._update_stats()

    def on_reset(self):
        """Handle reset request - clear filters and show all results like initial state"""
        # Reset to show all data (like initial state)
        if self.df is not None:
            self.filtered_df = self.df.copy()
            if self.table_model:
                self.table_model.update(self.filtered_df)
                self._update_stats()

        # Clear context display
        self.view.context_box.clear()

    def on_refresh(self):
        """Handle refresh request"""
        self.start_loading()

    def on_export(self):
        """Handle export request"""
        print("Export requested")
        # To be implemented

    def on_row_selected(self, selected, deselected):
        """Handle row selection - update context display"""
        if not selected.indexes():
            return

        # Get selected row
        index = selected.indexes()[0]
        row = index.row()

        # Get data from model
        if self.table_model:
            row_data = self.table_model.get_record(row)
            self._update_context_display(row_data)

    def on_selection_changed(self, selected, deselected):
        """Handle selection change - update button states"""
        self.view.update_context_buttons_state()

    def on_find_alternative(self, part_code: str):
        """Handle find alternative request

        Args:
            part_code: The part code to find alternatives for
        """
        print(f"Presenter: Finding alternative for {part_code}")

        if self.df is None:
            return

        # Get the original record
        original_record = self.df[self.df['Part Code'] == part_code]
        if original_record.empty:
            print(f"Could not find original record for {part_code}")
            return

        # Call model method to get alternatives
        if hasattr(self.model, 'find_alternative'):
            alternatives = self.model.find_alternative(part_code)
            print(f"Found {len(alternatives)} alternatives")

            # Convert alternatives to DataFrame
            alternatives_df = pd.DataFrame(
                alternatives) if alternatives else pd.DataFrame()

            # Combine original record with alternatives
            # Original record first, then alternatives
            if not alternatives_df.empty:
                combined_df = pd.concat(
                    [original_record, alternatives_df], ignore_index=True)
            else:
                combined_df = original_record.copy()

            # Update table with combined results
            self.filtered_df = combined_df
            if self.table_model:
                self.table_model.update(combined_df)
                self._update_stats()

            # Add to search history with special description
            result_count = len(combined_df)
            first_result = None
            if result_count > 0:
                first_row = combined_df.iloc[0]
                first_result = {
                    'Part Number': first_row.get('Part Number', ''),
                    'Part Code': first_row.get('Part Code', '')
                }

            # Create special filters dict for history
            special_filters = {
                'search_text': f"Alternative to {part_code}",
                '_special_action': 'find_alternative'  # Mark as special action
            }

            self.view.add_search_to_history(
                special_filters, result_count, first_result)
        else:
            print("Model does not support find_alternative")

    def on_find_opposite(self, part_code: str):
        """Handle find opposite request

        Args:
            part_code: The part code to find opposite for
        """
        print(f"Presenter: Finding opposite for {part_code}")

        if self.df is None:
            return

        # Get the original record
        original_record = self.df[self.df['Part Code'] == part_code]
        if original_record.empty:
            print(f"Could not find original record for {part_code}")
            return

        # Call model method to get opposite
        if hasattr(self.model, 'find_opposite'):
            opposite = self.model.find_opposite(part_code)
            print(f"Found opposite: {opposite}")

            # Convert opposite to DataFrame
            if opposite:
                opposite_df = pd.DataFrame([opposite])
                # Combine original record with opposite
                combined_df = pd.concat(
                    [original_record, opposite_df], ignore_index=True)
            else:
                # No opposite found, just show original
                combined_df = original_record.copy()

            # Update table with combined results
            self.filtered_df = combined_df
            if self.table_model:
                self.table_model.update(combined_df)
                self._update_stats()

            # Add to search history with special description
            result_count = len(combined_df)
            first_result = None
            if result_count > 0:
                first_row = combined_df.iloc[0]
                first_result = {
                    'Part Number': first_row.get('Part Number', ''),
                    'Part Code': first_row.get('Part Code', '')
                }

            # Create special filters dict for history
            special_filters = {
                'search_text': f"Opposite to {part_code}",
                '_special_action': 'find_opposite'  # Mark as special action
            }

            self.view.add_search_to_history(
                special_filters, result_count, first_result)
        else:
            print("Model does not support find_opposite")

    def _update_context_display(self, row_data: dict):
        """Update context box with selected connector details"""
        if not row_data:
            return

        details = f"""
Connector Details:
==================
Part Number: {row_data.get('Part Number', 'N/A')}
Part Code: {row_data.get('Part Code', 'N/A')}
Material: {row_data.get('Material', 'N/A')}
Database Status: {row_data.get('Database Status', 'N/A')}

Family: {row_data.get('Family', 'N/A')}
Shell Type: {row_data.get('Shell Type', 'N/A')}
Insert Arrangement: {row_data.get('Insert Arrangement', 'N/A')}
Socket Type: {row_data.get('Socket Type', 'N/A')}
Keying: {row_data.get('Keying', 'N/A')}
"""
        self.view.context_box.setText(details.strip())

    def _update_stats(self):
        """Update statistics display"""
        if self.filtered_df is not None:
            count = len(self.filtered_df)
            total = len(self.df) if self.df is not None else 0
            self.view.record_count_label.setText(
                f"Showing {count} of {total} connectors from database")
