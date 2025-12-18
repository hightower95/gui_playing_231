

from typing import List


class DataTypes:
    String = "String"
    StringList = "StringList"


class Parameter:
    def __init__(self, data_type: DataTypes, name: str, description: str):
        self.data_type = data_type
        self.name = name
        self.description = description


DataList = Parameter(DataTypes.String, name="Data List",
                     description="List of data items")


class Register:
    def __init__(self):
        self.registered = []

    def register(self, item):
        self.registered.append(item)

    def collector(self, name: str, inputs: List, outputs: List[DataTypes]):
        def decorator(func):
            self.register(func)
            return func
        return decorator

    def reporter(self, name: str, inputs: List, outputs: List[DataTypes]):
        def decorator(func):
            self.register(func)
            return func
        return decorator


register = Register()


@register.collector(
    name="Sample Collector",
    inputs=[],
    outputs=[DataTypes.StringList])
def sample_collector() -> list[str]:
    return ["Item1", "Item2", "Item3"]


@register.reporter(
    name="Sample Report",
    input=[DataList],
    outputs=[]
)
def do_report(value_list):
    print("Report:")
    for value in value_list:
        print(f"- {value}")
