# main.py
from app.views.main_window import MainWindow
from app.core.app_context import AppContext
from PySide6.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    context = AppContext()
    window = MainWindow(context)
    window.show()
    sys.exit(app.exec())
