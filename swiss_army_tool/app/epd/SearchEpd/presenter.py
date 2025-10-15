from PySide6.QtCore import QSortFilterProxyModel, Qt, Signal, QObject, QTimer
from app.epd.SearchEpd.view import SearchEpdView
from app.epd.epd_config import DEFAULT_VISIBLE_COLUMNS
from app.presenters.pandas_table_model import PandasTableModel


class SearchEpdPresenter(QObject):
    """Presenter mediating between EpdModel and SearchEpdView."""

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
        self.view = SearchEpdView()

        # Data storage
        self.df = None
        self.is_loading = False

        # UI Components
        self.table_model = None
        self.proxy = None

        # Connect model signals if available
        self._connect_model_signals()

        # Connect view signals
        self.view.searchEPDTriggered.connect(self.on_search)
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
            # Check if model is a QObject and has the signals
            if hasattr(self.model, 'data_loaded') and hasattr(self.model.data_loaded, 'connect'):
                self.model.data_loaded.connect(self._on_model_data_loaded)
                print("Connected to model data_loaded signal")
            else:
                print("Model doesn't have data_loaded signal")

            if hasattr(self.model, 'loading_progress') and hasattr(self.model.loading_progress, 'connect'):
                self.model.loading_progress.connect(
                    self._on_model_loading_progress)
                print("Connected to model loading_progress signal")
            else:
                print("Model doesn't have loading_progress signal")

            if hasattr(self.model, 'loading_failed') and hasattr(self.model.loading_failed, 'connect'):
                self.model.loading_failed.connect(
                    self._on_model_loading_failed)
                print("Connected to model loading_failed signal")
            else:
                print("Model doesn't have loading_failed signal")

        except Exception as e:
            print(f"Error connecting model signals: {e}")
            print(f"Model type: {type(self.model)}")
            print(
                f"Model dir: {[attr for attr in dir(self.model) if not attr.startswith('_')]}")

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
        """Async data loading simulation"""
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
        # self._update_view_statistics()

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

    def on_search(self, text: str):
        """Handle search request"""
        if self.df is None:
            # If no data loaded yet, ignore search
            return

        try:
            # Use model's filter method if available, otherwise filter locally
            if hasattr(self.model, 'filter'):
                filtered = self.model.filter(text)
            else:
                # Simple local filtering fallback
                if text.strip():
                    mask = self.df.astype(str).apply(lambda x: x.str.contains(
                        text, case=False, na=False)).any(axis=1)
                    filtered = self.df[mask]
                else:
                    filtered = self.df

            self.table_model.update(filtered)
            self.data_filtered.emit(filtered)

            # Update the working dataframe for other operations
            self.df = filtered

            # Update view statistics
            self._update_view_statistics()

        except Exception as e:
            print(f"Search error: {e}")
            self.view.show_error(f"Search failed: {str(e)}")

    def on_row_selected(self, selected, _):
        """Handle table row selection"""

        if self.df is None:
            return

        indexes = self.view.table.selectionModel().selectedRows()
        if not indexes:
            return

        try:
            row = indexes[0].row()
            print("row selected")
            # Get the actual dataframe row through the proxy model
            source_row = self.proxy.mapToSource(indexes[0]).row()
            record = self.table_model.get_record(source_row)

            # Display in context and footer areas
            context_text = self._format_context_text(record)
            footer_text = self._format_footer_text(record)

            self.view.display_context(context_text)
            self.view.display_footer(footer_text)

            # Emit selection changed signal
            self.selection_changed.emit(record)

        except Exception as e:
            print(f"Selection error: {e}")

    def _format_context_text(self, record):
        """Format context display text"""
        try:
            return (
                f"EPD: {record.get('EPD', 'N/A')}\n"
                f"Description: {record.get('Description', 'N/A')}\n"
                f"Cable: {record.get('Cable', 'N/A')}\n"
                f"AWG: {record.get('AWG', 'N/A')}"
            )
        except Exception:
            return "Error displaying record details"

    def _format_footer_text(self, record):
        """Format footer display text"""
        try:
            cable = record.get('Cable', 'Unknown')
            awg = record.get('AWG', 'Unknown')
            return f"This EPD uses cable type: {cable} (AWG {awg})"
        except Exception:
            return "Error displaying EPD details"

    # --- Public interface methods ---
    def refresh_data(self):
        """Refresh data from model"""
        if not self.is_loading:
            self.start_loading()

    def get_selected_record(self):
        """Get currently selected record"""
        indexes = self.view.table.selectionModel().selectedRows()
        if not indexes or self.df is None:
            return None

        try:
            source_row = self.proxy.mapToSource(indexes[0]).row()
            return self.table_model.get_record(source_row)
        except Exception:
            return None

    def on_refresh_requested(self):
        """Handle refresh request from view"""
        print("SearchEpd Presenter: Refresh requested")
        if hasattr(self.model, 'refresh_data'):
            self.model.refresh_data()
        else:
            # Fallback to reload
            self.start_loading()

    def on_export_requested(self, file_path: str):
        """Handle export request from view"""
        print(f"SearchEpd Presenter: Export requested to {file_path}")

        if self.df is None or self.df.empty:
            self.view.show_error("No data to export")
            return

        try:
            if hasattr(self.model, 'export_data'):
                success = self.model.export_data(file_path)
            else:
                # Fallback export
                if file_path.endswith('.csv'):
                    self.df.to_csv(file_path, index=False)
                    success = True
                else:
                    success = False

            if success:
                self.view.status_label.setText(f"Data exported to {file_path}")
            else:
                self.view.show_error("Export failed")

        except Exception as e:
            self.view.show_error(f"Export error: {str(e)}")

    def _update_view_statistics(self):
        """Update view with current data statistics"""
        if self.df is not None:
            total_records = len(self.df)
            if hasattr(self.model, 'get_statistics'):
                stats = self.model.get_statistics()
                full_count = stats.get('total_records', total_records)
                self.view.update_record_count(total_records, full_count)
            else:
                self.view.update_record_count(total_records)
