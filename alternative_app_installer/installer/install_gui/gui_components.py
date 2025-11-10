"""
GUI Components and Constants - Centralized styling and component definitions

This module provides:
- Color constants for consistent theming
- Status type mappings 
- Reusable styling functions
- Standard GUI component configurations
"""

# Status Color Constants


class StatusColors:
    """Color constants for different status types"""
    SUCCESS = "#22c55e"     # Bright green
    ERROR = "#ef4444"       # Red
    WARNING = "#f59e0b"     # Amber/Orange
    INFO = "#6b7280"        # Grey
    NEUTRAL = "#6b7280"     # Grey (same as info)


# Status Type Mappings
class StatusTypes:
    """Standard status type identifiers"""
    GREEN = "green"
    RED = "red"
    GREY = "grey"
    DEFAULT = "default"

    # Semantic aliases
    SUCCESS = GREEN
    ERROR = RED
    WARNING = "warning"
    INFO = GREY
    NEUTRAL = GREY


# Default Messages
class StatusMessages:
    """Default status messages for common scenarios"""
    PATH_ACCEPTED = "Path accepted"
    PATH_REJECTED = "Path rejected"
    NO_ACTION_REQUIRED = "No action required"
    DEFAULT_LOADED = "Default path loaded"
    PATH_VALID = "Installation path is valid"
    PATH_INVALID = "Path is invalid"


def get_status_color(status_type: str) -> str:
    """Get color code for a given status type

    Args:
        status_type: Status type identifier (green, red, grey, etc.)

    Returns:
        Hex color code string
    """
    color_map = {
        StatusTypes.GREEN: StatusColors.SUCCESS,
        StatusTypes.RED: StatusColors.ERROR,
        StatusTypes.GREY: StatusColors.INFO,
        StatusTypes.DEFAULT: StatusColors.NEUTRAL,
        StatusTypes.WARNING: StatusColors.WARNING,
        # Semantic aliases
        StatusTypes.SUCCESS: StatusColors.SUCCESS,
        StatusTypes.ERROR: StatusColors.ERROR,
        StatusTypes.INFO: StatusColors.INFO,
        StatusTypes.NEUTRAL: StatusColors.NEUTRAL,
    }

    return color_map.get(status_type, StatusColors.NEUTRAL)


def get_status_message(status_type: str, custom_message: str = "") -> str:
    """Get default message for a status type if no custom message provided

    Args:
        status_type: Status type identifier
        custom_message: Custom message to use instead of default

    Returns:
        Message string to display
    """
    if custom_message:
        return custom_message

    default_messages = {
        StatusTypes.GREEN: StatusMessages.PATH_ACCEPTED,
        StatusTypes.RED: StatusMessages.PATH_REJECTED,
        StatusTypes.GREY: StatusMessages.NO_ACTION_REQUIRED,
        StatusTypes.DEFAULT: StatusMessages.DEFAULT_LOADED,
        # Semantic aliases
        StatusTypes.SUCCESS: StatusMessages.PATH_ACCEPTED,
        StatusTypes.ERROR: StatusMessages.PATH_REJECTED,
        StatusTypes.INFO: StatusMessages.NO_ACTION_REQUIRED,
        StatusTypes.NEUTRAL: StatusMessages.NO_ACTION_REQUIRED,
    }

    return default_messages.get(status_type, StatusMessages.NO_ACTION_REQUIRED)


def apply_status_styling(widget, status_type: str, message: str = "", additional_styles: str = "") -> None:
    """Apply status-based styling to a QLabel or similar widget

    Args:
        widget: Qt widget to apply styling to
        status_type: Status type identifier  
        message: Message to set on widget (optional)
        additional_styles: Additional CSS styles to apply
    """
    color = get_status_color(status_type)
    display_message = get_status_message(status_type, message)

    # Set the message if provided
    if hasattr(widget, 'setText'):
        widget.setText(display_message)

    # Build stylesheet
    base_styles = f"color: {color}; font-weight: bold;"
    full_styles = f"{base_styles} {additional_styles}".strip()

    # Apply styling
    if hasattr(widget, 'setStyleSheet'):
        widget.setStyleSheet(full_styles)


# GUI Layout Constants
class LayoutConstants:
    """Standard spacing and sizing constants"""
    BUTTON_MIN_WIDTH = 80
    BUTTON_MIN_HEIGHT = 35
    STANDARD_SPACING = 8
    LARGE_SPACING = 15
    SMALL_SPACING = 5

    STANDARD_MARGINS = (15, 15, 15, 15)
    REDUCED_MARGINS = (10, 10, 10, 10)
    MINIMAL_MARGINS = (5, 5, 5, 5)


# Common Button Labels
class ButtonLabels:
    """Standard button text labels"""
    BROWSE = "Browse..."
    COMPLETE_STEP = "Complete Step"
    CANCEL_INSTALLATION = "Cancel Installation"
    FINISH = "Finish"
    NEXT = "Next"
    BACK = "Back"
    OK = "OK"
    CANCEL = "Cancel"


# Common Dialog Titles
class DialogTitles:
    """Standard dialog title text"""
    SELECT_FOLDER = "Select Installation Folder"
    INVALID_PATH = "Invalid Path"
    PERMISSION_DENIED = "Permission Denied"
    CANNOT_CREATE_DIRECTORY = "Cannot Create Directory"
    DIRECTORY_NOT_EMPTY = "Directory Not Empty"
    NO_PATH_SELECTED = "No Path Selected"
    FOLDER_SELECTION_DISABLED = "Folder Selection Disabled"
