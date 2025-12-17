
Simply:
collectors should not know about schemas.

collectors produce raw data (DataType.DataFrame)
we 
We 



The key realization (state it explicitly)

There are three orthogonal concerns, not two:

Transport / Source format
CSV, Excel, JSON, API, database, etc.

Structural contract
“What columns / fields must exist?” (schema)

Domain model
Part, Connector, Signal, etc.

Your system currently couples (1) and (3) inside collectors. That is what feels wrong.

The correct role of a collector

A collector should answer one question only:

“How do I obtain raw data from this source?”

Not:

What model it becomes

What schema it uses

What report consumes it

Those are downstream decisions.

The architectural pivot you need
❌ Current mental model (what you are doing)
CSV → PartsListCollector → List[Part] → Report


This forces:

One collector per (model × filetype)

Schema logic embedded in collectors

Duplication explosion

✅ Correct mental model (what you want)
CSV → DataFrame → Schema → List[Part] → Report
Excel → DataFrame → Schema → List[Part] → Report


Collectors stop at DataFrame (or equivalent raw structure).

Schemas own conversion to domain objects.

What this means concretely
1. Collectors produce raw data, not models

Rewrite your collectors to be format-only.

@data_collector(
    name="CSVCollector",
    inputs=[Variables.FilePath],
    outputs=[DataTypes.TabularData]
)
def csv_collector(filepath: str) -> pd.DataFrame:
    return pd.read_csv(filepath)

@data_collector(
    name="ExcelCollector",
    inputs=[Variables.FilePath],
    outputs=[DataTypes.TabularData]
)
def excel_collector(filepath: str) -> pd.DataFrame:
    return pd.read_excel(filepath)


No Part. No schema lookup.

2. Schema conversion becomes a framework step

Your schema is already registered:

schema = data_schemas.get_schema(DataTypes.PartsList)


So the framework should be able to do:

TabularData → PartsList (via schema)


This is not a collector. It is type adaptation.

Introduce an explicit concept: “Schema Adapter”

This is the missing piece.

Conceptually:

TabularData + Schema → DomainObjects


This can be implicit in your framework.

Example: automatic schema application

When a report declares:

inputs=[Variables.PartsList]


The framework should:

See that no collector directly produces PartsList

Find a collector that produces TabularData

Find a schema that converts TabularData → PartsList

Compose the pipeline automatically

This is exactly the same composition you are doing manually now.

What happens to your current csv_to_parts_list_collector?

It goes away.

Or more precisely: it becomes implicit framework logic, not user-authored code.

What you wrote here:

df = csv_collector(filepath)
parts = schema.convert(df)


…is framework plumbing, not a business artifact.

Revised mental model of the system
What users define

Models

@dataclass
class Part: ...


Schemas

DataSchema(model=Part, ...)


Collectors

CSV → DataFrame
Excel → DataFrame


Reports

def report(parts: list[Part])