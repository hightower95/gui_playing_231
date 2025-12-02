"""
Context provider wiring - centralized dependency registration

This module declares all inter-module dependencies in one place.
Makes it easy to see what talks to what.

Two-phase initialization:
  Phase 1: Register placeholder/default providers immediately
  Phase 2: Update providers when async data loads (e.g., database)
"""

from typing import Dict, Any
from .app_context import AppContext
from ..connector.connector_context_provider import ConnectorContextProvider
# from ..epd.epd_context_provider import EpdContextProvider


def setup_context_providers(context: AppContext, tab_registry: Dict[str, Any]) -> None:
    """Setup all context providers after tabs are loaded

    Phase 1: Register default/placeholder providers
    Consumers can safely call methods on these providers immediately.

    Phase 2: Providers will be updated when async data loads (e.g., database)

    Args:
        context: AppContext instance
        tab_registry: Tab registry from MainWindow with loaded tabs
    """

    # Phase 1: Register initial providers (may be stubs/defaults)
    context.register_context_provider('connectors', ConnectorContextProvider())

    print("[AppContext] ✓ All context providers setup complete (Phase 1 - defaults)")
