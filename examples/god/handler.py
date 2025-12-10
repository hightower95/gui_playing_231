
from god_module import handler, reporter, DataSources, param


def _have_api_key(context):
    return context.get("devops_api_key", None) is not None


@data_provider(
    provides=[DataSources.DevOps.QueryData],
    requires=[
        param('devops_query', str),
        param('devops_api_key', str),
    ],
    preconditions=[_have_api_key]
)
def load_query_data(devops_query: str, devops_api_key: str) -> List[dict]:
    handler.log("Loading DevOps query data...")
    # Simulate data loading
    data = handler.fetch_devops_data(devops_query, devops_api_key)
    if data is None:
        reporter.report_error("Failed to load DevOps data.")
        return None
    handler.log("DevOps query data loaded successfully.")
    return data


@reporter(
    report_name="DevOps Data Load Report",
    description="Report on the status of DevOps data loading operations.",
    inputs=[DataType.CableList,
            DataType.BillOfMaterials],
    outputs=[DataSources.Reports.DevOpsDataLoadReport],
    options=[
        param('include_summary', bool, default=True),
        param('detailed_logging', bool, default=False),
    ]
)
def generate_devops_data_load_report(
    query_data: List[dict],
    bom_document: dict,
    include_summary: bool,
    detailed_logging: bool
) -> dict:
    reporter.log("Generating DevOps Data Load Report...")
    report = {
        "summary": "",
        "details": []
    }

    if include_summary:
        report["summary"] = f"Loaded {len(query_data)} records from DevOps."

    if detailed_logging:
        for record in query_data:
            report["details"].append(
                f"Record ID: {record.get('id')}, Status: {record.get('status')}")

    reporter.log("DevOps Data Load Report generated successfully.")
    return report
