"""
Theme constants and stylesheet builders for start page

Provides centralized styling configuration including:
- Color constants
- Stylesheet generation functions
- Shadow effect creation
"""
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor


# ============================================================================
# COLOR CONSTANTS
# ============================================================================
BACKGROUND = "#1e1e1e"
TILE_BG = "#2a2a2a"
TILE_BG_HOVER = "#353535"
TILE_BORDER = "#3a3a3a"
TILE_BORDER_HOVER = "#4a4a4a"
ACCENT_BLUE = "#4fc3f7"
ACCENT_BLUE_LIGHT = "#90caf9"
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#b0b0b0"
TEXT_TERTIARY = "#c0c0c0"
TEXT_MUTED = "#909090"
BUTTON_BG = "rgba(100, 181, 246, 0.1)"
BUTTON_BG_HOVER = "rgba(100, 181, 246, 0.2)"
BUTTON_BORDER = "rgba(100, 181, 246, 0.2)"
BUTTON_BORDER_HOVER = "rgba(144, 202, 249, 0.3)"
BUTTON_COLOR = "#64b5f6"
BUTTON_COLOR_HOVER = "#90caf9"
BUTTON_DISABLED_BG = "rgba(80, 80, 80, 0.1)"
BUTTON_DISABLED_COLOR = "#505050"
BUTTON_DISABLED_BORDER = "rgba(80, 80, 80, 0.2)"

# ============================================================================
# SPACING CONSTANTS
# ============================================================================
TILE_PADDING = 18
TILE_SPACING = 10
GRID_SPACING = 12
TILE_MIN_HEIGHT = 176
TILE_MAX_HEIGHT = 208
BORDER_RADIUS = 16
BUTTON_BORDER_RADIUS = 6

# ============================================================================
# SHADOW PARAMETERS
# ============================================================================
SHADOW_BLUR_NORMAL = 25
SHADOW_BLUR_HOVER = 40
SHADOW_OFFSET_NORMAL = 6
SHADOW_OFFSET_HOVER = 10
SHADOW_OPACITY_NORMAL = 100
SHADOW_OPACITY_HOVER = 120


# ============================================================================
# STYLESHEET BUILDERS
# ============================================================================

def get_scrollbar_stylesheet():
    """Get stylesheet for modern scrollbar styling"""
    return f"""
        QScrollArea {{
            border: none;
            border-top: 1px solid #363535;
            background-color: transparent;
        }}
        QScrollBar:vertical {{
            border: none;
            background: {BACKGROUND};
            width: 10px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {TILE_BORDER};
            min-height: 20px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {TILE_BORDER_HOVER};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}
    """


def get_tile_stylesheet(hover=False):
    """Get stylesheet for tile styling
    
    Args:
        hover: Whether this is hover state
        
    Returns:
        QSS stylesheet string
    """
    bg_color = TILE_BG_HOVER if hover else TILE_BG
    border_color = TILE_BORDER_HOVER if hover else TILE_BORDER
    
    return f"""
        background-color: {bg_color};
        border: 1px solid {border_color};
        border-radius: {BORDER_RADIUS}px;
    """


def get_button_stylesheet(enabled=True):
    """Get stylesheet for button styling
    
    Args:
        enabled: Whether button is enabled
        
    Returns:
        QSS stylesheet string
    """
    if enabled:
        return f"""
            QPushButton {{
                background-color: {BUTTON_BG};
                color: {BUTTON_COLOR};
                border: 1px solid {BUTTON_BORDER};
                border-radius: {BUTTON_BORDER_RADIUS}px;
                text-align: center;
                padding: 6px 12px;
                font-size: 9pt;
            }}
            QPushButton:hover:enabled {{
                background-color: {BUTTON_BG_HOVER};
                color: {BUTTON_COLOR_HOVER};
                border-color: {BUTTON_BORDER_HOVER};
            }}
            QPushButton:disabled {{
                background-color: {BUTTON_DISABLED_BG};
                color: {BUTTON_DISABLED_COLOR};
                border-color: {BUTTON_DISABLED_BORDER};
            }}
        """
    else:
        return f"""
            QPushButton {{
                background-color: {BUTTON_BG};
                color: {BUTTON_COLOR};
                border: 1px solid {BUTTON_BORDER};
                border-radius: {BUTTON_BORDER_RADIUS}px;
                text-align: center;
                padding: 6px 12px;
                font-size: 9pt;
            }}
            QPushButton:hover {{
                background-color: {BUTTON_BG_HOVER};
                color: {BUTTON_COLOR_HOVER};
                border-color: {BUTTON_BORDER_HOVER};
            }}
        """


# ============================================================================
# SHADOW EFFECTS
# ============================================================================

def create_shadow(hover=False):
    """Create a subtle shadow effect for tiles
    
    Args:
        hover: Whether this is hover state (stronger shadow)
        
    Returns:
        QGraphicsDropShadowEffect instance
    """
    shadow = QGraphicsDropShadowEffect()
    if hover:
        shadow.setBlurRadius(SHADOW_BLUR_HOVER)
        shadow.setXOffset(0)
        shadow.setYOffset(SHADOW_OFFSET_HOVER)
        shadow.setColor(QColor(0, 0, 0, SHADOW_OPACITY_HOVER))
    else:
        shadow.setBlurRadius(SHADOW_BLUR_NORMAL)
        shadow.setXOffset(0)
        shadow.setYOffset(SHADOW_OFFSET_NORMAL)
        shadow.setColor(QColor(0, 0, 0, SHADOW_OPACITY_NORMAL))
    return shadow
