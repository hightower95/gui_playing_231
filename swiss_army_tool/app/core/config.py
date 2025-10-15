"""
Configuration settings for the Swiss Army Tool application
"""

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
}
