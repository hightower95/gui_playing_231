"""
EPD Module - Electronic Parts Data analysis interface with multiple sub-tabs
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from .SearchEpd.presenter import SearchEpdPresenter
from .IdentifyBestEpd.presenter import IdentifyBestEpdPresenter


class EpdModuleView(QWidget):
    """Main EPD module containing SearchEpd and IdentifyBestEpd tabs"""

    # ========================================================================
    # Module Constants - Single source of truth for module identification
    # ========================================================================
    MODULE_ID = 'epd'
    SUB_TAB_SEARCH = 'search'
    SUB_TAB_IDENTIFY_BEST = 'identify_best'
    
    SUB_TAB_ORDER = [SUB_TAB_SEARCH, SUB_TAB_IDENTIFY_BEST]
    SUB_TAB_LABELS = {
        SUB_TAB_SEARCH: 'Search',
        SUB_TAB_IDENTIFY_BEST: 'Identify Best',
    }

    def __init__(self, context, epd_model):
        super().__init__()
        self.context = context
        self.epd_model = epd_model

        # Create sub-presenters
        self.search_presenter = SearchEpdPresenter(context, epd_model)
        self.identify_presenter = IdentifyBestEpdPresenter(context, epd_model)

        # Sub-tabs mapping
        self.sub_tabs = {
            self.SUB_TAB_SEARCH: (self.search_presenter.view, self.search_presenter),
            self.SUB_TAB_IDENTIFY_BEST: (self.identify_presenter.view, self.identify_presenter),
        }

        self._setup_ui()

    def _setup_ui(self):
        """Setup the tabbed interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        self.tabs = QTabWidget()

        # Add sub-tabs with visibility control
        self._add_sub_tabs()

        layout.addWidget(self.tabs)

    def _add_sub_tabs(self):
        """Add sub-tabs based on visibility configuration"""
        from ..tabs.settings_tab import SubTabVisibilityConfig

        # Clear existing tabs
        self.tabs.clear()

        # Add each sub-tab if visible
        for sub_tab_id in self.SUB_TAB_ORDER:
            visible = SubTabVisibilityConfig.get_sub_tab_visibility(
                self.MODULE_ID, sub_tab_id)

            if sub_tab_id in self.sub_tabs:
                view, presenter = self.sub_tabs[sub_tab_id]
                if visible:
                    self.tabs.addTab(view, self.SUB_TAB_LABELS[sub_tab_id])

    def start_loading(self):
        """Start loading data for the currently active tab"""
        current_index = self.tabs.currentIndex()

        if current_index == 0:  # Search EPD tab
            self.search_presenter.start_loading()
        elif current_index == 1:  # Identify Best EPD tab
            self.identify_presenter.start_loading()

    def get_current_presenter(self):
        """Get the presenter for the currently active tab"""
        current_index = self.tabs.currentIndex()

        if current_index == 0:
            return self.search_presenter
        elif current_index == 1:
            return self.identify_presenter

        return None

    def sub_tab_visibility_updated(self, sub_tab_names: dict):
        """Update sub-tab visibility and reload tabs
        
        Args:
            sub_tab_names: Dictionary mapping sub-tab IDs to visibility state
        """
        self._add_sub_tabs()
