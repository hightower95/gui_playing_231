"""
Tab Configuration Module

Centralized configuration for all application tabs including:
- Tab registration and ordering
- Lazy loading settings
- Dependency management
- Default focus behavior
- Visibility defaults

Configuration Structure:
    - id: Unique identifier for the tab
    - presenter_class: The presenter/view class to instantiate
    - init_args: Lambda function returning arguments for __init__ (services, deps)
    - delay_ms: Milliseconds to wait before loading (for lazy loading)
    - dependencies: List of tab IDs that must be loaded first
    - visible: Default visibility on startup
    - view_from_presenter: Whether to get view from presenter.view property
    - default_focus: Whether this tab should be focused on startup
"""

from typing import Dict, List, Callable, Optional, Any
from ..core.app_context import AppContext
from ..epd.epd_presenter import EpdPresenter
from ..presenters.connectors_presenter import ConnectorsPresenter
from ..presenters.fault_presenter import FaultFindingPresenter
from ..document_scanner import DocumentScannerModuleView
from ..remote_docs import RemoteDocsPresenter
from ..devops import DevOpsPresenter
from .settings_tab import SettingsTab
from .start_page_tab import StartPageTab
from enum import Enum


# ============================================================================
# TAB CONFIGURATION
# ============================================================================
# To add a new tab:
# 1. Import the presenter class above
# 2. Add an entry to TAB_CONFIG list below
# 3. Set default_focus=True on ONE tab to make it focused on startup
#
# init_args signature: lambda services, deps: [args...]
#   - services: AppContext (service provider/dependency injection)
#   - deps: Dict of loaded tab presenters this tab depends on
# ============================================================================

class TabId(Enum):
    """Enum for all tab identifiers."""
    START_PAGE = 'start_page'
    SETTINGS = 'settings'
    CONNECTORS = 'connectors'
    EPD = 'epd'
    DOCUMENT_SCANNER = 'document_scanner'
    FAULT_FINDING = 'fault_finding'
    REMOTE_DOCS = 'remote_docs'
    DEVOPS = 'devops'


TAB_CONFIG: List[Dict[str, Any]] = [
    {
        'id': TabId.START_PAGE.value,
        'presenter_class': StartPageTab,
        'init_args': lambda services, deps: [services],
        'delay_ms': 0,  # Load immediately
        'view_from_presenter': False,  # This class IS the view
        'visible': True,  # Always visible in config
        'default_focus': True,  # Focus on startup
    },
    {
        'id': TabId.SETTINGS.value,
        'presenter_class': SettingsTab,
        'init_args': lambda services, deps: [services],
        'delay_ms': 0,  # Load immediately
        'view_from_presenter': False,  # This class IS the view
        'visible': True,
        'default_focus': False,
    },
    {
        'id': TabId.CONNECTORS.value,
        'presenter_class': ConnectorsPresenter,
        'init_args': lambda services, deps: [services],
        'delay_ms': 50,
        'visible': True,
        'default_focus': False,  # This tab will be focused on startup
    },
    {
        'id': TabId.EPD.value,
        'presenter_class': EpdPresenter,
        'init_args': lambda services, deps: [services],
        'delay_ms': 100,
        'visible': True,
        'default_focus': False,
    },
    {
        'id': TabId.DOCUMENT_SCANNER.value,
        'presenter_class': DocumentScannerModuleView,
        'init_args': lambda services, deps: [services],
        'delay_ms': 200,
        'view_from_presenter': False,  # This class IS the view
        'visible': True,
        'default_focus': True,
    },
    {
        'id': TabId.FAULT_FINDING.value,
        'presenter_class': FaultFindingPresenter,
        'init_args': lambda services, deps: [services, deps[TabId.EPD.value].model],
        'delay_ms': 300,
        'dependencies': [TabId.EPD.value],  # Requires EPD to be loaded first
        'visible': True,
    },
    {
        'id': TabId.REMOTE_DOCS.value,
        'presenter_class': RemoteDocsPresenter,
        'init_args': lambda services, deps: [services],
        'delay_ms': 400,
        'visible': True,
    },
    {
        'id': TabId.DEVOPS.value,
        'presenter_class': DevOpsPresenter,
        'init_args': lambda services, deps: [services],
        'delay_ms': 450,
        'visible': True,
    },
]


def get_tab_title(tab_config: Dict[str, Any]) -> str:
    """
    Extract tab title from presenter class.

    Tries to get title from:
    1. presenter_class.title (class attribute)
    2. Falls back to tab_config['id'] formatted as Title Case

    Args:
        tab_config: Tab configuration dictionary

    Returns:
        Title string for the tab
    """
    presenter_class = tab_config['presenter_class']

    # Try to get title from class attribute
    if hasattr(presenter_class, 'title'):
        return presenter_class.title

    # Fall back to formatting the ID
    tab_id = tab_config['id']
    return tab_id.replace('_', ' ').title()


def get_default_focus_tab() -> Optional[str]:
    """
    Get the ID of the tab that should be focused by default.

    Returns:
        Tab ID to focus, or None if no default is set
    """
    for tab_config in TAB_CONFIG:
        if tab_config.get('default_focus', False):
            return tab_config['id']
    return None


def get_tab_config_by_id(tab_id: str) -> Optional[Dict[str, Any]]:
    """
    Get tab configuration by ID.

    Args:
        tab_id: The unique identifier of the tab

    Returns:
        Tab configuration dict or None if not found
    """
    for config in TAB_CONFIG:
        if config['id'] == tab_id:
            return config
    return None


def get_tab_order() -> List[str]:
    """
    Get the ordered list of tab IDs.

    Returns:
        List of tab IDs in display order
    """
    return [config['id'] for config in TAB_CONFIG]


def validate_tab_config() -> List[str]:
    """
    Validate the tab configuration for common errors.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    tab_ids = set()
    default_focus_count = 0

    for i, config in enumerate(TAB_CONFIG):
        # Check required fields
        if 'id' not in config:
            errors.append(f"Tab at index {i} missing 'id' field")
            continue

        tab_id = config['id']

        # Check for duplicate IDs
        if tab_id in tab_ids:
            errors.append(f"Duplicate tab ID: {tab_id}")
        tab_ids.add(tab_id)

        # Check required fields
        if 'presenter_class' not in config:
            errors.append(f"Tab '{tab_id}' missing 'presenter_class'")
        if 'init_args' not in config:
            errors.append(f"Tab '{tab_id}' missing 'init_args'")
        if 'delay_ms' not in config:
            errors.append(f"Tab '{tab_id}' missing 'delay_ms'")

        # Check dependencies exist
        dependencies = config.get('dependencies', [])
        for dep_id in dependencies:
            if dep_id not in tab_ids and dep_id not in [c['id'] for c in TAB_CONFIG]:
                errors.append(
                    f"Tab '{tab_id}' has unknown dependency: {dep_id}")

        # Count default focus tabs
        if config.get('default_focus', False):
            default_focus_count += 1

    # Warn if multiple tabs have default focus
    if default_focus_count > 1:
        errors.append(
            f"Multiple tabs have 'default_focus=True' (found {default_focus_count})")

    return errors


# Validate configuration on module load
_validation_errors = validate_tab_config()
if _validation_errors:
    print("WARNING: Tab configuration has errors:")
    for error in _validation_errors:
        print(f"  - {error}")
