"""
Configuration for Connector Lookup feature
"""

# Available filter options
FAMILIES = [
    "D38999",
    "VG",
    "MIL-DTL-38999",
    "EN3645",
    "AS85049",
    "KJB"
]

SHELL_TYPES = [
    "26 - Plug",
    "24 - Receptacle",
    "20 - Receptacle B",
    "21 - Plug",
    "22 - Receptacle A",
    "23 - Plug B",
    "25 - Receptacle C"
]

INSERT_ARRANGEMENTS = [
    "A - 1",
    "B - 2",
    "C - 3",
    "D - 4",
    "E - 5",
    "F - 6",
    "G - 7",
    "H - 8"
]

SOCKET_TYPES = [
    "Type A",
    "Type B",
    "Type C",
    "Type D",
    "Type E",
    "Type F"
]

KEYINGS = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "J",
    "K"
]

MATERIALS = [
    "Aluminum",
    "Stainless Steel",
    "Composite",
    "Titanium",
    "Brass",
    "Nickel Alloy"
]

# Default visible columns for results table
DEFAULT_VISIBLE_COLUMNS = [
    "Part Number",
    "Part Code",
    "Material",
    "Database Status"
]
