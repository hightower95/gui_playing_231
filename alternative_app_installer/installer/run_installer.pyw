
"""
Alternative App Installer - Main Entry Point

This script serves as the primary launcher for the alternative app installer.
It handles configuration loading, logging setup, installation detection,
and launches the GUI-based installation wizard.

File Extension: .pyw
- Uses .pyw extension to prevent console window from appearing on Windows
- Provides clean GUI-only experience for end users

Operation:
1. Sets up logging to capture installation process details
2. Loads installation settings from 'install_settings.ini'
3. Detects if this is a first-time installation or an upgrade (does not do anything with that information yet)
4. Launches the installer GUI for user interaction
"""

# Core imports for installer functionality
import traceback
from install_gui import launch_installer_gui
from configparser import ConfigParser, ExtendedInterpolation
from pathlib import Path
import logging


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================


# Setup logging to logs directory
# Creates a dedicated logs folder for installer output and debugging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)  # Create logs directory if it doesn't exist
log_file = log_dir / "installer.log"


# ============================================================================
# CONFIGURATION MANAGEMENT
# ============================================================================

def get_installation_settings() -> ConfigParser:
    import getpass
    """Read installation settings from install_settings.ini

    Loads configuration file that contains:
    - Installation paths and directories
    - Application settings and preferences  
    - Debug and simulation flags
    - Virtual environment configuration

    Returns:
        ConfigParser: Loaded configuration with ExtendedInterpolation
                     for variable substitution within config values
    """
    settings_path = Path(__file__).parent / "install_settings.ini"
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read(settings_path)

    # fill in f-strings in config values
    available_vars = {
        "parent_folder": str(Path(__file__).parent.parent),
        "username": getpass.getuser(),  # Get current user's name
    }

    # Process all sections and substitute template variables
    for section_name in config.sections():
        for key, value in config[section_name].items():
            # Replace f-string-like placeholders with actual values
            new_value = value
            for var_name, var_value in available_vars.items():
                placeholder = "{" + var_name + "}"
                new_value = new_value.replace(placeholder, var_value)

            # Update the config value if it was changed
            if new_value != value:
                config.set(section_name, key, new_value)

    return config


def log_installation_settings(config: ConfigParser):
    """Log all installation settings for debugging purposes

    Iterates through all configuration sections and keys,
    logging each setting for troubleshooting and verification.
    Helpful for debugging configuration issues.

    Args:
        config: ConfigParser instance containing installation settings
    """
    for section_name in config.sections():
        logging.debug(f"[{section_name}]")
        for key, value in config[section_name].items():
            logging.debug(f"  {key} = {value}")


def setup_logging():
    """Configure logging for the installer

    Sets up dual logging output:
    - File logging: Detailed debug information saved to installer.log
    - Console logging: Real-time feedback during installation process

    Log Format: Timestamp - Level - Message
    Level: DEBUG (captures all installation steps and configuration details)
    """
    logging.basicConfig(
        level=logging.DEBUG,  # Capture all debug information
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),  # Log to file for persistence
            logging.StreamHandler()         # Log to console for real-time feedback
        ]
    )


# ============================================================================
# INSTALLATION STATE DETECTION
# ============================================================================

def is_first_install() -> bool:
    """Determine if this is a first-time installation

    Checks for the presence of run_app.pyw in the parent directory,
    which indicates a previous installation. This helps the installer
    decide whether to:
    - Perform fresh installation (first time)
    - Handle upgrade/reinstallation (subsequent runs)

    Detection Logic:
    - Looks for run_app.pyw two levels up from installer directory
    - run_app.pyw is the main application launcher created during installation
    - If found: Previous installation exists
    - If not found: First-time installation

    Returns:
        bool: True if this is a first-time installation, False if upgrading
    """
    # Check for existing installation by looking for run_app.pyw in parent directory
    parent_parent = Path(__file__).parent.parent
    run_app_path = parent_parent / "run_app.pyw"
    return not run_app_path.exists()


# ============================================================================
# MAIN INSTALLATION PROCESS
# ============================================================================

# Initialize logging system before any other operations
setup_logging()

# Load installation configuration from file
installation_settings = get_installation_settings()

# Log all settings for debugging and verification
log_installation_settings(installation_settings)

# Detect installation state (first-time vs upgrade)
previous_install_detected = not is_first_install()
if previous_install_detected:
    logging.info(
        "Previous installation detected - preparing for upgrade/reinstallation.")
else:
    logging.info(
        "No previous installation detected - performing first-time installation.")

# Launch the GUI installer with loaded configuration
# The installer GUI handles all user interaction and installation steps
logging.info("Launching installer GUI...")
try:
    result = launch_installer_gui(installation_settings)
except Exception as e:
    logging.error(f"Installer GUI failed to launch: {e}")
    logging.error(traceback.format_exc())
    result = None

# Handle installation results and provide appropriate logging
if result:
    logging.info("Installation completed successfully.")
    logging.info("Application is ready to use.")
else:
    logging.error("Installation failed or was cancelled by user.")
    logging.error("Check logs above for specific error details.")
