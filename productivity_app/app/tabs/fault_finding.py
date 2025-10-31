from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableView
from PySide6.QtCore import Signal
from PySide6.QtGui import QStandardItemModel, QStandardItem


class FaultFindingView(QWidget):
    searchRequested = Signal(str)

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        top = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_button = QPushButton("Search")
        top.addWidget(QLabel("Search Term:"))
        top.addWidget(self.search_box)
        top.addWidget(self.search_button)
        layout.addLayout(top)

        self.table = QTableView()
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.search_button.clicked.connect(
            lambda: self.searchRequested.emit(self.search_box.text()))

    def display_results(self, results):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Source", "Data", "Context"])
        for r in results:
            data_str = ", ".join(f"{k}: {v}" for k, v in r.data.items())
            ctx_str = ", ".join(f"{k}: {v}" for k,
                                v in (r.context or {}).items())
            model.appendRow([
                QStandardItem(r.source),
                QStandardItem(data_str),
                QStandardItem(ctx_str)
            ])
        self.table.setModel(model)
        self.table.resizeColumnsToContents()
