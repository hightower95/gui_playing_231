"""
EPD Module Configuration - Shared styling and settings for all EPD views
"""
from productivity_core.core.config import UI_COLORS


# Default columns to display in EPD results tables
# Columns not in this list will be hidden by default
# Order in this list determines display order (left to right)
DEFAULT_VISIBLE_COLUMNS = [
    "EPD",
    "Description",
    "Cable",
    "AWG",
    "Rating (A)",
    "Pins",
]


# EPD-specific table styling configuration
EPD_TABLE_STYLES = {
    'primary_color': UI_COLORS['section_highlight_primary'],
    'header_color': UI_COLORS['epd_header_color'],
    'header_gradient_stop1': UI_COLORS['section_highlight_primary'],
    'header_gradient_stop2': UI_COLORS['section_highlight_primary'],
    'header_hover_stop1': UI_COLORS['epd_header_hover_light'],
    'header_hover_stop2': UI_COLORS['epd_header_hover_dark'],
    'header_text_color': UI_COLORS['section_border'],
    'border_color': UI_COLORS['epd_border_light'],
    'border_bottom_color': UI_COLORS['epd_border_dark'],
    'gridline_color': UI_COLORS['epd_gridline'],
    'alternate_row_color': UI_COLORS['epd_alternate_row'],
}

# Common table style string template
EPD_TABLE_STYLESHEET = """
QTableView {{
    gridline-color: {gridline_color};
    alternate-background-color: {alternate_row_color};
    selection-background-color: {primary_color};
}}
QHeaderView::section {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {header_gradient_stop1}, stop:1 {header_gradient_stop2});
    color: {header_text_color};
    font-weight: bold;
    font-size: 11px;
    padding: 6px;
    border: 1px solid {border_color};
    border-bottom: 2px solid {border_bottom_color};
}}
QHeaderView::section:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {header_hover_stop1}, stop:1 {header_hover_stop2});
}}
"""


def apply_epd_table_styling(table_view):
    """
    Apply consistent EPD table styling to any QTableView

    Args:
        table_view: QTableView instance to style
    """
    from PySide6.QtWidgets import QSizePolicy

    # Apply stylesheet
    stylesheet = EPD_TABLE_STYLESHEET.format(**EPD_TABLE_STYLES)
    table_view.setStyleSheet(stylesheet)

    # Set common table properties
    table_view.setAlternatingRowColors(True)
    table_view.setShowGrid(True)
    table_view.horizontalHeader().setStretchLastSection(True)
    table_view.verticalHeader().setVisible(False)
    table_view.setSizePolicy(
        QSizePolicy.Policy.Expanding,
        QSizePolicy.Policy.Expanding
    )


# EPD-specific filter widget styles
EPD_FILTER_STYLES = {
    'filter_background': UI_COLORS['epd_header_hover_dark'],
    'filter_border': UI_COLORS['filter_pill_background'],
    'filter_text_color': UI_COLORS['section_border'],
    'remove_button_color': UI_COLORS['remove_button'],
    'remove_button_hover': UI_COLORS['remove_button_hover'],
}

EPD_FILTER_WIDGET_STYLESHEET = """
QLabel {{
    background-color: {filter_background};
    border: 1px solid {filter_border};
    border-radius: 12px;
    padding: 4px 8px;
    color: {filter_text_color};
    font-size: 11px;
}}
"""

EPD_REMOVE_BUTTON_STYLESHEET = """
QPushButton {{
    background-color: {remove_button_color};
    border: none;
    border-radius: 10px;
    color: white;
    font-weight: bold;
    font-size: 12px;
}}
QPushButton:hover {{
    background-color: {remove_button_hover};
}}
"""


def get_filter_label_style():
    """Get consistent filter label styling"""
    return EPD_FILTER_WIDGET_STYLESHEET.format(**EPD_FILTER_STYLES)


def get_filter_remove_button_style():
    """Get consistent filter remove button styling"""
    return EPD_REMOVE_BUTTON_STYLESHEET.format(**EPD_FILTER_STYLES)
