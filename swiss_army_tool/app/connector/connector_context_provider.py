"""
Example: Connector Context Provider

This shows how the Connector tab can provide additional context to Document Scanner results.
For example, if a part number is found, the Connector tab could provide:
- Connector type
- Pin count  
- Manufacturer
- Current stock levels
etc.
"""
from typing import List
from app.document_scanner.context_provider import ContextProvider
from app.document_scanner.search_result import SearchResult, Context


class ConnectorContextProvider(ContextProvider):
    """Provides connector-related context to search results"""

    def __init__(self, connector_model=None):
        """Initialize with connector model/data

        Args:
            connector_model: Reference to connector data/model (optional)
        """
        self.connector_model = connector_model
        self.enabled = True

    def get_context_name(self) -> str:
        """Get the name of this context provider"""
        return "Connector"

    def get_context(self, result: SearchResult) -> List[Context]:
        """Get connector context for a search result

        This method should look at the result data and determine if it can
        provide additional connector-related context.

        Args:
            result: The search result to provide context for

        Returns:
            List of Context objects
        """
        contexts = []
        context = Context(
            term="Test",
            context_owner="Connector",
            data_context={"Test": "Hello World"}
        )
        contexts.append(context)

        # Example: Look for part numbers in the result data
        for column, value in result.matched_row_data.items():
            # if column.lower() in ['part number', 'part_number', 'partnumber', 'pn']:
            # Look up part number in connector database
            connector_info = self._lookup_connector(str(value).strip())

            if connector_info:
                context = Context(
                    term=str(value),
                    context_owner="Connector",
                    data_context=connector_info
                )
                contexts.append(context)

        return contexts

    def _lookup_connector(self, part_number: str) -> dict:
        """Look up connector information by part number

        Args:
            part_number: The part number to look up

        Returns:
            Dictionary of connector data, or None if not found
        """
        if not self.connector_model:
            return None

        # Get all connectors from model
        connectors = self.connector_model.get_connectors()

        if not connectors:
            return None

        # Search for part number (try exact match first, then partial)
        part_number_clean = str(part_number).strip()

        # Try exact match on Part Number or Part Code
        for connector in connectors:
            if (connector.get('Part Number', '').strip() == part_number_clean or
                connector.get('Part Code', '').strip() == part_number_clean or
                    connector.get('Minified Part Code', '').strip() == part_number_clean):

                # Return relevant connector details
                return {
                    'Part Number': connector.get('Part Number', 'N/A'),
                    'Family': connector.get('Family', 'N/A'),
                    'Shell Type': connector.get('Shell Type', 'N/A'),
                    'Shell Size': connector.get('Shell Size', 'N/A'),
                    'Insert Arrangement': connector.get('Insert Arrangement', 'N/A'),
                    'Material': connector.get('Material', 'N/A'),
                    'Socket Type': connector.get('Socket Type', 'N/A'),
                    'Keying': connector.get('Keying', 'N/A'),
                    'Status': connector.get('Database Status', 'N/A')
                }

        # Try partial match (contains)
        part_number_lower = part_number_clean.lower()
        for connector in connectors:
            part_num = connector.get('Part Number', '').lower()
            part_code = connector.get('Part Code', '').lower()
            mini_code = connector.get('Minified Part Code', '').lower()

            if (part_number_lower in part_num or
                part_number_lower in part_code or
                    part_number_lower in mini_code):

                # Return relevant connector details
                return {
                    'Part Number': connector.get('Part Number', 'N/A'),
                    'Family': connector.get('Family', 'N/A'),
                    'Shell Type': connector.get('Shell Type', 'N/A'),
                    'Shell Size': connector.get('Shell Size', 'N/A'),
                    'Insert Arrangement': connector.get('Insert Arrangement', 'N/A'),
                    'Material': connector.get('Material', 'N/A'),
                    'Socket Type': connector.get('Socket Type', 'N/A'),
                    'Keying': connector.get('Keying', 'N/A'),
                    'Status': connector.get('Database Status', 'N/A')
                }

        # Not found
        return None

    def is_enabled(self) -> bool:
        """Check if this context provider is enabled"""
        return self.enabled

    def set_enabled(self, enabled: bool):
        """Enable or disable this context provider"""
        self.enabled = enabled
