"""
Check Multiple Connector Presenter - Placeholder
"""
from PySide6.QtCore import QObject
from app.connector.CheckMultiple.view import CheckMultipleConnectorView


class CheckMultipleConnectorPresenter(QObject):
    """Placeholder presenter for Check Multiple feature"""

    def __init__(self, context, connector_model):
        super().__init__()
        self.context = context
        self.model = connector_model
        self.view = CheckMultipleConnectorView()

    def start_loading(self):
        """Placeholder for loading"""
        pass
