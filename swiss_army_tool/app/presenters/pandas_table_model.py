from PySide6.QtCore import QAbstractTableModel, Qt


class PandasTableModel(QAbstractTableModel):
    """Adapter to show a Pandas DataFrame in a QTableView."""

    def __init__(self, df):
        super().__init__()
        self._data = df

    def update(self, df):
        self.beginResetModel()
        self._data = df
        self.endResetModel()

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
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

    def get_record(self, row):
        """Get a record as a dictionary for the given row"""
        if 0 <= row < len(self._data):
            return self._data.iloc[row].to_dict()
        return {}
