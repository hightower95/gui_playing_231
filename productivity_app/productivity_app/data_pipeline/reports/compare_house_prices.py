from productivity_app.data_pipeline.reports.decorator import report
from productivity_app.data_pipeline.parameters import ParameterEnum
from productivity_app.data_pipeline.models.street_price import StreetPrice


@report(
    title="Compare House Prices Report",
    description="Compares house prices from a street price list.",
    inputs=[
        ParameterEnum.StreetPriceList(
            name="street_price_list",
            description="List of street prices to compare",
        ),
        ParameterEnum.StreetPriceList(
            name="comparison_price_list",
            description="List of street prices to compare against",)
    ],
)
def compare_house_prices_report(
    street_price_list: list[StreetPrice],
    comparison_price_list: list[StreetPrice],
) -> str:
    """Compare house prices from a street price list

    Args:
        street_price_list: List of street prices to compare
        comparison_price_list: List of street prices to compare agains

    Returns:
        A string report comparing the house prices
    """
    report_lines = ["House Prices Comparison Report:"]
    comparison_dict = {
        (price.street, price.town): price.price for price in comparison_price_list
    }

    for street_price in street_price_list:
        key = (street_price.street, street_price.town)
        comparison_price = comparison_dict.get(key)
        if comparison_price is not None:
            difference = street_price.price - comparison_price
            report_lines.append(
                f"- {street_price.street}, {street_price.town}: "
                f"Current Price: {street_price.price}, "
                f"Comparison Price: {comparison_price}, "
                f"Difference: {difference}"
            )
        else:
            report_lines.append(
                f"- {street_price.street}, {street_price.town}: "
                f"Current Price: {street_price.price}, "
                "No comparison price available."
            )

    report_pretty = "\n".join(report_lines)

    print("report generated:")
    print(report_pretty)
    return report_pretty
