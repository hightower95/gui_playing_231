"""
Theme Manager - Consistent theming across the application
"""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor


class ThemeManager:
    """Manages application theming and ensures consistent appearance"""

    @staticmethod
    def apply_light_theme(app: QApplication):
        """Apply a consistent light theme to the application"""
        # Force light theme
        app.setStyle("Fusion")  # Use Fusion style for consistency

        # Create light palette
        palette = QPalette()

        # Window colors
        palette.setColor(QPalette.Window, QColor(245, 245, 245)
                         )          # Light gray background
        palette.setColor(QPalette.WindowText, QColor(
            0, 0, 0))            # Black text

        # Base colors (input fields)
        palette.setColor(QPalette.Base, QColor(255, 255, 255)
                         )            # White input background
        palette.setColor(QPalette.AlternateBase, QColor(
            240, 240, 240))   # Alternate row color

        # Text colors
        palette.setColor(QPalette.Text, QColor(0, 0, 0)
                         )                  # Black text
        palette.setColor(QPalette.BrightText, QColor(
            255, 0, 0))          # Red bright text

        # Button colors
        palette.setColor(QPalette.Button, QColor(240, 240, 240)
                         )          # Light button background
        palette.setColor(QPalette.ButtonText, QColor(
            0, 0, 0))            # Black button text

        # Highlight colors
        palette.setColor(QPalette.Highlight, QColor(
            0, 120, 212))         # Blue highlight
        palette.setColor(QPalette.HighlightedText, QColor(
            255, 255, 255))  # White highlighted text

        # Tool tip colors
        palette.setColor(QPalette.ToolTipBase, QColor(
            255, 255, 220))     # Light yellow tooltip
        palette.setColor(QPalette.ToolTipText, QColor(
            0, 0, 0))           # Black tooltip text

        # Apply the palette
        app.setPalette(palette)

    @staticmethod
    def apply_dark_theme(app: QApplication):
        """Apply a consistent dark theme to the application"""
        # Force dark theme
        app.setStyle("Fusion")  # Use Fusion style for consistency

        # Create dark palette
        palette = QPalette()

        # Window colors
        palette.setColor(QPalette.Window, QColor(53, 53, 53)
                         )             # Dark gray background
        palette.setColor(QPalette.WindowText, QColor(
            255, 255, 255))      # White text

        # Base colors (input fields)
        palette.setColor(QPalette.Base, QColor(25, 25, 25)
                         )               # Dark input background
        palette.setColor(QPalette.AlternateBase, QColor(
            66, 66, 66))      # Alternate row color

        # Text colors
        palette.setColor(QPalette.Text, QColor(
            255, 255, 255))            # White text
        palette.setColor(QPalette.BrightText, QColor(
            255, 0, 0))          # Red bright text

        # Button colors
        palette.setColor(QPalette.Button, QColor(53, 53, 53)
                         )             # Dark button background
        palette.setColor(QPalette.ButtonText, QColor(
            255, 255, 255))      # White button text

        # Highlight colors
        palette.setColor(QPalette.Highlight, QColor(
            42, 130, 218))        # Blue highlight
        palette.setColor(QPalette.HighlightedText, QColor(
            0, 0, 0))       # Black highlighted text

        # Tool tip colors
        palette.setColor(QPalette.ToolTipBase, QColor(
            255, 255, 220))     # Light yellow tooltip
        palette.setColor(QPalette.ToolTipText, QColor(
            0, 0, 0))           # Black tooltip text

        # Apply the palette
        app.setPalette(palette)

    @staticmethod
    def apply_system_theme(app: QApplication):
        """Apply theme based on system settings"""
        # Check if system supports dark mode detection
        if hasattr(app, 'styleHints'):
            style_hints = app.styleHints()
            if hasattr(style_hints, 'colorScheme'):
                # Qt 6.5+ has native dark mode detection
                color_scheme = style_hints.colorScheme()
                if color_scheme == Qt.ColorScheme.Dark:
                    ThemeManager.apply_dark_theme(app)
                else:
                    ThemeManager.apply_light_theme(app)
                return

        # Fallback: Force dark theme for consistency
        ThemeManager.apply_dark_theme(app)

    @staticmethod
    def initialize_theme(app: QApplication, theme_mode: str = "dark"):
        """Initialize application theme

        Args:
            app: QApplication instance
            theme_mode: "light", "dark", or "system"
        """
        if theme_mode == "light":
            ThemeManager.apply_light_theme(app)
        elif theme_mode == "system":
            ThemeManager.apply_system_theme(app)
        else:
            # Default to dark theme for consistency
            ThemeManager.apply_dark_theme(app)
