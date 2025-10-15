"""
Connector Lookup Presenter - Mediates between model and view
"""
from PySide6.QtCore import QObject, Signal, QSortFilterProxyModel, Qt, QTimer
from app.connector.Lookup.view import LookupConnectorView
from app.connector.Lookup.config import DEFAULT_VISIBLE_COLUMNS
from app.presenters.pandas_table_model import PandasTableModel
import pandas as pd


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

        # UI Components
        self.table_model = None
        self.proxy = None

        # Connect model signals
        self._connect_model_signals()

        # Connect view signals
        self.view.search_requested.connect(self.on_search)
        self.view.clear_filters_requested.connect(self.on_clear_filters)
        self.view.refresh_requested.connect(self.on_refresh)
        self.view.export_requested.connect(self.on_export)

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
        """Convert connector data to DataFrame"""
        if not data or 'connectors' not in data:
            return pd.DataFrame()

        connectors = data['connectors']
        # Convert dict of connectors to list of records
        records = list(connectors.values())
        return pd.DataFrame(records)

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

    def on_search(self, filters: dict):
        """Handle search with filters"""
        print(f"Searching with filters: {filters}")

        if self.df is None:
            return

        # Apply filters to dataframe
        filtered_df = self.df.copy()

        if filters.get('type'):
            filtered_df = filtered_df[filtered_df['type'].isin(
                filters['type'])]

        if filters.get('gender'):
            filtered_df = filtered_df[filtered_df['gender'].isin(
                filters['gender'])]

        if filters.get('manufacturer'):
            filtered_df = filtered_df[filtered_df['manufacturer'].isin(
                filters['manufacturer'])]

        # Update table
        self.filtered_df = filtered_df
        if self.table_model:
            self.table_model.update(filtered_df)
            self._update_stats()

    def on_clear_filters(self):
        """Handle clear filters"""
        if self.df is not None:
            self.filtered_df = self.df.copy()
            if self.table_model:
                self.table_model.update(self.filtered_df)
                self._update_stats()

    def on_refresh(self):
        """Handle refresh request"""
        self.start_loading()

    def on_export(self):
        """Handle export request"""
        print("Export requested")
        # To be implemented

    def on_row_selected(self, selected, deselected):
        """Handle row selection"""
        if not selected.indexes():
            return

        # Get selected row
        index = selected.indexes()[0]
        row = index.row()

        # Get data from model
        if self.table_model:
            row_data = self.table_model.get_record(row)
            self._update_context_display(row_data)

    def _update_context_display(self, row_data: dict):
        """Update context box with selected connector details"""
        if not row_data:
            return

        details = f"""
Connector Details:
==================
Name: {row_data.get('name', 'N/A')}
Type: {row_data.get('type', 'N/A')}
Gender: {row_data.get('gender', 'N/A')}
Pin Count: {row_data.get('pin_count', 'N/A')}
Manufacturer: {row_data.get('manufacturer', 'N/A')}
Part Number: {row_data.get('part_number', 'N/A')}
"""
        self.view.context_box.setText(details.strip())

    def _update_stats(self):
        """Update statistics display"""
        if self.filtered_df is not None:
            count = len(self.filtered_df)
            self.view.footer_box.setText(f"Showing {count} connector(s)")
            self.view.footer_box.setStyleSheet("")
