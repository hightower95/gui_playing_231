"""
DevOps Module - Main tab containing Query Viewer and other DevOps tools
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from ..devops.QueryViewer import QueryViewerPresenter


class DevOpsModuleView(QWidget):
    """Main DevOps module containing Query Viewer and other sub-tabs"""

    # ========================================================================
    # Module Constants - Single source of truth for module identification
    # ========================================================================
    MODULE_ID = 'devops'
    SUB_TAB_QUERY_VIEWER = 'query_viewer'

    SUB_TAB_ORDER = [SUB_TAB_QUERY_VIEWER]
    SUB_TAB_LABELS = {
        SUB_TAB_QUERY_VIEWER: 'Query Viewer',
    }

    def __init__(self, context):
        super().__init__()
        self.context = context

        # Create sub-presenters
        self.query_viewer_presenter = QueryViewerPresenter(context)

        # Sub-tabs mapping
        self.sub_tabs = {
            self.SUB_TAB_QUERY_VIEWER: (self.query_viewer_presenter.view, self.query_viewer_presenter),
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

        # TODO: Add more DevOps sub-tabs here in the future
        # Example: self.tabs.addTab(self.deployment_presenter.view, "Deployments")

    def start_loading(self):
        """Start loading data - called during lazy loading"""
        print("DevOps: Starting...")

        # Initialize all presenters
        self.query_viewer_presenter.start_loading()

    def get_current_presenter(self):
        """Get the presenter for the currently active tab"""
        current_index = self.tabs.currentIndex()

        if current_index == 0:
            return self.query_viewer_presenter

        return None

    def sub_tab_visibility_updated(self, sub_tab_names: dict):
        """Update sub-tab visibility and reload tabs

        Args:
            sub_tab_names: Dictionary mapping sub-tab IDs to visibility state
        """
        self._add_sub_tabs()
