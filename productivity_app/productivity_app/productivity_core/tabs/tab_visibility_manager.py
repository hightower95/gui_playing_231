"""
Tab Visibility Manager

Handles all tab visibility operations including:
- Showing/hiding tabs
- Calculating correct tab positions
- Managing tab registry
- Checking visibility state
- Setting focus to specific tabs
"""

from typing import Dict, Any, Optional
from PySide6.QtWidgets import QTabWidget
from .tab_config import get_tab_order


class TabVisibilityManager:
    """
    Manages tab visibility and positioning in a QTabWidget.

    This class encapsulates all logic related to:
    - Showing and hiding tabs
    - Calculating correct insertion positions
    - Checking if tabs are visible
    - Setting focus to specific tabs
    """

    def __init__(self, tab_widget: QTabWidget, tab_registry: Dict[str, Dict[str, Any]]):
        """
        Initialize the tab visibility manager.

        Args:
            tab_widget: The QTabWidget containing all tabs
            tab_registry: Dict mapping tab_id -> {'presenter': ..., 'view': ..., 'title': ...}
        """
        self.tab_widget = tab_widget
        self.tab_registry = tab_registry

    def show_tab(self, tab_id: str) -> bool:
        """
        Show a tab by inserting it at the correct position.

        Args:
            tab_id: ID of tab to show (e.g., 'epd')

        Returns:
            True if tab was shown, False if already visible or not found
        """
        if tab_id not in self.tab_registry:
            print(
                f"[TabVisibilityManager] Warning: Tab '{tab_id}' not found in registry")
            return False

        tab_info = self.tab_registry[tab_id]

        # Check if tab is already visible
        if self.is_tab_visible(tab_id):
            print(
                f"[TabVisibilityManager] Tab '{tab_info['title']}' already visible")
            return False

        # Find correct position to insert
        position = self.get_tab_position(tab_id)

        # Insert tab at correct position
        self.tab_widget.insertTab(
            position, tab_info['view'], tab_info['title'])

        print(
            f"[TabVisibilityManager] Shown tab: {tab_info['title']} at position {position}")
        return True

    def hide_tab(self, tab_id: str) -> bool:
        """
        Hide a tab by removing it from the tab widget.

        Args:
            tab_id: ID of tab to hide (e.g., 'epd')

        Returns:
            True if tab was hidden, False if not visible or not found
        """
        if tab_id not in self.tab_registry:
            print(
                f"[TabVisibilityManager] Warning: Tab '{tab_id}' not found in registry")
            return False

        tab_info = self.tab_registry[tab_id]

        # Find the tab index
        tab_index = self._find_tab_index(tab_id)

        if tab_index >= 0:
            self.tab_widget.removeTab(tab_index)
            print(f"[TabVisibilityManager] Hidden tab: {tab_info['title']}")
            return True
        else:
            print(
                f"[TabVisibilityManager] Tab '{tab_info['title']}' was not visible")
            return False

    def is_tab_visible(self, tab_id: str) -> bool:
        """
        Check if a tab is currently visible.

        Args:
            tab_id: ID of tab to check

        Returns:
            True if tab is visible, False otherwise
        """
        return self._find_tab_index(tab_id) >= 0

    def set_focus(self, tab_id: str) -> bool:
        """
        Set focus to a specific tab.

        Args:
            tab_id: ID of tab to focus

        Returns:
            True if focus was set, False if tab not visible or not found
        """
        if tab_id not in self.tab_registry:
            print(
                f"[TabVisibilityManager] Warning: Tab '{tab_id}' not found in registry")
            return False

        tab_info = self.tab_registry[tab_id]
        tab_index = self._find_tab_index(tab_id)

        if tab_index >= 0:
            self.tab_widget.setCurrentIndex(tab_index)
            print(
                f"[TabVisibilityManager] Set focus to '{tab_info['title']}' tab")
            return True
        else:
            print(
                f"[TabVisibilityManager] Warning: Tab '{tab_id}' not visible, cannot set focus")
            return False

    def get_tab_position(self, tab_id: str) -> int:
        """
        Calculate the correct position to insert a tab based on TAB_CONFIG order.

        This ensures tabs maintain their configured order even when some are hidden.

        Args:
            tab_id: ID of tab to position

        Returns:
            Index where tab should be inserted (0-based)
        """
        # Get tab order from config
        tab_order = get_tab_order()

        if tab_id not in tab_order:
            # If not in config, insert at end (before settings tab if it exists)
            return self.tab_widget.count() - 1 if self.tab_widget.count() > 0 else 0

        target_index = tab_order.index(tab_id)

        # Count how many tabs before this one are currently visible
        position = 0
        for i in range(target_index):
            other_tab_id = tab_order[i]
            if self.is_tab_visible(other_tab_id):
                position += 1

        return position

    def _find_tab_index(self, tab_id: str) -> int:
        """
        Find the current index of a tab in the tab widget.

        Args:
            tab_id: ID of tab to find

        Returns:
            Index of tab (0-based), or -1 if not visible
        """
        if tab_id not in self.tab_registry:
            return -1

        tab_view = self.tab_registry[tab_id]['view']

        for i in range(self.tab_widget.count()):
            if self.tab_widget.widget(i) == tab_view:
                return i

        return -1

    def get_visible_tabs(self) -> list[str]:
        """
        Get list of currently visible tab IDs in display order.

        Returns:
            List of tab IDs that are currently visible
        """
        visible_tabs = []
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            # Find which tab this widget belongs to
            for tab_id, tab_info in self.tab_registry.items():
                if tab_info['view'] == widget:
                    visible_tabs.append(tab_id)
                    break
        return visible_tabs

    def get_current_tab_id(self) -> Optional[str]:
        """
        Get the ID of the currently focused tab.

        Returns:
            Tab ID of current tab, or None if no tab is focused
        """
        current_widget = self.tab_widget.currentWidget()
        if not current_widget:
            return None

        # Find which tab this widget belongs to
        for tab_id, tab_info in self.tab_registry.items():
            if tab_info['view'] == current_widget:
                return tab_id

        return None
