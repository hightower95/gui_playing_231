
class FileSchema:
    def __init__(self, name: str, required_columns: list[str]):
        self.name = name
        self.required_columns = required_columns

    def validate(self, data) -> bool:
        return all(col in data.columns for col in self.required_columns)
