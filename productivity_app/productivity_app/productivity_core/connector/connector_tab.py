"""
Connector Module - Connector configuration and lookup interface with multiple sub-tabs
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PySide6.QtCore import QTimer


class ConnectorModuleView(QWidget):
    """Main Connector module containing Lookup and Check Multiple tabs"""

    # ========================================================================
    # MODULE IDENTIFIER - Single source of truth for this module
    # ========================================================================
    # Used for tab registration and sub-tab visibility management
    # ========================================================================

    MODULE_ID = 'connectors'

    # Tile configuration for start page
    TILE_CONFIG = {
        'module_id': MODULE_ID,  # Explicit module ID for clarity
        'title': "🔌 Connector Search",
        'subtitle': "Search for connectors",
        'bullets': [
            "Quick search by name or part number",
            "Filter by connector type",
            "View detailed pinout diagrams"
        ],
        'show_in_start_page': True,
        'user_guide_url': 'https://example.com/connector-guide'  # User guide button will appear
    }

    # ========================================================================
    # SUB-TAB IDENTIFIERS - Single source of truth
    # ========================================================================
    # All code that references sub-tabs should use these constants
    # When renaming: update here and everything else auto-updates
    # ========================================================================

    SUB_TAB_LOOKUP = 'lookup'
    SUB_TAB_CHECK_MULTIPLE = 'check_multiple'

    # Ordered list of all sub-tabs (used for iteration)
    SUB_TAB_ORDER = [
        SUB_TAB_LOOKUP,
        SUB_TAB_CHECK_MULTIPLE,
    ]

    # Display names (for UI labels)
    SUB_TAB_LABELS = {
        SUB_TAB_LOOKUP: 'Lookup',
        SUB_TAB_CHECK_MULTIPLE: 'Check Multiple',
    }

    def __init__(self, context, connector_model):
        super().__init__()
        self.context = context
        self.connector_model = connector_model

        # Import here to avoid circular imports
        from .Lookup.presenter import LookupConnectorPresenter
        from .CheckMultiple.presenter import CheckMultipleConnectorPresenter

        # Create sub-presenters
        self.lookup_presenter = LookupConnectorPresenter(
            context, connector_model)
        self.check_multiple_presenter = CheckMultipleConnectorPresenter(
            context, connector_model)

        # Store sub-tabs mapping using constants
        self.sub_tabs = {
            self.SUB_TAB_LOOKUP: (self.lookup_presenter.view, self.lookup_presenter),
            self.SUB_TAB_CHECK_MULTIPLE: (self.check_multiple_presenter.view, self.check_multiple_presenter),
        }

        # Connect signals for tab switching
        self.check_multiple_presenter.switch_to_lookup.connect(
            self._switch_to_lookup_with_search)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the tabbed interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        self.tabs = QTabWidget()

        # Add all sub-tabs
        self._add_sub_tabs()

        layout.addWidget(self.tabs)

    def _add_sub_tabs(self):
        """Add sub-tabs based on visibility settings"""
        from ..tabs.visibility_persistence import SubTabVisibilityConfig

        for sub_tab_id in self.SUB_TAB_ORDER:
            if sub_tab_id not in self.sub_tabs:
                continue

            view, presenter = self.sub_tabs[sub_tab_id]

            # Check if visible
            is_visible = SubTabVisibilityConfig.get_sub_tab_visibility(
                self.MODULE_ID, sub_tab_id)

            if is_visible:
                label = self.SUB_TAB_LABELS[sub_tab_id]
                self.tabs.addTab(view, label)

    def sub_tab_visibility_updated(self, sub_tab_names: dict):
        """Update sub-tab visibility

        Args:
            sub_tab_names: Dictionary mapping sub-tab IDs to visibility (True/False)
                          Example: {'lookup': True, 'check_multiple': False}
        """
        print(f"[Connector] Sub-tab visibility updated: {sub_tab_names}")

        # Clear existing tabs
        self.tabs.clear()

        # Re-add tabs based on new visibility
        for sub_tab_id in self.SUB_TAB_ORDER:
            if sub_tab_id not in self.sub_tabs:
                continue

            # Check new visibility
            if sub_tab_names.get(sub_tab_id, True):
                view, presenter = self.sub_tabs[sub_tab_id]
                label = self.SUB_TAB_LABELS[sub_tab_id]
                self.tabs.addTab(view, label)

        print(f"[Connector] Sub-tabs reloaded")

    def start_loading(self):
        """Start loading data for the currently active tab"""
        current_index = self.tabs.currentIndex()

        if current_index == 0:  # Lookup tab
            self.lookup_presenter.start_loading()
        elif current_index == 1:  # Check Multiple tab
            self.check_multiple_presenter.start_loading()

    def get_current_presenter(self):
        """Get the presenter for the currently active tab"""
        current_index = self.tabs.currentIndex()

        if current_index == 0:
            return self.lookup_presenter
        elif current_index == 1:
            return self.check_multiple_presenter

        return None

    def _switch_to_lookup_with_search(self, part_numbers_str: str):
        """Switch to Lookup tab, populate search box, and automatically trigger search"""
        print(
            f"DEBUG CONNECTOR_TAB: _switch_to_lookup_with_search called with: {part_numbers_str[:100]}...")

        # Switch to Lookup tab (index 0)
        self.tabs.setCurrentIndex(0)
        print("DEBUG CONNECTOR_TAB: Switched to tab 0")

        # Populate the search box
        self.lookup_presenter.view.search_input.setText(part_numbers_str)
        print(
            f"DEBUG CONNECTOR_TAB: Set search text to: {part_numbers_str[:100]}...")

        # Trigger the search after a short delay to ensure UI is ready
        # This ensures the tab switch is complete before triggering the search
        def trigger_search():
            self.lookup_presenter.view.search_requested.emit(
                {'search_text': part_numbers_str}
            )
            print("DEBUG CONNECTOR_TAB: Emitted search_requested signal (delayed)")

        QTimer.singleShot(100, trigger_search)  # 100ms delay
        print("DEBUG CONNECTOR_TAB: Scheduled search trigger")
