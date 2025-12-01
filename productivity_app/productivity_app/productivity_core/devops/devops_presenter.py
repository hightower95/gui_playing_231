"""
DevOps Presenter - Manages the DevOps module
"""
from PySide6.QtCore import QObject
from ..devops import DevOpsModuleView


class DevOpsPresenter(QObject):
    """Presenter for the DevOps module"""

    def __init__(self, context):
        super().__init__()
        self.context = context
        self.view = DevOpsModuleView(context)
        self.title = "🔧 DevOps"

    def start_loading(self):
        """Initialize the presenter - called during lazy tab loading"""
        self.view.start_loading()

    def sub_tab_visibility_updated(self, sub_tab_names: dict):
        """Update sub-tab visibility
        
        Args:
            sub_tab_names: Dictionary mapping sub-tab IDs to visibility state
        """
        self.view.sub_tab_visibility_updated(sub_tab_names)
