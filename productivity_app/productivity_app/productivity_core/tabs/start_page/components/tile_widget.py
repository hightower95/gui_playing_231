"""
Tile widget component for start page

Provides:
- TileFrame: Custom QFrame with hover animations
- create_tile: Factory function to create a complete tile widget
"""
from typing import List, Callable
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton)
from PySide6.QtCore import Qt
from ..theme import (
    create_shadow,
    get_tile_stylesheet,
    get_button_stylesheet,
    TILE_MIN_HEIGHT,
    TILE_MAX_HEIGHT,
    TILE_PADDING,
    TILE_SPACING,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_TERTIARY
)


class TileFrame(QFrame):
    """Custom frame with hover animations for tile elevation effect"""

    def __init__(self, parent_window, parent=None):
        """Initialize tile frame

        Args:
            parent_window: Parent window that has create_shadow method
            parent: Qt parent widget
        """
        super().__init__(parent)
        self.parent_window = parent_window
        self._base_margins = None

    def enterEvent(self, event):
        """Handle mouse enter - elevate tile with hover styling"""
        self.setStyleSheet(get_tile_stylesheet(hover=True))
        self.setGraphicsEffect(create_shadow(hover=True))

        # Use negative top margin to create upward movement
        if self._base_margins is None:
            layout = self.layout()
            if layout:
                self._base_margins = layout.contentsMargins()
        if self._base_margins:
            self.layout().setContentsMargins(
                self._base_margins.left(),
                self._base_margins.top() - 4,
                self._base_margins.right(),
                self._base_margins.bottom() + 4
            )
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave - return tile to normal state"""
        self.setStyleSheet(get_tile_stylesheet(hover=False))
        self.setGraphicsEffect(create_shadow(hover=False))

        # Restore original margins
        if self._base_margins:
            self.layout().setContentsMargins(self._base_margins)
        super().leaveEvent(event)


def create_tile(parent_window, title: str, subtitle: str, bullets: List[str],
                tab_id: str, is_visible: bool,
                on_goto_clicked: Callable[[str], None],
                on_guide_clicked: Callable[[str], None],
                user_guide_url: str = None,
                enable_navigation: bool = True) -> QFrame:
    """Factory function to create a single tile widget

    Args:
        parent_window: Parent window for TileFrame
        title: Tile title (with emoji)
        subtitle: Brief description
        bullets: List of feature bullet points
        tab_id: Identifier for the tab
        is_visible: Whether the tab is currently visible
        on_goto_clicked: Callback when "Go To" button clicked, receives tab_id
        on_guide_clicked: Callback when "User Guide" button clicked, receives tab_id
        user_guide_url: Optional URL for user guide (enables guide button if provided)
        enable_navigation: Whether to show Go To button (default True)

    Returns:
        Configured TileFrame widget
    """
    from PySide6.QtWidgets import QSizePolicy

    tile = TileFrame(parent_window)
    tile.setStyleSheet(get_tile_stylesheet(hover=False))
    tile.setGraphicsEffect(create_shadow(hover=False))
    tile.setMinimumHeight(TILE_MIN_HEIGHT)
    tile.setMaximumHeight(TILE_MAX_HEIGHT)

    # Set size policy to prevent extra vertical spacing
    tile.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

    layout = QVBoxLayout(tile)
    layout.setSpacing(TILE_SPACING)
    layout.setContentsMargins(
        TILE_PADDING, TILE_PADDING, TILE_PADDING, TILE_PADDING)

    # Title
    title_label = QLabel(title)
    title_label.setStyleSheet(
        f"font-size: 15pt; font-weight: bold; color: {TEXT_PRIMARY}; border: none; background-color: transparent;")
    title_label.setFrameStyle(0)
    layout.addWidget(title_label)

    # Subtitle
    subtitle_label = QLabel(subtitle)
    subtitle_label.setStyleSheet(
        f"color: {TEXT_SECONDARY}; font-size: 10pt; border: none; background-color: transparent; margin-top: 2px;")
    subtitle_label.setWordWrap(True)
    subtitle_label.setFrameStyle(0)
    layout.addWidget(subtitle_label)

    # Bullet points
    for bullet in bullets:
        bullet_label = QLabel(f"• {bullet}")
        bullet_label.setStyleSheet(
            f"color: {TEXT_TERTIARY}; font-size: 9pt; border: none; background-color: transparent; padding-left: 2px;")
        bullet_label.setWordWrap(True)
        bullet_label.setFrameStyle(0)
        layout.addWidget(bullet_label)

    layout.addStretch()

    # 15px spacing before buttons
    layout.addSpacing(15)

    # Button container
    button_layout = QHBoxLayout()
    button_layout.setSpacing(8)
    button_layout.addStretch()

    # For special tiles (user_manual, feedback), show only "Open" button
    # For regular tabs, show "Go To" (if enabled) and optionally "User Guide"
    is_special_tile = tab_id in ['user_manual', 'feedback']

    if is_special_tile:
        # Special tiles: single "Open" button
        open_btn = QPushButton("Open")
        open_btn.setStyleSheet(get_button_stylesheet(enabled=False))
        open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_btn.clicked.connect(
            lambda: on_guide_clicked(tab_id, user_guide_url))
        button_layout.addWidget(open_btn)
    else:
        # Regular tabs: "Go To" button (always shown, disabled if enable_navigation is False)
        goto_btn = QPushButton("Go To")
        # Enable button only if both is_visible AND enable_navigation are True
        goto_btn.setEnabled(is_visible and enable_navigation)
        goto_btn.setStyleSheet(get_button_stylesheet(enabled=True))
        goto_btn.setCursor(
            Qt.CursorShape.PointingHandCursor if (is_visible and enable_navigation) else Qt.CursorShape.ArrowCursor)
        goto_btn.clicked.connect(lambda: on_goto_clicked(tab_id))
        button_layout.addWidget(goto_btn)

        button_layout.addSpacing(8)

        # User Guide button (only show if URL is provided)
        if user_guide_url:
            guide_btn = QPushButton("User Guide")
            guide_btn.setStyleSheet(get_button_stylesheet(enabled=False))
            guide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            guide_btn.clicked.connect(
                lambda: on_guide_clicked(tab_id, user_guide_url))
            button_layout.addWidget(guide_btn)

    button_layout.addStretch()
    layout.addLayout(button_layout)

    return tile
