"""
Component Enums

Enumerations for component configuration variants.
"""
from enum import Enum


class ButtonRole(Enum):
    """Button roles that determine color scheme

    Available roles:
    - PRIMARY: Main action (blue #0078d4)
    - SECONDARY: Secondary action (gray #6c757d)
    - SUCCESS: Positive action (green #28a745)
    - DANGER: Destructive action (red #dc3545)
    - WARNING: Warning action (orange #ffc107)
    - INFO: Informational (light blue #17a2b8)
    """
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"


class ButtonSize(Enum):
    """Button size variants

    Available sizes:
    - FULL: Full width/height (auto x 36px)
    - HALF_WIDTH: 50% width (150px x 36px)
    - HALF_HEIGHT: 50% height (auto x 24px)
    - COMPACT: Both half (100px x 24px)
    """
    FULL = "full"
    HALF_WIDTH = "half_width"
    HALF_HEIGHT = "half_height"
    COMPACT = "compact"


class ComboSize(Enum):
    """ComboBox size variants

    Available sizes:
    - SINGLE: Standard width (~200px)
    - DOUBLE: Double width (~400px)
    - FULL: Full available width
    """
    SINGLE = "single"
    DOUBLE = "double"
    FULL = "full"


class TextStyle(Enum):
    """Text label style variants

    Available styles:
    - TITLE: 14pt bold - Main titles
    - SECTION: 12pt bold - Section headers
    - SUBSECTION: 11pt bold - Subsection headers
    - LABEL: 10pt normal - Standard labels
    - NOTES: 9pt italic gray - Helper text
    - STATUS: 10pt normal - Status messages
    """
    TITLE = "title"
    SECTION = "section"
    SUBSECTION = "subsection"
    LABEL = "label"
    NOTES = "notes"
    STATUS = "status"


class DialogResult(Enum):
    """Dialog result values for StandardWarningDialog

    Available results:
    - OK: OK button clicked
    - YES: Yes button clicked
    - NO: No button clicked
    - CANCEL: Cancel button clicked or dialog closed
    """
    OK = "ok"
    YES = "yes"
    NO = "no"
    CANCEL = "cancel"


class SelectionMode(Enum):
    """Selection mode for list-based components

    Available modes:
    - NONE: No selection allowed
    - SINGLE: Single item selection
    - MULTI: Multiple item selection
    """
    NONE = "none"
    SINGLE = "single"
    MULTI = "multi"
