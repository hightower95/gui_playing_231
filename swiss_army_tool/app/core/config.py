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
    "highlight_text": "#d3d3d3",
    "section_text": "#6c757d",
    "section_text_shadow": "#000000",

    # Background colors
    "window_background": "#f5f5f5",
    "panel_background": "#ffffff",
    "frame_border": "#d0d0d0",
    "section_background": "#444444",
    "section_label_background": "#121212",
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
