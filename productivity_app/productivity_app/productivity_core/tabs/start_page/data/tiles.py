"""
Tile data definitions for the start page

Dynamically loads tile configurations from TAB_CONFIG, reading each module's
TILE_CONFIG to display on the start page.

Tiles can be:
- Module tiles: Pulled from presenter/view classes with TILE_CONFIG
- Special tiles: Hardcoded (User Guide, Feedback, etc.)
"""
from typing import List, Tuple, Optional


def get_tile_data() -> List[Tuple[str, str, List[str], str, bool, Optional[str], bool]]:
    """Get tile data for all tabs by reading from TAB_CONFIG

    Returns:
        List of tuples: (title, subtitle, bullets_list, tab_id, is_visible, user_guide_url, enable_navigation)
    """
    from ...tab_config import TAB_CONFIG

    tiles = []

    # Load tiles from TAB_CONFIG
    for tab_config in TAB_CONFIG:
        # Check if this tab has tile configuration
        if 'tile' not in tab_config:
            continue

        tile_config = tab_config['tile']

        # Skip if module doesn't want to show in start page
        if not tile_config.get('show_in_start_page', True):
            continue

        tab_id = tab_config['id']
        is_visible = tab_config.get('visible', True)
        user_guide_url = tile_config.get('user_guide_url', None)
        enable_navigation = tile_config.get('enable_navigation', True)

        tiles.append((
            tile_config['title'],
            tile_config['subtitle'],
            tile_config['bullets'],
            tab_id,
            is_visible,
            user_guide_url,
            enable_navigation
        ))

    # Add special tiles (non-module tiles)
    tiles.extend(_get_special_tiles())

    return tiles


def _get_special_tiles() -> List[Tuple[str, str, List[str], str, bool, Optional[str], bool]]:
    """Get special tiles that don't correspond to modules

    Returns:
        List of special tile tuples: (title, subtitle, bullets, tab_id, is_visible, user_guide_url, enable_navigation)
    """
    return [
        ("📚 User Manual", "Learn how to use the toolkit",
         ["Getting started guide", "Feature documentation", "Best practices and tips"],
         "user_manual", False, "https://example.com/manual", False),

        ("💬 Feedback", "Help us improve",
         ["Report bugs and issues", "Request new features", "Share your suggestions"],
         "feedback", False, "https://example.com/feedback", False),
    ]
