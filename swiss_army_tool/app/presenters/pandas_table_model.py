from PySide6.QtCore import QAbstractTableModel, Qt
from PySide6.QtGui import QColor, QBrush


class PandasTableModel(QAbstractTableModel):
    """Adapter to show a Pandas DataFrame in a QTableView."""

    def __init__(self, df, input_column_prefix="Input: "):
        super().__init__()
        self._data = df
        self.input_column_prefix = input_column_prefix

    def update(self, df):
        self.beginResetModel()
        self._data = df
        self.endResetModel()

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._data.columns)

    def data(self, index, role):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            return str(self._data.iat[index.row(), index.column()])

        # Color cells in input columns slightly differently
        if role == Qt.BackgroundRole:
            column_name = self._data.columns[index.column()]
            if column_name.startswith(self.input_column_prefix):
                # Light blue tint for input columns
                return QBrush(QColor(230, 240, 255))  # Lighter blue

        # Ensure text is visible in input columns
        if role == Qt.ForegroundRole:
            column_name = self._data.columns[index.column()]
            if column_name.startswith(self.input_column_prefix):
                # Dark text for input columns
                return QBrush(QColor(0, 0, 0))  # Black text

        return None

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return str(self._data.columns[section])

            # Color input column headers differently
            if role == Qt.BackgroundRole:
                column_name = self._data.columns[section]
                if column_name.startswith(self.input_column_prefix):
                    # Blue background for input column headers
                    return QBrush(QColor(100, 149, 237))  # Cornflower blue

            # White text for input column headers
            if role == Qt.ForegroundRole:
                column_name = self._data.columns[section]
                if column_name.startswith(self.input_column_prefix):
                    return QBrush(QColor(255, 255, 255))  # White text

        if role == Qt.DisplayRole and orientation == Qt.Vertical:
            return str(section + 1)

        return None

    def get_record(self, row):
        """Get a record as a dictionary for the given row"""
        if 0 <= row < len(self._data):
            return self._data.iloc[row].to_dict()
        return {}
