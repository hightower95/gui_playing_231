"""
Swiss Army Tool - Main Application Entry Point
"""
import io
import socket
from .productivity_core.tabs.main_window import MainWindow
from .productivity_core.core.config import APP_SETTINGS, set_app_name
from .productivity_core.core.theme_manager import ThemeManager
from .productivity_core.core.config_manager import ConfigManager
from .productivity_core.core.app_context import AppContext
from PySide6.QtWidgets import QApplication
import sys
import os
from pathlib import Path

# Setup module path for productivity_core


def setup_module_path():
    """Add the directory containing productivity_core to Python path"""
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))


setup_module_path()


# UTF-8 Console Support for Windows
# This fixes encoding issues when running from command prompt


def setup_utf8_console():
    """Setup UTF-8 console output safely"""
    try:
        # Only on Windows and only if we have encoding issues
        if (sys.platform == 'win32'
            and hasattr(sys.stdout, 'buffer')
            and hasattr(sys.stdout, 'encoding')
            and sys.stdout.encoding.lower() not in ('utf-8', 'utf8')
                and not sys.stdout.closed):

            # Create new wrapper but keep reference to original
            original_stdout = sys.stdout
            try:
                sys.stdout = io.TextIOWrapper(
                    sys.stdout.buffer,
                    encoding='utf-8',
                    errors='replace',
                    line_buffering=True
                )
                # Test the new stdout works
                sys.stdout.write("")
                sys.stdout.flush()
            except (AttributeError, ValueError, OSError, UnicodeError):
                # Restore original if wrapping fails
                sys.stdout = original_stdout

    except Exception:
        # Silently ignore any setup errors
        pass


# Setup UTF-8 console (only if needed)
# setup_utf8_console()
# import os
# env = os.environ.copy()
# env['PYTHONUTF8'] = '1'

# result = subprocess.run(
#     [str(venv_python), "-c", runner_script],
#     cwd=str(app_dir),
#     capture_output=True,
#     text=True,
#     creationflags=creation_flags,
#     env=env  # Add this line
# )
# Option B:
# result = subprocess.run(
#     [str(venv_python), "-X", "utf8", "-c", runner_script],
#     # ... rest of the parameters
# # )
# -X utf8 specifically:
# The -X utf8 flag enables UTF-8 mode in Python, which:

# Forces UTF-8 encoding for all text I/O (stdin, stdout, stderr)
# Overrides system locale settings - ignores Windows' default CP1252/CP437 encodings
# Sets locale.getpreferredencoding() to return 'utf-8'
# Makes open() default to UTF-8 instead of system encoding
# Equivalent to setting PYTHONUTF8=1 environment variable

def send_message_to_splash(message):
    """Send a message to the splash screen."""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the splash screen server
        client.connect(("localhost", 65432))
        client.sendall(message.encode("utf-8"))
        client.close()
    except ConnectionRefusedError:
        print("Splash screen is not running.")
    except Exception as e:
        print(f"Error communicating with splash screen: {e}")


def main(*args, app_name=None, **kwargs):
    """Main application entry point

    Args:
        app_name: Optional application name for config directory (e.g., 'productivity_app_dev').
                 If provided, this will override the default and create a separate config directory.
    """
    # Set custom app_name if provided (must be before ConfigManager.initialize)
    if app_name:
        set_app_name(app_name)

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

    send_message_to_splash("close")

    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Application failed: {e}")
