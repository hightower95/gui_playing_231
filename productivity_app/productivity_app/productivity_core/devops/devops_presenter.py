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
