"""
Tile data definitions for the start page

Dynamically loads tile configurations from TAB_CONFIG, reading each module's
TILE_CONFIG to display on the start page.

Tiles can be:
- Module tiles: Pulled from presenter/view classes with TILE_CONFIG
- Special tiles: Hardcoded (User Guide, Feedback, etc.)
"""
from typing import List, Tuple, Optional


def get_tile_data() -> List[Tuple[str, str, List[str], str, bool, Optional[str]]]:
    """Get tile data for all tabs by reading from TAB_CONFIG

    Returns:
        List of tuples: (title, subtitle, bullets_list, tab_id, is_visible, user_guide_url)
    """
    from ...tab_config import TAB_CONFIG

    tiles = []

    # Load tiles from TAB_CONFIG
    for tab_config in TAB_CONFIG:
        presenter_class = tab_config['presenter_class']

        # Check if this module has TILE_CONFIG
        if not hasattr(presenter_class, 'TILE_CONFIG'):
            continue

        tile_config = presenter_class.TILE_CONFIG

        # Skip if module doesn't want to show in start page
        if not tile_config.get('show_in_start_page', True):
            continue

        tab_id = tab_config['id']
        is_visible = tab_config.get('visible', True)
        user_guide_url = tile_config.get('user_guide_url', None)

        tiles.append((
            tile_config['title'],
            tile_config['subtitle'],
            tile_config['bullets'],
            tab_id,
            is_visible,
            user_guide_url
        ))

    # Add special tiles (non-module tiles)
    tiles.extend(_get_special_tiles())

    return tiles


def _get_special_tiles() -> List[Tuple[str, str, List[str], str, bool, Optional[str]]]:
    """Get special tiles that don't correspond to modules

    Returns:
        List of special tile tuples: (title, subtitle, bullets, tab_id, is_visible, user_guide_url)
    """
    return [
        # Example special tiles - uncomment and customize as needed
        # ("📚 User Guide", "Learn how to use the toolkit",
        #  ["Getting started tutorials", "Feature documentation", "Video guides"],
        #  "user_guide", True, "https://example.com/guide"),
        #
        # ("💬 Feedback", "Help us improve",
        #  ["Report bugs", "Request features", "Share suggestions"],
        #  "feedback", True, None),
    ]
