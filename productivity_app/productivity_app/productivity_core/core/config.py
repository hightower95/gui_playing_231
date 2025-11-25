"""
Configuration settings for the Swiss Army Tool application
"""
from pathlib import Path
import os
from enum import Enum


class FilterOperator(Enum):
    """Available filter operators for EPD field filtering"""
    CONTAINS = "contains"
    EQUALS = "equals"
    GREATER_THAN = "greater than"
    GREATER_THAN_OR_EQUAL = "greater than or equal"
    LESS_THAN = "less than"
    LESS_THAN_OR_EQUAL = "less than or equal"
    STARTS_WITH = "starts with"
    ENDS_WITH = "ends with"
    NOT_EQUALS = "not equals"
    NOT_CONTAINS = "not contains"


def get_all_operators():
    """Get all operator values as a list for UI dropdowns"""
    return [op.value for op in FilterOperator]


# UI Color Scheme
UI_COLORS = {
    # Section highlight colors
    "section_highlight_primary": "#4a90e2",      # Primary blue gradient start
    "section_highlight_secondary": "#357abd",    # Primary blue gradient end
    "section_border": "#2c5aa0",                 # Border color for sections

    # Alternative colors (if needed later)
    "section_green_primary": "#50c878",
    "section_green_secondary": "#3e9f5f",
    "section_green_border": "#2d7a47",

    # Text colors
    "highlight_text": "#e0e0e0",
    "section_text": "#6c757d",
    "section_text_shadow": "#000000",
    "muted_text": "#888888",                     # Muted/secondary text color

    # Background colors
    "window_background": "#f5f5f5",
    "panel_background": "#ffffff",
    "frame_border": "#d0d0d0",
    "section_background": "#444444",
    "section_label_background": "#121212",
    "light_background": "#fafafa",               # Light background for scroll areas

    # Filter pill colors
    "filter_pill_background": "#4a90e2",         # Primary blue
    "filter_pill_hover": "#5ba0f2",              # Lighter blue on hover
    "filter_pill_text": "#ffffff",               # White text

    # Button colors
    # Red for dangerous actions (hover)
    "danger_color": "#ff4444",
    "danger_pressed": "#cc0000",                 # Darker red for pressed state
    "remove_button": "#ff6b6b",                  # Remove/delete button color
    "remove_button_hover": "#ff5252",            # Remove/delete button hover

    # Border colors
    "dark_border": "#121212",                    # Dark border for separators

    # EPD table-specific colors
    "epd_header_color": "#111214",               # Dark EPD table header
    "epd_header_hover_light": "#f0f7ff",
    "epd_header_hover_dark": "#e8f1fa",
    "epd_border_light": "#c0d9f0",
    "epd_border_dark": "#a8cae8",
    "epd_gridline": "#ddd",
    "epd_alternate_row": "#2d2e35",
}

# UI Styling
UI_STYLES = {
    "section_banner": {
        "font_size": "11px",
        "font_weight": "bold",
        "padding": "4px",
        "border_radius": "3px",
        "height": 28
    }
}

# Application Settings
APP_SETTINGS = {
    "window_title": "Swiss Army Tool",
    "default_window_size": (1200, 800),
    "show_maximized": True,
    "theme_mode": "dark",  # Options: "light", "dark", "system"
}

# Configuration File Names
CONFIG_FILES = {
    "document_scanner": "document_scanner.json",
    "app_settings": "app_settings.json",
}

# Configuration Directory Path Configuration

# Configuration path variables - customize as needed
CONFIG_PATH_VARIABLES = {
    "APPDATA": Path(os.getenv("APPDATA", "~")),
    "LOCALAPPDATA": Path(os.getenv("LOCALAPPDATA", "~")),
    "USERPROFILE": Path(os.getenv("USERPROFILE", "~")),
    "HOME": Path.home(),
    "SYSTEM_NAME": "SwissArmyTool",  # Your system/organization name
    "APP_NAME": "productivity_app"   # Your application name
}

# Configuration directory template - customize this pattern
# Examples:
# - "{APPDATA}/{SYSTEM_NAME}/{APP_NAME}"  -> C:/Users/user/AppData/Roaming/SwissArmyTool/productivity_app
# - "{HOME}/.config/{APP_NAME}"           -> /home/user/.config/productivity_app
# - ".tool_config"                        -> ./tool_config (relative to app)
CONFIG_DIR_TEMPLATE = "{APPDATA}/{SYSTEM_NAME}/{APP_NAME}"


def resolve_config_dir() -> Path:
    """Resolve the configuration directory path from template and variables"""
    try:
        # Expand the template using the variables
        resolved_path = CONFIG_DIR_TEMPLATE.format(**CONFIG_PATH_VARIABLES)
        return Path(resolved_path).expanduser().resolve()
    except (KeyError, ValueError) as e:
        # Fallback to simple relative directory if template fails
        print(f"Warning: Config path template failed ({e}), using fallback")
        return Path(".tool_config")


# Resolved configuration directory
CONFIG_DIR = resolve_config_dir()


def get_app_name() -> str:
    """Get the current APP_NAME from configuration.

    Returns:
        The current APP_NAME value (e.g., 'productivity_app', 'productivity_app_dev')
    """
    return CONFIG_PATH_VARIABLES.get('APP_NAME', 'productivity_app')


def set_app_name(app_name: str) -> None:
    """Runtime modification of APP_NAME to support dev/live environments.

    This function must be called BEFORE ConfigManager.initialize().

    Args:
        app_name: The application name to use in the config directory path.
                 Example: 'productivity_app_dev' or 'productivity_app_live'

    Example:
        >>> from productivity_app.productivity_core.core.config import set_app_name
        >>> set_app_name('productivity_app_dev')  # Use before ConfigManager.initialize()
    """
    global CONFIG_PATH_VARIABLES, CONFIG_DIR

    # Update the APP_NAME in variables
    CONFIG_PATH_VARIABLES['APP_NAME'] = app_name

    # Recalculate CONFIG_DIR with the new APP_NAME
    CONFIG_DIR = resolve_config_dir()

    print(f"✓ Application data directory set to: {CONFIG_DIR}")
