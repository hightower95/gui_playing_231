"""
Theme Test Script - Test different themes for the productivity app
"""
from app.ui.components import StandardButton, ButtonRole, StandardLabel, TextStyle
from app.core.theme_manager import ThemeManager
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
import sys
from pathlib import Path

# Add the productivity_app to the Python path
app_path = Path(__file__).parent / "productivity_app"
sys.path.insert(0, str(app_path))


class ThemeTestWindow(QMainWindow):
    """Test window to compare themes"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Theme Test - Productivity App")
        self.setGeometry(100, 100, 600, 400)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title
        title = StandardLabel("Theme Comparison Test", style=TextStyle.TITLE)
        layout.addWidget(title)

        # Description
        desc = StandardLabel(
            "Use the buttons below to test different themes", style=TextStyle.NOTES)
        layout.addWidget(desc)

        # Theme buttons
        light_btn = StandardButton(
            "Apply Light Theme", role=ButtonRole.PRIMARY)
        light_btn.clicked.connect(self.apply_light_theme)
        layout.addWidget(light_btn)

        dark_btn = StandardButton(
            "Apply Dark Theme", role=ButtonRole.SECONDARY)
        dark_btn.clicked.connect(self.apply_dark_theme)
        layout.addWidget(dark_btn)

        system_btn = StandardButton("Apply System Theme", role=ButtonRole.INFO)
        system_btn.clicked.connect(self.apply_system_theme)
        layout.addWidget(system_btn)

        # Sample components
        layout.addWidget(StandardLabel(
            "Sample Components:", style=TextStyle.SECTION))

        sample_btn = StandardButton("Sample Button", role=ButtonRole.SUCCESS)
        layout.addWidget(sample_btn)

        status = StandardLabel(
            "Status: Theme testing active", style=TextStyle.STATUS)
        layout.addWidget(status)

        notes = StandardLabel(
            "This text should be consistent across themes", style=TextStyle.NOTES)
        layout.addWidget(notes)

    def apply_light_theme(self):
        ThemeManager.apply_light_theme(QApplication.instance())

    def apply_dark_theme(self):
        ThemeManager.apply_dark_theme(QApplication.instance())

    def apply_system_theme(self):
        ThemeManager.apply_system_theme(QApplication.instance())


def main():
    app = QApplication(sys.argv)

    # Start with dark theme (new default)
    ThemeManager.initialize_theme(app, theme_mode="dark")

    window = ThemeTestWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
