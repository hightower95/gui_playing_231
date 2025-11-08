"""
File Operations Manager
Handles copying utils, templates, and configuring files for app deployment
"""
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import configparser
import logging


class FileOperationsManager:
    """Manages file operations for app deployment"""

    def __init__(self, installer_root: Path):
        """
        Initialize with installer root directory

        Args:
            installer_root: Path to productivity_app_installer directory
        """
        self.installer_root = Path(installer_root)
        self.utils_dir = self.installer_root / "utils"
        self.templates_dir = self.installer_root / "templates"

    def setup_files_in_target_folder(self, target_folder: Path, config: Dict[str, Any], overwrite: bool = True) -> bool:
        """
        Set up all necessary files in the target deployment folder

        Args:
            target_folder: Destination directory for app deployment
            config: Installation configuration dictionary
            overwrite: Whether to overwrite existing files

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            target_folder = Path(target_folder)
            target_folder.mkdir(parents=True, exist_ok=True)

            # Step 1: Copy utils folder
            if not self._copy_utils_folder(target_folder, overwrite):
                return False

            # Step 2: Copy and configure templates
            if not self._copy_and_configure_templates(target_folder, config, overwrite):
                return False

            # Step 3: Create any additional required files
            if not self._create_additional_files(target_folder, config, overwrite):
                return False

            logging.info(f"Successfully set up files in {target_folder}")
            return True

        except Exception as e:
            logging.error(f"Failed to set up files in {target_folder}: {e}")
            return False

    def _copy_utils_folder(self, target_folder: Path, overwrite: bool) -> bool:
        """Copy the utils folder to target directory"""
        try:
            target_utils = target_folder / "utils"

            if target_utils.exists() and not overwrite:
                logging.info(
                    f"Utils folder already exists at {target_utils}, skipping")
                return True

            if target_utils.exists() and overwrite:
                shutil.rmtree(target_utils)

            shutil.copytree(self.utils_dir, target_utils)
            logging.info(f"Copied utils folder to {target_utils}")
            return True

        except Exception as e:
            logging.error(f"Failed to copy utils folder: {e}")
            return False

    def _copy_and_configure_templates(self, target_folder: Path, config: Dict[str, Any], overwrite: bool) -> bool:
        """Copy template files and configure them"""
        try:
            # Copy run_app.pyw
            if not self._copy_template_file("run_app.pyw", target_folder, overwrite):
                return False

            # Copy and configure launch_config.ini
            if not self._configure_launch_config(target_folder, config, overwrite):
                return False

            return True

        except Exception as e:
            logging.error(f"Failed to copy and configure templates: {e}")
            return False

    def _copy_template_file(self, template_name: str, target_folder: Path, overwrite: bool) -> bool:
        """Copy a single template file"""
        try:
            source_file = self.templates_dir / template_name
            target_file = target_folder / template_name

            if not source_file.exists():
                logging.error(f"Template file not found: {source_file}")
                return False

            if target_file.exists() and not overwrite:
                logging.info(f"File {template_name} already exists, skipping")
                return True

            shutil.copy2(source_file, target_file)
            logging.info(f"Copied {template_name} to {target_file}")
            return True

        except Exception as e:
            logging.error(f"Failed to copy template file {template_name}: {e}")
            return False

    def _configure_launch_config(self, target_folder: Path, config: Dict[str, Any], overwrite: bool) -> bool:
        """Create and configure launch_config.ini with installation settings"""
        try:
            target_config = target_folder / "launch_config.ini"

            if target_config.exists() and not overwrite:
                logging.info(
                    f"launch_config.ini already exists, skipping configuration")
                return True

            # Create configuration content based on installation config
            config_content = self._generate_launch_config_content(config)

            # Write the configuration file
            target_config.write_text(config_content, encoding='utf-8')
            logging.info(
                f"Created configured launch_config.ini at {target_config}")
            return True

        except Exception as e:
            logging.error(f"Failed to configure launch_config.ini: {e}")
            return False

    def _generate_launch_config_content(self, config: Dict[str, Any]) -> str:
        """Generate launch_config.ini content from installation config"""
        app_name = config.get('app_name', 'ProductivityApp')
        library_name = config.get('library_name', 'productivity_app')
        venv_dir = config.get('venv_dir_name', '.test_venv')

        # Default upgrade settings (conservative)
        auto_upgrade_major = config.get('auto_upgrade_major_version', False)
        auto_upgrade_minor = config.get('auto_upgrade_minor_version', True)
        auto_upgrade_patches = config.get('auto_upgrade_patches', True)
        allow_test_releases = config.get(
            'allow_upgrade_to_test_releases', False)
        enable_log = config.get('enable_log', False)
        debug = config.get('debug', False)

        return f"""[Settings]
# Application Configuration
app_name = {app_name}
library_name = {library_name}
venv_dir_name = {venv_dir}

# Automatic upgrade permissions
auto_upgrade_major_version = {str(auto_upgrade_major).lower()}
auto_upgrade_minor_version = {str(auto_upgrade_minor).lower()}
auto_upgrade_patches = {str(auto_upgrade_patches).lower()}

# Test release handling  
allow_upgrade_to_test_releases = {str(allow_test_releases).lower()}

# Logging and debugging
enable_log = {str(enable_log).lower()}
debug = {str(debug).lower()}
"""

    def _create_additional_files(self, target_folder: Path, config: Dict[str, Any], overwrite: bool) -> bool:
        """Create any additional files needed for the deployment"""
        try:
            # Could add creation of update.pyw, about.pyw, etc. here in the future
            return True

        except Exception as e:
            logging.error(f"Failed to create additional files: {e}")
            return False

    def validate_installer_structure(self) -> bool:
        """Validate that the installer has all required components"""
        required_paths = [
            self.utils_dir,
            self.templates_dir,
            self.templates_dir / "run_app.pyw",
            self.templates_dir / "launch_config.ini"
        ]

        missing_paths = []
        for path in required_paths:
            if not path.exists():
                missing_paths.append(path)

        if missing_paths:
            logging.error(
                f"Missing required installer components: {missing_paths}")
            return False

        logging.info("Installer structure validation passed")
        return True


def setup_files_in_target_folder(target_folder: Path, config: Dict[str, Any],
                                 overwrite: bool = True, installer_root: Optional[Path] = None) -> bool:
    """
    Convenience function for setting up files in target folder

    Args:
        target_folder: Destination directory for app deployment
        config: Installation configuration dictionary
        overwrite: Whether to overwrite existing files
        installer_root: Path to installer root (auto-detected if None)

    Returns:
        bool: True if successful, False otherwise
    """
    if installer_root is None:
        # Auto-detect installer root (assume this file is in installer/scripts/)
        installer_root = Path(__file__).parent.parent.parent

    file_ops = FileOperationsManager(installer_root)

    # Validate installer structure first
    if not file_ops.validate_installer_structure():
        return False

    return file_ops.setup_files_in_target_folder(target_folder, config, overwrite)


# For backward compatibility and easier imports
__all__ = [
    'FileOperationsManager',
    'setup_files_in_target_folder'
]
