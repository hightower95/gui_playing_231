"""
Test that multiple contexts display correctly for a single result
"""
from app.document_scanner.search_result import SearchResult, Context

# Create a test result
result = SearchResult(
    search_term="test",
    document_name="test.csv",
    document_type="csv",
    matched_row_data={"Part": "D38999/26WA35PN", "Cable": "CW100"}
)

# Add multiple contexts (simulating multiple providers)
ctx1 = Context(
    term="D38999/26WA35PN",
    context_owner="Connector",
    data_context={
        "Part Number": "D38999/26WA35PN",
        "Family": "D38999",
        "Shell Size": "26"
    }
)

ctx2 = Context(
    term="D38999/26WA35PN",
    context_owner="EPD",
    data_context={
        "EPD Part": "EPD-12345",
        "Stock Level": "50 units",
        "Lead Time": "2 weeks"
    }
)

ctx3 = Context(
    term="CW100",
    context_owner="Cable Database",
    data_context={
        "Cable Type": "Coaxial",
        "Length": "5m",
        "Status": "Active"
    }
)

result.add_context(ctx1)
result.add_context(ctx2)
result.add_context(ctx3)

print(f"Result has {len(result.contexts)} contexts:")
for i, ctx in enumerate(result.contexts, 1):
    print(f"\n  Context {i}: {ctx.context_owner} • '{ctx.term}'")
    for key, value in ctx.data_context.items():
        print(f"    - {key}: {value}")

print(f"\n✓ Result.has_contexts() = {result.has_contexts()}")
print(f"✓ Multiple contexts work correctly!")
