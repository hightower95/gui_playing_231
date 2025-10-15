"""
Configuration for Identify Best EPD feature
"""
from app.core.config import FilterOperator


# Field-to-operator mappings
# Maps field names to their default operator
FIELD_OPERATOR_DEFAULTS = {
    # Text fields default to "contains"
    "Description": FilterOperator.CONTAINS.value,
    "Cable": FilterOperator.CONTAINS.value,
    "EPD": FilterOperator.CONTAINS.value,
    
    # Numeric fields default to "greater than or equal"
    "AWG": FilterOperator.GREATER_THAN_OR_EQUAL.value,
    "Rating (A)": FilterOperator.GREATER_THAN_OR_EQUAL.value,
    "Pins": FilterOperator.GREATER_THAN_OR_EQUAL.value,
}



