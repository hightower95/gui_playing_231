"""
EPD Presenter - Main coordinator for EPD module with sub-tabs
"""
from app.epd.epd_model import EpdModel
from app.core.base_presenter import BasePresenter
from app.epd.epd_tab import EpdModuleView


class EpdPresenter(BasePresenter):
    """Main EPD presenter coordinating SearchEpd and IdentifyBestEpd sub-modules"""

    def __init__(self, context):
        self.model = EpdModel(context)
        self.view = EpdModuleView(context, self.model)
        super().__init__(context, self.view, self.model, title="EPD Tools")

        self.bind()

    def bind(self):
        """Connect any top-level EPD module signals"""
        # The view creates its own sub-presenters and handles their signals
        pass

    def start_loading(self):
        """Start loading data for the EPD module"""
        self.view.start_loading()

    def get_current_presenter(self):
        """Get the currently active sub-presenter"""
        return self.view.get_current_presenter()
