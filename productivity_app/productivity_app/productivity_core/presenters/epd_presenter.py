"""
EPD Presenter - Business logic for EPD analysis
"""
from PySide6.QtCore import QAbstractTableModel, Qt, QSortFilterProxyModel, QModelIndex
from swiss_army_tool.app.epd.epd_tab import EpdView
from swiss_army_tool.app.epd.epd_model import EpdModel
from productivity_core.core.base_presenter import BasePresenter
import pandas as pd


class PandasTableModel(QAbstractTableModel):
    """Adapter to show a Pandas DataFrame in a QTableView."""

    def __init__(self, df):
        super().__init__()
        self._data = df

    def update(self, df):
        self.beginResetModel()
        self._data = df
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._data.columns)

    def data(self, index, role):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        return str(self._data.iat[index.row(), index.column()])

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return str(self._data.columns[section])
        return str(section + 1)


class EpdProxyModel(QSortFilterProxyModel):
    """Custom proxy model for sorting & filtering EPD data."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_text = ""
        self.min_rating = 0
        self.max_awg = 40

    def set_filters(self, search_text, min_rating, max_awg):
        self.search_text = search_text.lower()
        self.min_rating = min_rating
        self.max_awg = max_awg
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        df = model._data

        if df is None or source_row >= len(df):
            return False

        row = df.iloc[source_row]

        # Apply text search (any column)
        if self.search_text:
            if not any(self.search_text in str(v).lower() for v in row.values):
                return False

        # Apply numeric filters
        if row["Rating (A)"] < self.min_rating:
            return False
        if row["AWG"] > self.max_awg:
            return False

        return True


class EpdPresenter(BasePresenter):
    def __init__(self, context):
        self.model = EpdModel(context)
        self.view = EpdView()
        super().__init__(context, self.view, self.model, title="Search EPD")

        # Create the table model
        df = self.model.get_all()
        self.table_model = PandasTableModel(df)

        # Proxy for sorting/filtering
        self.proxy = EpdProxyModel()
        self.proxy.setSourceModel(self.table_model)

        # Connect proxy to the view
        self.view.set_table_model(self.proxy)

        self.bind()

    def bind(self):
        # Connect search box signal -> filtering logic
        self.view.searchTextChanged.connect(self.update_filters)
        self.view.minRatingChanged.connect(self.update_filters)
        self.view.maxAwgChanged.connect(self.update_filters)
        self.view.resetFiltersClicked.connect(self.reset_filters)

    def reset_filters(self, *_):
        """Reset all filters to default values."""
        self.view.search_box.setText("")
        self.view.min_rating.setValue(0)
        self.view.max_awg.setValue(40)
        self.update_filters()

    def update_filters(self, *_):
        """Gather filters from view and apply to proxy."""
        text = self.view.search_box.text()
        min_rating = self.view.min_rating.value()
        max_awg = self.view.max_awg.value()
        self.proxy.set_filters(text, min_rating, max_awg)

    # def on_search_text_changed(self, text):
    #     """Handle user typing in search box."""
    #     filtered = self.model.filter(text)
    #     self.table_model.update(filtered)

# class EpdPresenter(BasePresenter):
#     """Presenter for EPD analysis functionality"""

#     def __init__(self, context: AppContext):
#         super().__init__(context)
#         self.model = EpdModel(context)
#         self._connect_model_signals()

#     def _initialize(self):
#         """Initialize the EPD presenter"""
#         # Load initial data
#         self.model.load_data()
#         print("EPD Presenter initialized")

#     def _connect_model_signals(self):
#         """Connect to model signals"""
#         self.model.data_updated.connect(self._on_model_data_updated)
#         self.model.data_loaded.connect(self._on_model_data_loaded)

#     def handle_breakout_wire_selection(self, breakout_wire_name: str):
#         """Handle breakout wire selection from view"""
#         print(f"EPD Presenter: Breakout wire selected - {breakout_wire_name}")

#         # Update model with current selection
#         self.model.set_current_breakout_wire(breakout_wire_name)

#         # Get breakout wire data
#         breakout_wire_data = self.model.get_breakout_wire_data(breakout_wire_name)

#         # Process and emit data changes
#         if breakout_wire_data:
#             self.data_changed.emit({
#                 'type': 'breakout_wire_selected',
#                 'breakout_wire': breakout_wire_name,
#                 'data': breakout_wire_data
#             })

#             # Update application state
#             self.context.set_state('current_breakout_wire', breakout_wire_name)

#             self.complete_operation(f"breakout_wire_selection_{breakout_wire_name}")
#         else:
#             self.handle_error(f"No data found for breakout wire: {breakout_wire_name}")

#     def handle_connection_selection(self, breakout_wire_name: str, connection_name: str):
#         """Handle connection selection from view"""
#         print(f"EPD Presenter: Connection selected - {breakout_wire_name}.{connection_name}")

#         # Update model with current selection
#         self.model.set_current_connection(breakout_wire_name, connection_name)

#         # Get connection data
#         connection_data = self.model.get_connection_data(breakout_wire_name, connection_name)

#         # Process and emit data changes
#         if connection_data:
#             self.data_changed.emit({
#                 'type': 'connection_selected',
#                 'breakout_wire': breakout_wire_name,
#                 'connection': connection_name,
#                 'data': connection_data
#             })

#             # Update application state
#             self.context.set_state('current_breakout_wire', breakout_wire_name)
#             self.context.set_state('current_connection', connection_name)

#             self.complete_operation(f"connection_selection_{breakout_wire_name}_{connection_name}")
#         else:
#             self.handle_error(f"No data found for connection: {breakout_wire_name}.{connection_name}")

#     def update_breakout_wire_pin_data(self, breakout_wire_name: str, pin_data: dict):
#         """Update breakout wire pin data"""
#         print(f"EPD Presenter: Updating pin data for {breakout_wire_name}")

#         try:
#             self.model.update_breakout_wire_pin_data(breakout_wire_name, pin_data)
#             self.complete_operation(f"update_pin_data_{breakout_wire_name}")
#         except Exception as e:
#             self.handle_error(f"Failed to update pin data: {str(e)}")

#     def update_connection_data(self, breakout_wire_name: str, connection_name: str, connection_data: dict):
#         """Update connection data"""
#         print(f"EPD Presenter: Updating connection data for {breakout_wire_name}.{connection_name}")

#         try:
#             self.model.update_connection_data(breakout_wire_name, connection_name, connection_data)
#             self.complete_operation(f"update_connection_data_{breakout_wire_name}_{connection_name}")
#         except Exception as e:
#             self.handle_error(f"Failed to update connection data: {str(e)}")

#     def get_breakout_wire_list(self):
#         """Get list of all breakout wires"""
#         return self.model.get_breakout_wire_list()

#     def get_current_selection(self):
#         """Get current breakout wire and connection selection"""
#         return {
#             'breakout_wire': self.context.get_state('current_breakout_wire'),
#             'connection': self.context.get_state('current_connection')
#         }

#     def _on_model_data_updated(self, data):
#         """Handle model data updates"""
#         print(f"EPD Presenter: Model data updated - {list(data.keys())}")
#         self.data_changed.emit(data)

#     def _on_model_data_loaded(self, data):
#         """Handle model data loaded"""
#         print(f"EPD Presenter: Model data loaded - {len(data)} items")
#         self.data_changed.emit({'type': 'data_loaded', 'data': data})
