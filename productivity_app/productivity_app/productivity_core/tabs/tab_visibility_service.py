"""
Tab Visibility Service

Centralized service for managing tab visibility across the application.
Handles both UI state (through TabVisibilityManager) and persistence (through config).

This service is registered in AppContext and can be accessed by any component.
"""

from typing import Optional, Dict, Any
from PySide6.QtWidgets import QTabWidget
from PySide6.QtCore import QObject, Signal
from .tab_visibility_manager import TabVisibilityManager
from .visibility_persistence import TabVisibilityPersistence, TAB_VISIBILITY_CONFIG


class TabVisibilityService(QObject):
    """
    Service for managing tab visibility with persistence.

    This service:
    - Manages UI visibility through TabVisibilityManager
    - Persists state through TabVisibilityConfig
    - Emits signals when visibility changes
    - Provides a clean API for other components

    Register in AppContext:
        services.register('tab_visibility', TabVisibilityService())

    Usage:
        tab_service = services.get('tab_visibility')
        tab_service.show_tab('epd')
        tab_service.hide_tab('connectors')
        is_visible = tab_service.is_tab_visible('document_scanner')
    """

    # Signals
    tab_visibility_changed = Signal(str, bool)  # (tab_id, visible)

    def __init__(self):
        super().__init__()
        self._ui_manager: Optional[TabVisibilityManager] = None
        self._initialized = False

    def initialize(self, tab_widget: QTabWidget, tab_registry: Dict[str, Dict[str, Any]]):
        """
        Initialize the service with UI components.

        This should be called once during application startup after tabs are loaded.

        Args:
            tab_widget: The QTabWidget containing all tabs
            tab_registry: Dict mapping tab_id -> {'presenter': ..., 'view': ..., 'title': ...}
        """
        if self._initialized:
            print("[TabVisibilityService] Warning: Already initialized")
            return

        self._ui_manager = TabVisibilityManager(tab_widget, tab_registry)
        self._initialized = True
        print("[TabVisibilityService] Initialized with UI manager")

    def show_tab(self, tab_id: str, persist: bool = True) -> bool:
        """
        Show a tab and optionally persist the change.

        Args:
            tab_id: ID of tab to show
            persist: Whether to save state to config (default: True)

        Returns:
            True if successful, False otherwise
        """
        if not self._initialized:
            print(
                f"[TabVisibilityService] Not initialized, cannot show tab '{tab_id}'")
            return False

        # Update UI
        success = self._ui_manager.show_tab(tab_id)

        if success and persist:
            # Persist to config
            TabVisibilityPersistence.set_tab_visibility(tab_id, True)
            # Emit signal
            self.tab_visibility_changed.emit(tab_id, True)

        return success

    def hide_tab(self, tab_id: str, persist: bool = True) -> bool:
        """
        Hide a tab and optionally persist the change.

        Args:
            tab_id: ID of tab to hide
            persist: Whether to save state to config (default: True)

        Returns:
            True if successful, False otherwise
        """
        if not self._initialized:
            print(
                f"[TabVisibilityService] Not initialized, cannot hide tab '{tab_id}'")
            return False

        # Update UI
        success = self._ui_manager.hide_tab(tab_id)

        if success and persist:
            # Persist to config
            TabVisibilityPersistence.set_tab_visibility(tab_id, False)
            # Emit signal
            self.tab_visibility_changed.emit(tab_id, False)

        return success

    def is_tab_visible(self, tab_id: str, check_ui: bool = False) -> bool:
        """
        Check if a tab is visible.

        Args:
            tab_id: ID of tab to check
            check_ui: If True, check UI state; if False, check config (default: False)

        Returns:
            True if tab is visible, False otherwise
        """
        if check_ui and self._initialized:
            return self._ui_manager.is_tab_visible(tab_id)
        else:
            # Check persisted config
            return TabVisibilityPersistence.get_tab_visibility(tab_id)

    def set_focus(self, tab_id: str) -> bool:
        """
        Set focus to a specific tab.

        Args:
            tab_id: ID of tab to focus

        Returns:
            True if successful, False otherwise
        """
        if not self._initialized:
            print(
                f"[TabVisibilityService] Not initialized, cannot set focus to '{tab_id}'")
            return False

        return self._ui_manager.set_focus(tab_id)

    def get_visible_tabs(self) -> list[str]:
        """
        Get list of currently visible tab IDs.

        Returns:
            List of tab IDs that are currently visible in UI
        """
        if not self._initialized:
            return []

        return self._ui_manager.get_visible_tabs()

    def get_current_tab_id(self) -> Optional[str]:
        """
        Get the ID of the currently focused tab.

        Returns:
            Tab ID or None
        """
        if not self._initialized:
            return None

        return self._ui_manager.get_current_tab_id()

    def get_all_visibility_settings(self) -> Dict[str, bool]:
        """
        Get all tab visibility settings from config.

        Returns:
            Dict mapping tab_id -> visible (True/False)
        """
        return TabVisibilityPersistence.get_visibility_settings()

    def set_all_visibility_settings(self, settings: Dict[str, bool]) -> bool:
        """
        Set all tab visibility settings and apply to UI.

        Args:
            settings: Dict mapping tab_id -> visible

        Returns:
            True if successful, False otherwise
        """
        # Save to config
        success = TabVisibilityPersistence.set_visibility_settings(settings)

        if success and self._initialized:
            # Apply each setting to UI
            for tab_id, visible in settings.items():
                if visible:
                    self._ui_manager.show_tab(tab_id)
                else:
                    self._ui_manager.hide_tab(tab_id)

                # Emit signal for each change
                self.tab_visibility_changed.emit(tab_id, visible)

        return success

    def reset_to_defaults(self) -> bool:
        """
        Reset all tab visibility to default values from config.

        Returns:
            True if successful, False otherwise
        """
        defaults = {config['id']: config['default']
                    for config in TAB_VISIBILITY_CONFIG}
        return self.set_all_visibility_settings(defaults)

    @property
    def is_initialized(self) -> bool:
        """Check if service has been initialized with UI components"""
        return self._initialized
