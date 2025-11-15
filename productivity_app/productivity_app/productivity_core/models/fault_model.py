from ..shared.result_object import ResultObject


class FaultFindingModel:
    def __init__(self, epd_model):
        self.epd_model = epd_model  # We’ll pass this in from main setup

    def search(self, term: str):
        results = []
        df = self.epd_model.get_all()

        mask = df.apply(lambda r: r.astype(str).str.contains(
            term, case=False).any(), axis=1)
        for _, row in df[mask].iterrows():
            results.append(ResultObject(source="EPD", data=row.to_dict()))
        return results
