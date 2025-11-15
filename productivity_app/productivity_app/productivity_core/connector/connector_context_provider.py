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
from ..document_scanner.context_provider import ContextProvider
from ..document_scanner.search_result import SearchResult, Context


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

        # Look for part numbers in the result data
        # Check each value in the result to see if it's a connector part number
        for column, value in result.matched_row_data.items():
            # Skip empty values
            if not value or str(value).strip() == "" or str(value).lower() == "nan":
                continue

            # Look up this value in connector database
            connector_info = self._lookup_connector(str(value).strip())

            if connector_info:
                print(
                    f"  ✓ Found connector match for '{value}' in column '{column}'")
                context = Context(
                    term=str(value),
                    context_owner="Connector",
                    data_context=connector_info
                )
                # Add callback to switch to Lookup tab for this connector
                part_num = connector_info.get('Part Number', '')
                context.add_callback(
                    "View in Lookup",
                    lambda pn=part_num: self._switch_to_lookup_tab(pn),
                    "Open this connector in the Connector Lookup tab"
                )
                contexts.append(context)
                # Note: We continue checking other columns to find all connector matches

        return contexts

    def _switch_to_lookup_tab(self, part_number: str):
        """Switch to the Connector Lookup tab and search for part number

        Note: This method requires the main window reference to be set.
        For now, it just prints a message. Implement tab switching when
        main window reference is available.

        Args:
            part_number: The part number to search for
        """
        print(
            f"TODO: Switch to Connector Lookup tab and search for '{part_number}'")
        # TODO: Implement when main window reference is available
        # Example implementation:
        # self.main_window.switch_to_tab("Connector")
        # self.connector_tab.switch_to_subtab("Lookup")
        # self.connector_tab.lookup_view.search_input.setText(part_number)

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

        # Try exact match on Part Number, Part Code, or Minified Part Code
        for connector in connectors:
            part_num = connector.get('Part Number', '').strip()
            part_code = connector.get('Part Code', '').strip()
            mini_code = connector.get('Minified Part Code', '').strip()

            # Case-insensitive exact match
            if (part_num.lower() == part_number_clean.lower() or
                part_code.lower() == part_number_clean.lower() or
                    mini_code.lower() == part_number_clean.lower()):

                print(f"    → Exact match found: {part_num}")
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

        # No exact match found - don't use partial matching as it's too unreliable
        # Partial matching would return wrong connectors (e.g., "D38999" matches all D38999 connectors)
        print(f"    → No exact match found for '{part_number_clean}'")
        return None

    def is_enabled(self) -> bool:
        """Check if this context provider is enabled"""
        return self.enabled

    def set_enabled(self, enabled: bool):
        """Enable or disable this context provider"""
        self.enabled = enabled
