"""
Utilities package for ProductivityApp
Common utilities for version management, logging, and configuration
"""

from .version_manager import (
    parse_version,
    is_stable_version,
    get_installed_version,
    get_all_versions,
    should_upgrade,
    upgrade_to_version
)

from .logging_utils import (
    log_upgrade_event,
    write_comprehensive_log
)

from .config_utils import (
    load_launch_config,
    create_default_launch_config
)

__all__ = [
    # Version management
    'parse_version',
    'is_stable_version', 
    'get_installed_version',
    'get_all_versions',
    'should_upgrade',
    'upgrade_to_version',
    
    # Logging
    'log_upgrade_event',
    'write_comprehensive_log',
    
    # Configuration
    'load_launch_config',
    'create_default_launch_config'
]