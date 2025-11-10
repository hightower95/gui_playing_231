
"""
Folder Selection Step - Allows user to choose installation directory

This step handles:
- Displaying current/default installation path
- Allowing user to browse for different folder
- Validating the selected path
- Updating shared state with validated path
"""
import os
import ast
from pathlib import Path
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt

from .base_step import BaseStep
from ..gui_components import (
    StatusTypes, ButtonLabels, DialogTitles, LayoutConstants,
    apply_status_styling
)


class GetFolderStep(BaseStep):
    """Installation step for selecting the target installation folder"""

    def __init__(self, installation_settings, shared_state):
        super().__init__(installation_settings, shared_state)
        self.path_input = None
        self.browse_button = None
        self.feedback_label = None

        # Store default path locally, don't update shared state until validation
        self._default_path = self._get_default_installation_folder()
        self._current_path = self._default_path

    def get_title(self) -> str:
        """Get the title for this step"""
        return "Select Installation Folder"

    def get_description(self) -> str:
        """Get the description for this step"""
        return "Choose where you want to install the application"

    def get_hint_text(self) -> str:
        """Get hint text for this step"""
        if self._is_folder_selection_enabled():
            return "Instructions: Click browse button to change installation folder."
        else:
            return "Installation folder has been pre-configured and cannot be changed."

    def can_complete(self) -> bool:
        """Check if step can be completed"""
        current_path = self._current_path if hasattr(
            self, '_current_path') else ""
        return bool(current_path.strip())

    def create_widgets(self, parent_widget, layout):
        """Create UI widgets for folder selection"""
        # Path display and input
        path_label = QLabel("Installation Path:")
        layout.addWidget(path_label)

        # Path input row
        path_row = QHBoxLayout()

        self.path_input = QLineEdit()
        # Use local current path, not shared state
        self.path_input.setText(self._current_path)

        # Check if folder selection is enabled
        folder_selection_enabled = self._is_folder_selection_enabled()

        if folder_selection_enabled:
            self.path_input.textChanged.connect(self._on_path_changed)
        else:
            # Make read-only if folder selection is disabled
            self.path_input.setReadOnly(True)
            self.path_input.setStyleSheet(
                "QLineEdit { background-color: #f0f0f0; color: #666; }")
            # Connect signal to enforce path restrictions even if readonly is bypassed
            self.path_input.textChanged.connect(self._on_path_changed)

        path_row.addWidget(self.path_input)

        self.browse_button = QPushButton(ButtonLabels.BROWSE)
        self.browse_button.setFixedWidth(LayoutConstants.BUTTON_MIN_WIDTH)
        self.browse_button.clicked.connect(self._browse_for_folder)

        # Disable browse button if folder selection is disabled
        if not folder_selection_enabled:
            self.browse_button.setEnabled(False)
            self.browse_button.setToolTip(
                "Folder selection has been disabled by administrator")

        path_row.addWidget(self.browse_button)

        layout.addLayout(path_row)

        # Feedback label for validation status
        self.feedback_label = QLabel("Default installation path loaded")
        self.feedback_label.setWordWrap(True)
        self._update_feedback_status(StatusTypes.DEFAULT)
        layout.addWidget(self.feedback_label)

        # Information label (actual hint text)
        folder_selection_enabled = self._is_folder_selection_enabled()
        if folder_selection_enabled:
            info_text = "The application will be installed to this location. "
        else:
            info_text = "The application will be installed to this pre-configured location. Folder selection has been disabled."

        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        # Remove explicit styling to use system defaults
        layout.addWidget(info_label)

        # Add some spacing
        layout.addStretch()

        # Initial validation of default path
        self._path_is_valid(self.path_input.text())

    def complete_step(self) -> bool:
        """Complete the folder selection step"""
        current_path = self.path_input.text().strip() if self.path_input else ""

        if not current_path:
            QMessageBox.warning(
                None,
                DialogTitles.NO_PATH_SELECTED,
                "Please select an installation folder before proceeding."
            )
            return False

        # If folder selection is disabled, ensure path hasn't been changed from default
        if not self._is_folder_selection_enabled():
            if current_path != self._default_path:
                QMessageBox.warning(
                    None,
                    DialogTitles.FOLDER_SELECTION_DISABLED,
                    f"Folder selection is disabled. The installation path has been reverted to the default location:\n\n{self._default_path}"
                )
                # Reset to default path
                self.path_input.setText(self._default_path)
                self._current_path = self._default_path
                current_path = self._default_path

        # Validate the path
        if not self._validate_installation_path(current_path):
            return False

        # ONLY update shared state when path is validated and step completes successfully
        self.update_shared_state("valid_installation_path", current_path)
        self.mark_completed()
        return True

    def _get_default_installation_folder(self) -> str:
        """Get the default installation folder using Step_Select_Folder configuration"""
        # Try to get app name from settings
        app_name = "AlternativeApp"
        if hasattr(self.installation_settings, 'get'):
            try:
                app_name = self.installation_settings.get(
                    'Settings', 'app_name', fallback=app_name)
            except:
                pass

        # Try to get default_installation_folder from Step_Select_Folder section
        if hasattr(self.installation_settings, 'get'):
            try:
                # First try default_installation_folder
                default_str = self.installation_settings.get(
                    'Step_Select_Folder', 'default_installation_folder', fallback=None)
                if default_str:
                    default_list = ast.literal_eval(default_str)
                    for location_template in default_list:
                        expanded_location = self._expand_template_variables(
                            location_template)
                        full_path = str(Path(expanded_location) / app_name)
                        if self._is_location_accessible_and_allowed(expanded_location):
                            return full_path

                # If default doesn't work, try fallback_installation_folders
                fallback_str = self.installation_settings.get(
                    'Step_Select_Folder', 'fallback_installation_folders', fallback=None)
                if fallback_str:
                    fallback_list = ast.literal_eval(fallback_str)
                    for location_template in fallback_list:
                        expanded_location = self._expand_template_variables(
                            location_template)
                        full_path = str(Path(expanded_location) / app_name)
                        if self._is_location_accessible_and_allowed(expanded_location):
                            return full_path

            except Exception as e:
                # If parsing fails, continue to fallback
                pass

        # Final fallback to standard program files location
        if os.name == 'nt':  # Windows
            program_files = os.environ.get('PROGRAMFILES', r'C:\Program Files')
            fallback_path = str(Path(program_files) / app_name)
            if self._is_drive_allowed(fallback_path):
                return fallback_path
        else:  # Unix-like systems
            return str(Path.home() / app_name)

        # If all else fails, use current directory
        return str(Path.cwd() / app_name)

    def _expand_template_variables(self, template: str) -> str:
        """Expand template variables like {username} and {parent_folder}"""
        # Get current user's username
        username = os.getenv('USERNAME') or os.getenv('USER') or 'DefaultUser'

        # Get parent folder of current working directory
        parent_folder = str(Path.cwd().parent)

        # Replace template variables
        expanded = template.format(
            username=username,
            parent_folder=parent_folder
        )

        return expanded

    def _is_folder_selection_enabled(self) -> bool:
        """Check if folder selection is enabled in configuration"""
        if hasattr(self.installation_settings, 'getboolean'):
            try:
                return self.installation_settings.getboolean(
                    'Step_Select_Folder', 'enable_folder_selection', fallback=True)
            except Exception:
                # If parsing fails, default to enabled
                return True
        return True

    def _is_location_accessible_and_allowed(self, location: str) -> bool:
        """Check if a location is accessible for installation and on allowed drive"""
        return self._is_location_accessible(location) and self._is_drive_allowed(location)

    def _is_location_accessible(self, location: str) -> bool:
        """Check if a location is accessible for installation"""
        try:
            location_path = Path(location)

            # Check if location exists or can be created
            if not location_path.exists():
                # Try to create parent directories to test access
                try:
                    location_path.mkdir(parents=True, exist_ok=True)
                    # If successful, check if we can write to it
                    test_file = location_path / "test_write_access.tmp"
                    test_file.touch()
                    test_file.unlink()
                    return True
                except:
                    return False
            else:
                # Location exists, check write access
                return os.access(location_path, os.W_OK)

        except Exception:
            return False

    def _is_drive_allowed(self, path: str) -> bool:
        """Check if the path is on an allowed drive according to hard_drive_letter_restrictions"""
        try:
            # Get drive letter from path
            path_obj = Path(path)
            if not path_obj.is_absolute():
                return False

            # Extract drive letter (e.g., 'C' from 'C:\...')
            drive_part = path_obj.parts[0]
            if ':' in drive_part:
                drive_letter = drive_part.rstrip(':\\').upper()
            else:
                # Handle network paths or non-standard paths
                return False  # Reject non-local paths by default

            # Check if hard drive restrictions are configured
            if hasattr(self.installation_settings, 'get'):
                try:
                    lock_to_local = self.installation_settings.getboolean(
                        'Step_Select_Folder', 'lock_install_to_local_hard_drive', fallback=False)

                    if lock_to_local:
                        restrictions_str = self.installation_settings.get(
                            'Step_Select_Folder', 'hard_drive_letter_restrictions', fallback=None)

                        if restrictions_str:
                            try:
                                # Try to parse as a proper list first
                                allowed_drives = ast.literal_eval(
                                    restrictions_str)
                            except (ValueError, SyntaxError):
                                # If that fails, try manual parsing for cases like [C] instead of ["C"]
                                # Remove brackets and split by comma
                                clean_str = restrictions_str.strip('[]')
                                allowed_drives = [item.strip().strip(
                                    '"\'') for item in clean_str.split(',')]

                            # Convert to uppercase for comparison and ensure string type
                            allowed_drives = [str(drive).upper()
                                              for drive in allowed_drives]
                            return drive_letter in allowed_drives
                        else:
                            # If lock is enabled but no restrictions specified, default to C drive
                            return drive_letter == 'C'
                except Exception as e:
                    # If parsing fails, allow by default
                    print(f"Drive validation error: {e}")  # Debug output
                    return True

            # If no restrictions, allow all drives
            return True

        except Exception as e:
            # If path parsing fails, reject by default
            print(f"Path parsing error: {e}")  # Debug output
            return False

    def _get_allowed_drives_display(self) -> str:
        """Get a display string of allowed drives for error messages"""
        try:
            if hasattr(self.installation_settings, 'get'):
                restrictions_str = self.installation_settings.get(
                    'Step_Select_Folder', 'hard_drive_letter_restrictions', fallback=None)

                if restrictions_str:
                    try:
                        # Try to parse as a proper list first
                        allowed_drives = ast.literal_eval(restrictions_str)
                    except (ValueError, SyntaxError):
                        # If that fails, try manual parsing for cases like [C] instead of ["C"]
                        # Remove brackets and split by comma
                        clean_str = restrictions_str.strip('[]')
                        allowed_drives = [item.strip().strip('"\'')
                                          for item in clean_str.split(',')]

                    # Format as "C:, D:, E:"
                    return ", ".join([f"{drive}:" for drive in allowed_drives])
                else:
                    return "C:"  # Default
        except Exception:
            return "C:"  # Safe fallback

    def _on_path_changed(self, new_path):
        """Handle path input changes - update local state only"""
        # Only process changes if folder selection is enabled
        if not self._is_folder_selection_enabled():
            # If folder selection is disabled, revert any changes to default path
            if hasattr(self, '_default_path') and new_path != self._default_path:
                # Block the signal to prevent infinite recursion
                self.path_input.blockSignals(True)
                self.path_input.setText(self._default_path)
                self.path_input.blockSignals(False)
                self._current_path = self._default_path
            return

        self._current_path = new_path
        self._path_is_valid(new_path)

    def _browse_for_folder(self):
        """Open folder browser dialog"""
        # Check if folder selection is enabled
        if not self._is_folder_selection_enabled():
            QMessageBox.information(
                None,
                DialogTitles.FOLDER_SELECTION_DISABLED,
                "Folder selection has been disabled by the administrator. "
                "The installation will use the pre-configured location."
            )
            return
        """Open folder browser dialog"""
        current_path = self._default_path

        # # Start browsing from current path or default location
        # start_path = current_path if current_path and Path(
        #     current_path).exists() else str(Path.home())

        folder_path = QFileDialog.getExistingDirectory(
            None,
            DialogTitles.SELECT_FOLDER,
            current_path
        )

        if folder_path:
            self.path_input.setText(folder_path)
            self._current_path = folder_path

    def _validate_installation_path(self, path: str) -> bool:
        """Validate the selected installation path"""
        try:
            path_obj = Path(path)

            # Check if path is absolute
            if not path_obj.is_absolute():
                QMessageBox.warning(
                    None,
                    DialogTitles.INVALID_PATH,
                    "Please provide an absolute path (e.g., C:\\Program Files\\MyApp)."
                )
                return False

            # Check drive restrictions first
            if not self._is_drive_allowed(path):
                allowed_drives = self._get_allowed_drives_display()
                QMessageBox.warning(
                    None,
                    DialogTitles.INVALID_PATH,
                    f"Installation is restricted to local hard drives: {allowed_drives}\n\nPlease choose a path on an allowed drive."
                )
                return False

            # Check if parent directory exists or can be created
            parent_dir = path_obj.parent
            if not parent_dir.exists():
                try:
                    parent_dir.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    QMessageBox.warning(
                        None,
                        DialogTitles.CANNOT_CREATE_DIRECTORY,
                        f"Cannot create parent directory:\n{parent_dir}\n\nError: {str(e)}"
                    )
                    return False

            # Check if we have write permissions
            if not os.access(parent_dir, os.W_OK):
                QMessageBox.warning(
                    None,
                    DialogTitles.PERMISSION_DENIED,
                    f"You don't have write permissions to:\n{parent_dir}\n\nPlease choose a different location or run as administrator."
                )
                return False

            # Warn if target directory already exists and is not empty
            if path_obj.exists() and any(path_obj.iterdir()):
                reply = QMessageBox.question(
                    None,
                    DialogTitles.DIRECTORY_NOT_EMPTY,
                    f"The directory already exists and contains files:\n{path_obj}\n\nDo you want to continue? Existing files may be overwritten.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return False

            return True

        except Exception as e:
            QMessageBox.warning(
                None,
                DialogTitles.INVALID_PATH,
                f"The selected path is invalid:\n{str(e)}"
            )
            return False

    def _path_is_valid(self, path: str) -> bool:
        """Validate path in real-time and update feedback"""
        if not self.feedback_label:
            return False

        if not path.strip():
            self._update_feedback_status(StatusTypes.INFO, "No path selected")
            return False

        try:
            path_obj = Path(path)

            # Check if path is absolute
            if not path_obj.is_absolute():
                self._update_feedback_status(
                    StatusTypes.ERROR, "Path must be absolute (e.g., C:\\Program Files\\MyApp)")
                return False

            # Check drive restrictions
            if not self._is_drive_allowed(path):
                allowed_drives = self._get_allowed_drives_display()
                self._update_feedback_status(
                    StatusTypes.ERROR, f"Path must be on allowed drive: {allowed_drives}")
                return False

            # Check if parent directory exists or can be created
            parent_dir = path_obj.parent
            if not parent_dir.exists():
                self._update_feedback_status(
                    StatusTypes.INFO, f"Parent directory will be created: {parent_dir}")
                return True

            # Check if we have write permissions
            if not os.access(parent_dir, os.W_OK):
                self._update_feedback_status(
                    StatusTypes.ERROR, "No write permissions to parent directory")
                return False

            # Check if target directory already exists and is not empty
            if path_obj.exists() and any(path_obj.iterdir()):
                self._update_feedback_status(
                    StatusTypes.INFO, "Directory exists and contains files - will prompt before overwriting")
                return True

            # Path is valid
            self._update_feedback_status(
                StatusTypes.SUCCESS, "Installation path is valid")
            return True

        except Exception as e:
            self._update_feedback_status(
                StatusTypes.ERROR, f"Invalid path: {str(e)}")
            return False

    def _update_feedback_status(self, status_type: str, message: str = ""):
        """Update feedback label with color-coded status using GUI components"""
        if not self.feedback_label:
            return

        apply_status_styling(
            self.feedback_label,
            status_type,
            message,
            "margin-top: 5px;"
        )


# Alias for backward compatibility
FolderStep = GetFolderStep
