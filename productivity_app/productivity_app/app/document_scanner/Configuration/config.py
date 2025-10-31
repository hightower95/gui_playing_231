"""
Document Scanner Configuration - Document type definitions
"""

# Document type definitions - easily extensible
DOCUMENT_TYPES = {
    'default': {
        'name': 'Default',
        'description': 'Generic document with standard search',
        'default_search_behavior': 'contains',
        'case_sensitive': False
    },
    'part_numbers': {
        'name': 'Part Numbers',
        'description': 'Documents containing part number lookups',
        'default_search_behavior': 'exact',
        'case_sensitive': True
    },
    'specifications': {
        'name': 'Specifications',
        'description': 'Technical specification documents',
        'default_search_behavior': 'contains',
        'case_sensitive': False
    },
    'custom': {
        'name': 'Custom',
        'description': 'User-defined custom document type',
        'default_search_behavior': 'contains',
        'case_sensitive': False
    }
}

# Supported file extensions
SUPPORTED_EXTENSIONS = ['.csv', '.txt', '.xlsx', '.xls']

# Cache settings
CACHE_DIRECTORY = 'document_scanner_cache'
CONFIG_FILENAME = 'documents_config.json'
