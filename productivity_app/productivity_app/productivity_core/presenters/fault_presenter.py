from productivity_core.models.fault_model import FaultFindingModel
from productivity_core.tabs.fault_finding import FaultFindingView
from productivity_core.core.base_presenter import BasePresenter


class FaultFindingPresenter(BasePresenter):
    def __init__(self, context, epd_model, contextualizers=None, title="Fault Finding"):
        self.context = context
        self.model = FaultFindingModel(epd_model)
        self.view = FaultFindingView()
        super().__init__(context, self.view, self.model, title)
        self.contextualizers = contextualizers or []
        self.title = title

        self.view.searchRequested.connect(self._on_search)

    def _on_search(self, term: str):
        results = self.model.search(term)
        for ctx in self.contextualizers:
            results = ctx.contextualize(results)
        self.view.display_results(results)
