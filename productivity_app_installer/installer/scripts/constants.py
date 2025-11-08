"""
Bootstrap Application Constants
Centralized location for all magic strings, UI settings, and configuration
"""

# UI Constants
WINDOW_SIZE = "800x1000"
PROGRESS_BAR_LENGTH = 200
DEFAULT_PADDING = 20
SECTION_PADDING = 10
ENTRY_WIDTH = 70

# Window Settings
WINDOW_RESIZABLE = False
WINDOW_TITLE_TEMPLATE = "{app_name} - Setup Wizard"

# Status Messages
STATUS_NOT_RUN = "⏸ Not run yet"
STATUS_VALIDATING = "⏳ Validating..."
STATUS_RUNNING = "⏳ Running..."
STATUS_COMPLETE = "✅ Complete"
STATUS_OK = "✅ OK"
STATUS_ERROR = "❌ Error"
STATUS_WARNING = "⚠️ Warning"
STATUS_NOT_VALIDATED = "⏸ Not validated"
STATUS_FOLDER_OK = "✅ Folder OK"
STATUS_VENV_CREATED = "✅ Virtual environment created"
STATUS_PYIRC_CONFIGURED = "✅ PyIRC configured"
STATUS_LIBRARY_INSTALLED = "✅ Library installed successfully"
STATUS_FILES_VERIFIED = "✅ All files verified"

# Progress Messages
PROGRESS_TEMPLATE = "Progress: {completed}/{total} steps completed"
ALL_STEPS_COMPLETE = "All steps completed!"

# Section Titles (without emojis for easy formatting)
SECTION_FOLDER = "Select Installation Folder"
SECTION_VENV = "Create Virtual Environment"
SECTION_PYIRC = "Configure PyIRC"
SECTION_LIBRARY = "Install Library"
SECTION_FILES = "Verify Required Files"

# Section Titles with Numbers and Emojis
SECTION_1_FOLDER = "1️⃣ Select Installation Folder"
SECTION_2_VENV = "2️⃣ Create Virtual Environment"
SECTION_3_PYIRC = "3️⃣ Configure PyIRC"
SECTION_4_LIBRARY = "4️⃣ Install Library"
SECTION_5_FILES = "5️⃣ Verify Required Files"

# Button Labels
BTN_BROWSE = "Browse..."
BTN_CREATE_VENV = "Create Virtual Environment"
BTN_SAVE_CONFIG = "Save Configuration"
BTN_INSTALL_LIBRARY = "Install Library"
BTN_CREATE_FILES = "Create Files Manually"
BTN_EXIT = "Exit"
BTN_SHOW_ME = "Show Me 📂"
BTN_HELP = "Help"
BTN_VALIDATE = "Validate"

# Required Files
REQUIRED_FILES = [
    "run_app.pyw",
    "launch_config.ini",
    "update.pyw",
    "about.pyw"
]

# File Extensions
PYTHON_EXTENSION = ".py"
PYTHON_WINDOWS_EXTENSION = ".pyw"
CONFIG_EXTENSION = ".ini"
LOG_EXTENSION = ".log"

# Directory Names
BOOTSTRAPPER_DIR = "bootstrapper"
LOGS_DIR = "logs"
TEMPLATES_DIR = "templates"
SCRIPTS_DIR = "Scripts"

# Config File Names
BOOTSTRAP_CONFIG_FILE = "installation_settings.ini"
LAUNCH_CONFIG_FILE = "launch_config.ini"
PIP_CONFIG_FILE = "pip.conf"

# Log File Names
SETUP_WIZARD_LOG = "setup_wizard.log"

# Step Keys
STEP_FOLDER = "folder"
STEP_VENV = "venv"
STEP_PYIRC = "pyirc"
STEP_LIBRARY = "library"
STEP_FILES = "files"

# All step keys in order
ALL_STEPS = [STEP_FOLDER, STEP_VENV, STEP_PYIRC, STEP_LIBRARY, STEP_FILES]

# Colors
COLOR_GRAY = "gray"
COLOR_GREEN = "green"
COLOR_RED = "red"
COLOR_ORANGE = "orange"
COLOR_BLUE = "blue"

# Default Values
DEFAULT_APP_NAME = "My Application"
DEFAULT_VERSION = "1.0.0"
DEFAULT_VENV_DIR = ".venv"
DEFAULT_TOKEN_URL = "https://example.com/get-token"
DEFAULT_HELP_URL = "https://example.com/help"

# DEV Mode Constants
DEV_SKIP_LOCAL_INDEX_LABEL = "[Local index disabled]"
DEV_SIMULATION_LABEL = "[SIMULATED]"
DEV_AUTO_GEN_LABEL = "[AUTO]"

# Threading Constants
THREAD_CHECK_INTERVAL_MS = 100

# Process Constants
if __name__ != "__main__":
    import sys
    if sys.platform == "win32":
        CREATE_NO_WINDOW = 0x08000000
    else:
        CREATE_NO_WINDOW = 0

# Message Dialog Constants
DIALOG_BUSY_TITLE = "Busy"
DIALOG_BUSY_MESSAGE = "Another step is running. Please wait."
DIALOG_ERROR_TITLE = "Error"
DIALOG_WARNING_TITLE = "Warning"
DIALOG_INFO_TITLE = "Information"
DIALOG_SUCCESS_TITLE = "Success"

# Validation Messages
MSG_FOLDER_INVALID = "Please select a valid installation folder"
MSG_VENV_MISSING = "Virtual environment not found or invalid"
MSG_PYIRC_MISSING = "PyIRC configuration not found"
MSG_LIBRARY_MISSING = "Required library not installed"
MSG_FILES_MISSING = "Required files are missing"

# Success Messages
MSG_SETUP_COMPLETE = "Setup completed successfully!"
MSG_FILES_CREATED = "All required files have been created"
MSG_VENV_CREATED = "Virtual environment created successfully"
MSG_LIBRARY_INSTALLED = "Library installed successfully"

# Ghost Text / Placeholder Text
PLACEHOLDER_TOKEN = "Enter your PyIRC token here..."
PLACEHOLDER_INDEX_URL = "https://your-index-url.com/simple/"

# Font Settings
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_HEADING = ("Segoe UI", 12, "bold")
FONT_NORMAL = ("Segoe UI", 9)

# Padding and Spacing
PADDING_LARGE = (0, 20)
PADDING_MEDIUM = (0, 10)
PADDING_SMALL = (0, 5)
PADDING_NONE = (0, 0)
