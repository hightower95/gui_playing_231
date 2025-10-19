"""
Component Constants

Size and color constants for UI components.
"""
from .enums import ButtonRole


# ============================================================================
# SIZE CONSTANTS
# ============================================================================

COMPONENT_SIZES = {
    # Button sizes
    "button_full_width": None,         # Use layout default
    "button_full_height": 36,
    "button_half_width": 150,
    "button_half_height": 24,
    "button_compact_width": 100,
    "button_compact_height": 24,

    # Input sizes
    "input_standard_height": 30,
    "input_standard_width": 200,

    # ComboBox sizes
    "combo_single_width": 200,
    "combo_double_width": 400,
    "combo_height": 30,

    # Drag-drop area
    "drop_area_min_height": 80,

    # SpinBox sizes
    "spinbox_standard_width": 100,
    "spinbox_height": 30,

    # TextArea sizes
    "textarea_min_height": 60,
    "textarea_standard_height": 120,

    # ProgressBar sizes
    "progressbar_height": 20,

    # Form layout
    "form_label_width": 120,
    "form_row_spacing": 8,
    "form_section_spacing": 16,
}


# ============================================================================
# COLOR SCHEMES BY ROLE
# ============================================================================

BUTTON_COLORS = {
    ButtonRole.PRIMARY: {
        "background": "#0078d4",
        "hover": "#106ebe",
        "pressed": "#005a9e",
        "disabled": "#cccccc",
        "text": "#ffffff",
        "text_disabled": "#666666",
    },
    ButtonRole.SECONDARY: {
        "background": "#6c757d",
        "hover": "#5a6268",
        "pressed": "#4e555b",
        "disabled": "#cccccc",
        "text": "#ffffff",
        "text_disabled": "#666666",
    },
    ButtonRole.SUCCESS: {
        "background": "#28a745",
        "hover": "#218838",
        "pressed": "#1e7e34",
        "disabled": "#cccccc",
        "text": "#ffffff",
        "text_disabled": "#666666",
    },
    ButtonRole.DANGER: {
        "background": "#dc3545",
        "hover": "#c82333",
        "pressed": "#bd2130",
        "disabled": "#cccccc",
        "text": "#ffffff",
        "text_disabled": "#666666",
    },
    ButtonRole.WARNING: {
        "background": "#ffc107",
        "hover": "#e0a800",
        "pressed": "#d39e00",
        "disabled": "#cccccc",
        "text": "#212529",
        "text_disabled": "#666666",
    },
    ButtonRole.INFO: {
        "background": "#17a2b8",
        "hover": "#138496",
        "pressed": "#117a8b",
        "disabled": "#cccccc",
        "text": "#ffffff",
        "text_disabled": "#666666",
    },
}
