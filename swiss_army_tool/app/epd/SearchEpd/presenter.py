from PySide6.QtCore import QSortFilterProxyModel, Qt, Signal
from app.epd.SearchEpd.view import SearchEpdView
from app.presenters.pandas_table_model import PandasTableModel


class SearchEpdPresenter:
    """Presenter mediating between EpdModel and SearchEpdView."""
    # searchTextChanged = Signal(str)

    def __init__(self, context, epd_model):
        self.context = context
        self.model = epd_model
        self.view = SearchEpdView()

        # Setup table model
        self.df = self.model.get_all()
        self.table_model = PandasTableModel(self.df)
        self.proxy = QSortFilterProxyModel()
        self.proxy.setSourceModel(self.table_model)
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy.setFilterKeyColumn(-1)

        self.view.table.setModel(self.proxy)
        self.view.table.setSortingEnabled(True)
        self.view.table.setSelectionBehavior(
            self.view.table.SelectionBehavior.SelectRows)
        self.view.table.setSelectionMode(
            self.view.table.SelectionMode.SingleSelection)

        # --- Connect signals ---
        # self.view.search_button.clicked.connect(self.on_search)
        # self.view.search_input.returnPressed.connect(self.on_search)
        self.view.table.selectionModel().selectionChanged.connect(self.on_row_selected)
        self.view.searchEPDTriggered.connect(self.on_search)
        # self.searchTextChanged.

    # --- Handle user search ---
    def on_search(self, text: str):
        filtered = self.model.filter(text)
        self.table_model.update(filtered)
        self.df = filtered

    # --- Handle row selection ---
    def on_row_selected(self, selected, _):
        indexes = self.view.table.selectionModel().selectedRows()
        if not indexes:
            return
        row = indexes[0].row()
        record = self.df.iloc[row].to_dict()

        # Display in context and footer areas
        context_text = (
            f"EPD: {record['EPD']}\n"
            f"Description: {record['Description']}\n"
            f"Cable: {record['Cable']}\n"
            f"AWG: {record['AWG']}"
        )
        footer_text = f"This EPD uses cable type: {record['Cable']} (AWG {record['AWG']})"
        self.view.display_context(context_text)
        self.view.display_footer(footer_text)
