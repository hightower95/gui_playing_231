"""
E3.series Configuration
"""

# E3 COM Interface settings
E3_COM_PROG_ID = "CT.Application"  # E3.series COM ProgID

# Cache settings
E3_CACHE_DIRECTORY = "e3_caches"
E3_CACHE_FILE_PATTERN = "e3_connector_cache_*.csv"

# Default timeout for E3 operations (seconds)
E3_OPERATION_TIMEOUT = 300  # 5 minutes

# Connector fields to extract from E3
E3_CONNECTOR_FIELDS = [
    'Part Number',
    'Part Code',
    'Material',
    'Database Status',
    'Family',
    'Shell Type',
    'Shell Size',
    'Insert Arrangement',
    'Socket Type',
    'Keying',
    'Description',
    'Manufacturer',
    'Manufacturer Part Number',
    'E3 Project',
    'E3 Sheet',
    'E3 Device Name'
]

# Progress update intervals
E3_PROGRESS_UPDATE_FREQUENCY = 10  # Update progress every N connectors
