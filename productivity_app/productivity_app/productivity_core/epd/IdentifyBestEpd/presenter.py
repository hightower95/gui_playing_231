from PySide6.QtCore import QSortFilterProxyModel, Qt, Signal, QObject, QTimer
from productivity_core.epd.IdentifyBestEpd.view import IdentifyBestEpdView
from productivity_core.epd.epd_config import DEFAULT_VISIBLE_COLUMNS
from productivity_core.presenters.pandas_table_model import PandasTableModel
import pandas as pd


class IdentifyBestEpdPresenter(QObject):
    """Presenter for identifying the best EPD based on filters."""

    # Signals for loading process
    loading_started = Signal()
    loading_progress = Signal(int, str)  # progress_percent, status_message
    loading_completed = Signal()
    loading_failed = Signal(str)  # error_message

    # Data signals
    data_loaded = Signal(object)  # dataframe
    data_filtered = Signal(object)  # filtered dataframe
    selection_changed = Signal(dict)  # selected record

    def __init__(self, context, epd_model):
        super().__init__()
        self.context = context
        self.model = epd_model
        self.view = IdentifyBestEpdView()

        # Data storage
        self.df = None
        self.filtered_df = None
        self.is_loading = False
        self.active_filters = []

        # UI Components
        self.table_model = None
        self.proxy = None

        # Connect model signals if available
        self._connect_model_signals()

        # Connect view signals
        self.view.filter_added.connect(self.on_filter_added)
        self.view.filter_removed.connect(self.on_filter_removed)
        self.view.clear_filters.connect(self.on_clear_filters)
        self.view.apply_filters.connect(self.on_apply_filters)
        self.view.refresh_requested.connect(self.on_refresh_requested)
        self.view.export_requested.connect(self.on_export_requested)

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
        """Safely connect to model signals"""
        try:
            if hasattr(self.model, 'data_loaded') and hasattr(self.model.data_loaded, 'connect'):
                self.model.data_loaded.connect(self._on_model_data_loaded)
                print("IdentifyBestEpd: Connected to model data_loaded signal")
            else:
                print("IdentifyBestEpd: Model doesn't have data_loaded signal")

            if hasattr(self.model, 'loading_progress') and hasattr(self.model.loading_progress, 'connect'):
                self.model.loading_progress.connect(
                    self._on_model_loading_progress)
                print("IdentifyBestEpd: Connected to model loading_progress signal")
            else:
                print("IdentifyBestEpd: Model doesn't have loading_progress signal")

            if hasattr(self.model, 'loading_failed') and hasattr(self.model.loading_failed, 'connect'):
                self.model.loading_failed.connect(
                    self._on_model_loading_failed)
                print("IdentifyBestEpd: Connected to model loading_failed signal")
            else:
                print("IdentifyBestEpd: Model doesn't have loading_failed signal")

        except Exception as e:
            print(f"IdentifyBestEpd: Error connecting model signals: {e}")

    def _setup_ui_components(self):
        """Setup UI components that don't require data"""
        # Create proxy model for sorting/filtering
        self.proxy = QSortFilterProxyModel()
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy.setFilterKeyColumn(-1)

        # Configure table view
        self.view.table.setModel(self.proxy)
        self.view.table.setSortingEnabled(True)
        self.view.table.setSelectionBehavior(
            self.view.table.SelectionBehavior.SelectRows)
        self.view.table.setSelectionMode(
            self.view.table.SelectionMode.SingleSelection)

    def start_loading(self):
        """Start the data loading process"""
        if self.is_loading:
            return

        self.is_loading = True
        self.loading_started.emit()
        self.loading_progress.emit(0, "Initializing data load...")

        # Use QTimer to simulate async loading or call model's async method
        QTimer.singleShot(100, self._load_data_async)

    def _load_data_async(self):
        """Async data loading"""
        try:
            self.loading_progress.emit(25, "Connecting to data source...")

            # Load data from model
            if hasattr(self.model, 'load_async'):
                # If model supports async loading
                self.model.load_async()
            else:
                # Fallback to synchronous loading
                self.loading_progress.emit(50, "Loading EPD data...")
                data = self.model.get_all()
                self.loading_progress.emit(75, "Processing data...")
                self._on_model_data_loaded(data)

        except Exception as e:
            self.loading_failed.emit(f"Failed to load data: {str(e)}")
            self.is_loading = False

    def _on_model_data_loaded(self, data):
        """Handle data loaded from model"""
        self.loading_progress.emit(90, "Finalizing data setup...")
        self.df = data
        self.filtered_df = data.copy()  # Start with all data
        self.data_loaded.emit(data)
        self.loading_progress.emit(100, "Data loading completed")
        self.loading_completed.emit()
        self.is_loading = False

    def _on_model_loading_progress(self, progress, message):
        """Forward model loading progress"""
        self.loading_progress.emit(progress, message)

    def _on_model_loading_failed(self, error_message):
        """Handle model loading failure"""
        self.loading_failed.emit(error_message)
        self.is_loading = False

    def _on_data_ready(self, data):
        """Handle when data is ready for UI"""
        # Create table model with loaded data
        self.table_model = PandasTableModel(data)
        self.proxy.setSourceModel(self.table_model)

        # Apply column visibility settings
        self._apply_column_visibility()

        # Connect selection signal now that we have data
        if self.view.table.selectionModel():
            self.view.table.selectionModel().selectionChanged.connect(self.on_row_selected)

        # Update view statistics
        self._update_view_statistics()

    def _apply_column_visibility(self):
        """Apply default column visibility settings from config"""
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

    def on_filter_added(self, field: str, operator: str, value: str):
        """Handle filter addition"""
        filter_dict = {
            'field': field,
            'operator': operator,
            'value': value
        }

        # Add to active filters if not duplicate
        if filter_dict not in self.active_filters:
            self.active_filters.append(filter_dict)

        print(f"Filter added: {field} {operator} {value}")

        # Auto-apply filters
        self._apply_current_filters()

    def on_filter_removed(self, filter_data: dict):
        """Handle filter removal"""
        if filter_data in self.active_filters:
            self.active_filters.remove(filter_data)

        print(f"Filter removed: {filter_data}")

        # Re-apply remaining filters
        self._apply_current_filters()

    def on_clear_filters(self):
        """Handle clearing all filters"""
        self.active_filters.clear()
        print("All filters cleared")

        # Reset to original data
        if self.df is not None:
            self.filtered_df = self.df.copy()
            self.table_model.update(self.filtered_df)
            self._update_view_statistics()

    def on_apply_filters(self):
        """Handle explicit filter application"""
        self._apply_current_filters()

    def _apply_current_filters(self):
        """Apply all current filters to the data"""
        if self.df is None or not self.active_filters:
            if len(self.active_filters) == 0 and self.df is not None:
                self.filtered_df = self.df.copy()
                if self.table_model:
                    self.table_model.update(self.filtered_df)
                    self._update_view_statistics()
            return

        try:
            filtered_data = self.df.copy()

            for filter_item in self.active_filters:
                field = filter_item['field']
                operator = filter_item['operator']
                value = filter_item['value']

                filtered_data = self._apply_single_filter(
                    filtered_data, field, operator, value)

            self.filtered_df = filtered_data

            # Update table
            if self.table_model:
                self.table_model.update(filtered_data)

            # Update statistics
            self._update_view_statistics()

            # Update context with best recommendation
            self._update_best_recommendation()

            print(
                f"Applied {len(self.active_filters)} filters, {len(filtered_data)} results")

        except Exception as e:
            self.view.show_error(f"Filter application failed: {str(e)}")
            print(f"Filter error: {e}")

    def _apply_single_filter(self, data: pd.DataFrame, field: str, operator: str, value: str):
        """Apply a single filter to the data"""
        if field not in data.columns:
            return data

        # Convert value to appropriate type for numeric comparisons
        numeric_value = None
        try:
            numeric_value = float(value)
        except ValueError:
            pass

        if operator == "equals":
            if numeric_value is not None:
                return data[data[field] == numeric_value]
            else:
                return data[data[field].astype(str).str.lower() == value.lower()]

        elif operator == "not equals":
            if numeric_value is not None:
                return data[data[field] != numeric_value]
            else:
                return data[data[field].astype(str).str.lower() != value.lower()]

        elif operator == "contains":
            return data[data[field].astype(str).str.contains(value, case=False, na=False)]

        elif operator == "not contains":
            return data[~data[field].astype(str).str.contains(value, case=False, na=False)]

        elif operator == "less than":
            if numeric_value is not None:
                return data[pd.to_numeric(data[field], errors='coerce') < numeric_value]
            else:
                return data[data[field].astype(str) < value]

        elif operator == "greater than":
            if numeric_value is not None:
                return data[pd.to_numeric(data[field], errors='coerce') > numeric_value]
            else:
                return data[data[field].astype(str) > value]

        elif operator == "less than or equal":
            if numeric_value is not None:
                return data[pd.to_numeric(data[field], errors='coerce') <= numeric_value]
            else:
                return data[data[field].astype(str) <= value]

        elif operator == "greater than or equal":
            if numeric_value is not None:
                return data[pd.to_numeric(data[field], errors='coerce') >= numeric_value]
            else:
                return data[data[field].astype(str) >= value]

        return data

    def _update_best_recommendation(self):
        """Update the context with best EPD recommendation"""
        if self.filtered_df is None or self.filtered_df.empty:
            self.view.display_footer("No EPDs match the current filters.")
            return

        # Simple scoring logic - can be enhanced
        best_epd = self.filtered_df.iloc[0]  # First result for now

        recommendation_text = (
            f"RECOMMENDED EPD: {best_epd.get('EPD', 'N/A')}\n\n"
            f"Based on your filters, this EPD best matches your criteria:\n"
            f"• Description: {best_epd.get('Description', 'N/A')}\n"
            f"• Cable Type: {best_epd.get('Cable', 'N/A')}\n"
            f"• AWG Rating: {best_epd.get('AWG', 'N/A')}\n\n"
            f"Found {len(self.filtered_df)} total options matching your criteria."
        )

        self.view.display_footer(recommendation_text)

    def on_row_selected(self, selected, _):
        """Handle table row selection"""
        if self.filtered_df is None:
            return

        indexes = self.view.table.selectionModel().selectedRows()
        if not indexes:
            return

        try:
            row = indexes[0].row()
            source_row = self.proxy.mapToSource(indexes[0]).row()
            record = self.table_model.get_record(source_row)

            # Display detailed information
            context_text = self._format_context_text(record)
            self.view.display_context(context_text)

            # Emit selection changed signal
            self.selection_changed.emit(record)

        except Exception as e:
            print(f"Selection error: {e}")

    def _format_context_text(self, record):
        """Format context display text for selected EPD"""
        try:
            return (
                f"SELECTED EPD DETAILS\n"
                f"{'='*40}\n\n"
                f"EPD Code: {record.get('EPD', 'N/A')}\n"
                f"Description: {record.get('Description', 'N/A')}\n"
                f"Cable Type: {record.get('Cable', 'N/A')}\n"
                f"AWG Rating: {record.get('AWG', 'N/A')}\n\n"
                f"COMPATIBILITY ANALYSIS\n"
                f"{'='*40}\n"
                f"This EPD meets your specified criteria and can be used "
                f"for applications requiring {record.get('Cable', 'unknown')} cable "
                f"with AWG {record.get('AWG', 'unknown')} specifications."
            )
        except Exception:
            return "Error displaying EPD details"

    def on_refresh_requested(self):
        """Handle refresh request from view"""
        print("IdentifyBestEpd: Refresh requested")
        if hasattr(self.model, 'refresh_data'):
            self.model.refresh_data()
        else:
            self.start_loading()

    def on_export_requested(self, file_path: str):
        """Handle export request from view"""
        print(f"IdentifyBestEpd: Export requested to {file_path}")

        export_data = self.filtered_df if self.filtered_df is not None else self.df

        if export_data is None or export_data.empty:
            self.view.show_error("No data to export")
            return

        try:
            if hasattr(self.model, 'export_data'):
                success = self.model.export_data(file_path, export_data)
            else:
                # Fallback export
                if file_path.endswith('.csv'):
                    export_data.to_csv(file_path, index=False)
                    success = True
                else:
                    success = False

            if success:
                record_count = len(export_data)
                self.view.status_label.setText(
                    f"Exported {record_count} records to {file_path}")
            else:
                self.view.show_error("Export failed")

        except Exception as e:
            self.view.show_error(f"Export error: {str(e)}")

    def _update_view_statistics(self):
        """Update view with current data statistics"""
        if self.filtered_df is not None:
            filtered_count = len(self.filtered_df)
            total_count = len(
                self.df) if self.df is not None else filtered_count
            self.view.update_record_count(filtered_count, total_count)

    def get_filtered_data(self):
        """Get the current filtered dataset"""
        return self.filtered_df

    def get_active_filters(self):
        """Get list of active filters"""
        return self.active_filters.copy()

    def refresh_data(self):
        """Public method to refresh data"""
        if not self.is_loading:
            self.start_loading()
