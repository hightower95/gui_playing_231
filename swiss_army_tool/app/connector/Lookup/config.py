"""
Configuration for Connector Lookup feature
"""

# Available filter options for multi-select
CONNECTOR_TYPES = [
    "DB9",
    "DB15",
    "DB25",
    "RJ45",
    "USB-C",
    "HDMI",
    "VGA",
    "DVI",
    "DisplayPort"
]

GENDERS = [
    "Male",
    "Female",
    "Hermaphroditic"
]

MANUFACTURERS = [
    "Amphenol",
    "TE Connectivity",
    "Molex",
    "Phoenix Contact",
    "Harting",
    "Weidmüller",
    "Generic"
]

# Default visible columns for results table
DEFAULT_VISIBLE_COLUMNS = [
    "name",
    "type",
    "gender",
    "pin_count",
    "manufacturer",
    "part_number"
]
