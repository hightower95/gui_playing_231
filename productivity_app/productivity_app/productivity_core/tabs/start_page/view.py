"""
Start Page View - Welcome page with tile-based app overview

This is the main orchestration view that assembles all start page components.
"""
from typing import Optional
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea,
                               QGridLayout)
from PySide6.QtCore import Qt
from ...core.app_context import AppContext
from ...core.config_manager import AppSettingsConfig
from .data import get_tile_data
from .components import create_tile
from .theme import get_scrollbar_stylesheet, BACKGROUND, ACCENT_BLUE, TEXT_MUTED


class StartPageView(QWidget):
    """Start page tab shown on application startup

    Displays a grid of tiles representing all available tabs with:
    - Navigation buttons to switch to tabs
    - User guide links
    - Modern hover effects and animations
    """

    TAB_TITLE = "🏠 Start Page"
    MODULE_ID = 'start_page'
    CONFIG_KEY = 'start_page_closed'

    def __init__(self, services: Optional[AppContext] = None, parent: Optional[QWidget] = None):
        """Initialize start page view

        Args:
            services: AppContext for accessing tab_visibility_service
            parent: Qt parent widget
        """
        super().__init__(parent)
        self.services = services
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI with tile-based layout"""
        self.setStyleSheet(f"background-color: {BACKGROUND};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 20)

        # Title
        title = QLabel("Engineering Productivity Toolkit")
        title.setStyleSheet(
            f"font-size: 14pt; font-weight: bold; color: {ACCENT_BLUE}; padding: 10px;")
        title.setFrameStyle(0)
        layout.addWidget(title)

        # Scroll area for tiles
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(get_scrollbar_stylesheet())

        # Container widget for tiles
        tiles_container = QWidget()
        tiles_container.setStyleSheet("background-color: transparent;")
        scroll.setWidget(tiles_container)

        # Grid layout for tiles (3 columns)
        tiles_layout = QGridLayout(tiles_container)
        tiles_layout.setSpacing(12)
        tiles_layout.setContentsMargins(40, 10, 40, 0)

        # Create tiles with real tab data - simple loop as requested
        tile_data = get_tile_data()
        for idx, (title_text, subtitle, bullets, tab_id, is_visible) in enumerate(tile_data):
            row = idx // 3
            col = idx % 3
            tile = create_tile(
                parent_window=self,
                title=title_text,
                subtitle=subtitle,
                bullets=bullets,
                tab_id=tab_id,
                is_visible=is_visible,
                on_goto_clicked=self._navigate_to_tab,
                on_guide_clicked=self._show_user_guide
            )
            tiles_layout.addWidget(tile, row, col)

        layout.addWidget(scroll)

        # Version subtitle (at bottom)
        version = QLabel("Version 1.2.3")
        version.setStyleSheet(
            f"font-size: 9pt; color: {TEXT_MUTED}; padding: 10px;")
        version.setFrameStyle(0)
        layout.addWidget(version)

    def _navigate_to_tab(self, tab_id: str):
        """Navigate to a specific tab using tab_visibility_service

        Args:
            tab_id: The ID of the tab to navigate to
        """
        if not self.services:
            print(f"[StartPageView] Cannot navigate - no services available")
            return

        tab_visibility_service = self.services.get('tab_visibility')
        if tab_visibility_service:
            # Ensure tab is visible
            if not tab_visibility_service.is_tab_visible(tab_id):
                tab_visibility_service.set_tab_as_visible(tab_id)
            # Switch focus to it
            tab_visibility_service.set_focus(tab_id)
            print(f"[StartPageView] Navigated to {tab_id} tab")
        else:
            print(f"[StartPageView] tab_visibility_service not available")

    def _show_user_guide(self, tab_id: str):
        """Show user guide for a specific tab (placeholder)

        Args:
            tab_id: The ID of the tab
        """
        print(f"[StartPageView] User guide requested for: {tab_id}")
        # TODO: Implement user guide system

    def _on_close_clicked(self):
        """Handle close button clicked - hide tab until next run"""
        # Mark as closed for this session
        AppSettingsConfig.set_setting(self.CONFIG_KEY, True)

        # Hide the tab using TabVisibilityService
        if self.services:
            tab_visibility_service = self.services.get('tab_visibility')
            if tab_visibility_service:
                # Don't persist - we want it visible again on next run
                tab_visibility_service.set_tab_as_hidden(
                    self.MODULE_ID, persist=False)

        print(f"[StartPageView] Closed for this session")

    @staticmethod
    def should_show_on_startup() -> bool:
        """Check if start page should be shown on startup

        Returns:
            True if should be shown, False if user closed it this session
        """
        return not AppSettingsConfig.get_setting(StartPageView.CONFIG_KEY, False)
