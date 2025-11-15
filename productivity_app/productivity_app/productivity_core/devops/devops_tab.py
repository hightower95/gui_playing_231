"""
DevOps Module - Main tab containing Query Viewer and other DevOps tools
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from ..devops.QueryViewer import QueryViewerPresenter


class DevOpsModuleView(QWidget):
    """Main DevOps module containing Query Viewer and other sub-tabs"""

    def __init__(self, context):
        super().__init__()
        self.context = context

        # Create sub-presenters
        self.query_viewer_presenter = QueryViewerPresenter(context)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the tabbed interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        self.tabs = QTabWidget()

        # Add sub-tabs
        self.tabs.addTab(self.query_viewer_presenter.view, "Query Viewer")

        # TODO: Add more DevOps sub-tabs here in the future
        # Example: self.tabs.addTab(self.deployment_presenter.view, "Deployments")

        layout.addWidget(self.tabs)

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
