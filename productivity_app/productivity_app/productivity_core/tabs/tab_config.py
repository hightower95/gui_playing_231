"""
Tab Configuration Module

Centralized configuration for all application tabs including:
- Tab registration and ordering
- Lazy loading settings
- Dependency management
- Default focus behavior
- Visibility defaults
- Start page tile configuration

Configuration Structure:
    - id: Unique identifier for the tab (pulled from module's MODULE_ID)
    - presenter_class: The presenter/view class to instantiate
    - init_args: Lambda function returning arguments for __init__ (services, deps)
    - delay_ms: Milliseconds to wait before loading (for lazy loading)
    - dependencies: List of tab IDs that must be loaded first
    - visible: Default visibility on startup
    - view_from_presenter: Whether to get view from presenter.view property
    - default_focus: Whether this tab should be focused on startup

Tile Configuration (What is displayed on Start Page):
    Tile configs are defined directly in TAB_CONFIG below:
    - title: Display title (with emoji)
    - subtitle: Brief description
    - bullets: List of feature highlights
    - show_in_start_page: Whether to display tile on start page
    - user_guide_url: Optional URL for user guide
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
from .start_page import StartPageView
from .automated_reports import AutomatedReportsView


# ============================================================================
# TAB CONFIGURATION
# ============================================================================
# To add a new tab:
# 1. Import the presenter class above
# 2. Add an entry to TAB_CONFIG list below with tile config
# 3. Set default_focus=True on ONE tab to make it focused on startup
#
# init_args signature: lambda services, deps: [args...]
#   - services: AppContext (service provider/dependency injection)
#   - deps: Dict of loaded tab presenters this tab depends on
#
# MODULE_ID is pulled from the module's class definition (single source of truth)
# ============================================================================

TAB_CONFIG: List[Dict[str, Any]] = [
    {
        'id': StartPageView.MODULE_ID,
        'presenter_class': StartPageView,
        'init_args': lambda services, deps: [services],
        'delay_ms': 0,
        'view_from_presenter': False,
        'visible': True,
        'default_focus': True,
        'tile': {
            'title': "🏠 Start Page",
            'subtitle': "Your productivity hub",
            'bullets': [
                "Quick access to all tools",
                "Overview of available features",
                "Navigation center"
            ],
            'show_in_start_page': False,  # Don't show start page tile on start page
            'user_guide_url': None
        },
    },
    {
        'id': SettingsTab.MODULE_ID,
        'presenter_class': SettingsTab,
        'init_args': lambda services, deps: [services],
        'delay_ms': 0,
        'view_from_presenter': False,
        'visible': True,
        'default_focus': False,
        'tile': {
            'title': "⚙️ Settings",
            'subtitle': "Configure your workspace",
            'bullets': [
                "Manage tab visibility",
                "Customize appearance",
                "Configure preferences"
            ],
            'show_in_start_page': False,
            'user_guide_url': None
        },
    },
    {
        'id': ConnectorsPresenter.MODULE_ID,
        'presenter_class': ConnectorsPresenter,
        'init_args': lambda services, deps: [services],
        'delay_ms': 50,
        'visible': True,
        'default_focus': False,
        'tile': {
            'title': "🔌 Connector Search",
            'subtitle': "Search for connectors",
            'bullets': [
                "Quick search by name or part number",
                "Filter by connector type",
                "View detailed pinout diagrams"
            ],
            'show_in_start_page': True,
            'user_guide_url': 'https://example.com/connector-guide'
        },
    },
    {
        'id': EpdPresenter.MODULE_ID,
        'presenter_class': EpdPresenter,
        'init_args': lambda services, deps: [services],
        'delay_ms': 100,
        'visible': True,
        'default_focus': False,
        'tile': {
            'title': "📊 EPD Tools",
            'subtitle': "Electronic Part Database tools",
            'bullets': [
                "Search for electronic parts",
                "Identify best EPD matches",
                "View detailed part information"
            ],
            'show_in_start_page': True,
            'user_guide_url': None
        },
    },
    {
        'id': DocumentScannerModuleView.MODULE_ID,
        'presenter_class': DocumentScannerModuleView,
        'init_args': lambda services, deps: [services],
        'delay_ms': 200,
        'view_from_presenter': False,
        'visible': True,
        'default_focus': False,
        'tile': {
            'title': "📄 Document Scanner",
            'subtitle': "Search and analyze documents",
            'bullets': [
                "Scan multiple document types",
                "Advanced search capabilities",
                "Export and filter results"
            ],
            'show_in_start_page': True,
            'user_guide_url': None
        },
    },
    {
        'id': FaultFindingPresenter.MODULE_ID,
        'presenter_class': FaultFindingPresenter,
        'init_args': lambda services, deps: [services, deps['epd'].model],
        'delay_ms': 300,
        'dependencies': ['epd'],
        'visible': True,
        'tile': {
            'title': "🔍 Fault Finding",
            'subtitle': "Diagnose and troubleshoot issues",
            'bullets': [
                "Search for common faults",
                "View diagnostic procedures",
                "Access troubleshooting guides"
            ],
            'show_in_start_page': True,
            'user_guide_url': None
        },
    },
    {
        'id': RemoteDocsPresenter.MODULE_ID,
        'presenter_class': RemoteDocsPresenter,
        'init_args': lambda services, deps: [services],
        'delay_ms': 400,
        'visible': True,
        'tile': {
            'title': "📁 Remote Docs",
            'subtitle': "Access remote documentation",
            'bullets': [
                "Browse remote documents",
                "Download documentation",
                "Upload and share files"
            ],
            'show_in_start_page': True,
            'user_guide_url': None
        },
    },
    {
        'id': DevOpsPresenter.MODULE_ID,
        'presenter_class': DevOpsPresenter,
        'init_args': lambda services, deps: [services],
        'delay_ms': 450,
        'visible': True,
        'tile': {
            'title': "🔧 DevOps",
            'subtitle': "Development and operations tools",
            'bullets': [
                "Manage development workflows",
                "Access build and deployment tools",
                "Monitor system operations"
            ],
            'show_in_start_page': True,
            'enable_navigation': False,
            'user_guide_url': None
        },
    },
    {
        'id': AutomatedReportsView.MODULE_ID,
        'presenter_class': AutomatedReportsView,
        'init_args': lambda services, deps: [],
        'delay_ms': 500,
        'view_from_presenter': False,
        'visible': True,
        'default_focus': False,
        'tile': {
            'title': "📊 Automated Reports",
            'subtitle': "Searchable library of automated reports",
            'bullets': [
                "Browse reports by category and topic",
                "Filter by type, input, project, and scope",
                "Sort by name, date, type, or project"
            ],
            'show_in_start_page': True,
            'user_guide_url': None
        },
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
