"""
Configuration for Check Multiple feature
"""

# Supported file types for import
SUPPORTED_FILE_EXTENSIONS = ['.csv', '.xlsx', '.txt']

# Preview row limit
PREVIEW_ROWS = 10

# Batch operation types
BATCH_OPERATIONS = {
    'find_opposites': 'Find Opposites',
    'find_alternatives': 'Find Alternatives',
    'lookup': 'Lookup',
    'get_material': 'Get Material',
    'check_status': 'Check Status'
}

# Define which connector fields to include in results for each operation
# 'all' means include all available connector fields
# Otherwise, specify a list of field names to include
OPERATION_RESULT_COLUMNS = {
    'find_opposites': 'all',  # Show all properties for opposites
    'find_alternatives': 'all',  # Show all properties for alternatives
    'lookup': 'all',  # Show all properties for lookups
    'get_material': [  # Only show material-related info
        'Part Number',
        'Part Code',
        'Material'
    ],
    'check_status': [  # Only show status-related info
        'Part Number',
        'Part Code',
        'Database Status'
    ]
}
