"""
Swiss Army Tool - Main Application Entry Point
"""
import sys
from PySide6.QtWidgets import QApplication
from app.core.app_context import AppContext
from app.core.config_manager import ConfigManager
from app.tabs.main_window import MainWindow


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)

    # Initialize configuration manager (creates .tool_config directory)
    ConfigManager.initialize()

    # Initialize application context
    context = AppContext()

    # Create and show main window
    window = MainWindow(context)
    window.show()

    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
