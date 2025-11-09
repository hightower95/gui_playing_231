"""
Swiss Army Tool - Main Application Entry Point
"""
import sys
from PySide6.QtWidgets import QApplication
from app.core.app_context import AppContext
from app.core.config_manager import ConfigManager
from app.core.theme_manager import ThemeManager
from app.core.config import APP_SETTINGS
from app.tabs.main_window import MainWindow


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)

    # Initialize configuration manager (creates .tool_config directory)
    ConfigManager.initialize()

    # Initialize consistent theming BEFORE any widgets are created
    theme_mode = APP_SETTINGS.get("theme_mode", "dark")
    ThemeManager.initialize_theme(app, theme_mode=theme_mode)

    # Initialize application context
    context = AppContext()

    # Create and show main window
    window = MainWindow(context)
    window.show()

    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
