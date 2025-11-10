
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
    StatusTypes, ButtonLabels, DialogTitles_step_folder, LayoutConstants,
    apply_status_styling
)


class GetFolderStep(BaseStep):
    """Installation step for selecting the target installation folder"""

    def __init__(self, installation_settings, shared_state):
        super().__init__(installation_settings, shared_state)
        self.path_input = None
        self.browse_button = None
        self.feedback_label = None

        # Set default installation path
        default_path = self._get_default_installation_folder()
        self.update_shared_state("installation_path", default_path)

    def get_title(self) -> str:
        """Get the title for this step"""
        return "Select Installation Folder"

    def get_description(self) -> str:
        """Get the description for this step"""
        return "Choose where you want to install the application"

    def get_hint_text(self) -> str:
        """Get hint text for this step"""
        return "Instructions: Click browse button to change installation folder."

    def can_complete(self) -> bool:
        """Check if step can be completed"""
        current_path = self.get_shared_state("installation_path", "")
        return bool(current_path.strip())

    def create_widgets(self, parent_widget, layout):
        """Create UI widgets for folder selection"""
        # Path display and input
        path_label = QLabel("Installation Path:")
        layout.addWidget(path_label)

        # Path input row
        path_row = QHBoxLayout()

        self.path_input = QLineEdit()
        current_path = self.get_shared_state("installation_path", "")
        self.path_input.setText(current_path)
        self.path_input.textChanged.connect(self._on_path_changed)
        path_row.addWidget(self.path_input)

        self.browse_button = QPushButton(ButtonLabels.BROWSE)
        self.browse_button.setFixedWidth(LayoutConstants.BUTTON_MIN_WIDTH)
        self.browse_button.clicked.connect(self._browse_for_folder)
        path_row.addWidget(self.browse_button)

        layout.addLayout(path_row)

        # Feedback label for validation status
        self.feedback_label = QLabel("Default installation path loaded")
        self.feedback_label.setWordWrap(True)
        self._update_feedback_status(StatusTypes.DEFAULT)
        layout.addWidget(self.feedback_label)

        # Information label (actual hint text)
        info_label = QLabel(
            "The application will be installed to this location. "
        )
        info_label.setWordWrap(True)
        # Remove explicit styling to use system defaults
        layout.addWidget(info_label)

        # Add some spacing
        layout.addStretch()

        # Initial validation of default path
        self._validate_path_real_time(self.path_input.text())

    def complete_step(self) -> bool:
        """Complete the folder selection step"""
        current_path = self.path_input.text().strip() if self.path_input else ""

        if not current_path:
            QMessageBox.warning(
                None,
                DialogTitles_step_folder.NO_PATH_SELECTED,
                "Please select an installation folder before proceeding."
            )
            return False

        # Validate the path
        if not self._validate_installation_path(current_path):
            return False

        # Update shared state and mark as completed
        self.update_shared_state("installation_path", current_path)
        self.mark_completed()
        return True

    def _get_default_installation_folder(self) -> str:
        """Get the default installation folder using install_locations_preferences"""
        # Try to get app name from settings
        app_name = "AlternativeApp"
        if hasattr(self.installation_settings, 'get'):
            try:
                app_name = self.installation_settings.get(
                    'Settings', 'app_name', fallback=app_name)
            except:
                pass

        # Try to get install_locations_preferences from config
        if hasattr(self.installation_settings, 'get'):
            try:
                preferences_str = self.installation_settings.get(
                    'Settings', 'install_locations_preferences', fallback=None)
                if preferences_str:
                    # Parse the list string and find first valid location
                    preferences_list = ast.literal_eval(preferences_str)
                    for location_template in preferences_list:
                        expanded_location = self._expand_template_variables(
                            location_template)
                        # Create full path with app name
                        full_path = str(Path(expanded_location) / app_name)
                        # Check if this location is valid/accessible
                        if self._is_location_accessible(expanded_location):
                            return full_path
            except Exception as e:
                # If parsing fails, continue to fallback
                pass

        # Fallback to standard program files location
        if os.name == 'nt':  # Windows
            program_files = os.environ.get('PROGRAMFILES', r'C:\Program Files')
            return str(Path(program_files) / app_name)
        else:  # Unix-like systems
            return str(Path.home() / app_name)

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

    def _on_path_changed(self, new_path):
        """Handle path input changes"""
        self.update_shared_state("installation_path", new_path)
        self._validate_path_real_time(new_path)

    def _browse_for_folder(self):
        """Open folder browser dialog"""
        current_path = self.path_input.text() if self.path_input else ""

        # Start browsing from current path or default location
        start_path = current_path if current_path and Path(
            current_path).exists() else str(Path.home())

        folder_path = QFileDialog.getExistingDirectory(
            None,
            DialogTitles_step_folder.SELECT_FOLDER,
            start_path
        )

        if folder_path:
            self.path_input.setText(folder_path)
            self.update_shared_state("installation_path", folder_path)
            self._validate_path_real_time(folder_path)

    def _validate_installation_path(self, path: str) -> bool:
        """Validate the selected installation path"""
        try:
            path_obj = Path(path)

            # Check if path is absolute
            if not path_obj.is_absolute():
                QMessageBox.warning(
                    None,
                    DialogTitles_step_folder.INVALID_PATH,
                    "Please provide an absolute path (e.g., C:\\Program Files\\MyApp)."
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
                        DialogTitles_step_folder.CANNOT_CREATE_DIRECTORY,
                        f"Cannot create parent directory:\n{parent_dir}\n\nError: {str(e)}"
                    )
                    return False

            # Check if we have write permissions
            if not os.access(parent_dir, os.W_OK):
                QMessageBox.warning(
                    None,
                    DialogTitles_step_folder.PERMISSION_DENIED,
                    f"You don't have write permissions to:\n{parent_dir}\n\nPlease choose a different location or run as administrator."
                )
                return False

            # Warn if target directory already exists and is not empty
            if path_obj.exists() and any(path_obj.iterdir()):
                reply = QMessageBox.question(
                    None,
                    DialogTitles_step_folder.DIRECTORY_NOT_EMPTY,
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
                DialogTitles_step_folder.INVALID_PATH,
                f"The selected path is invalid:\n{str(e)}"
            )
            return False

    def _validate_path_real_time(self, path: str):
        """Validate path in real-time and update feedback"""
        if not self.feedback_label:
            return

        if not path.strip():
            self._update_feedback_status(StatusTypes.INFO, "No path selected")
            return

        try:
            path_obj = Path(path)

            # Check if path is absolute
            if not path_obj.is_absolute():
                self._update_feedback_status(
                    StatusTypes.ERROR, "Path must be absolute (e.g., C:\\Program Files\\MyApp)")
                return

            # Check if parent directory exists or can be created
            parent_dir = path_obj.parent
            if not parent_dir.exists():
                self._update_feedback_status(
                    StatusTypes.INFO, f"Parent directory will be created: {parent_dir}")
                return

            # Check if we have write permissions
            if not os.access(parent_dir, os.W_OK):
                self._update_feedback_status(
                    StatusTypes.ERROR, "No write permissions to parent directory")
                return

            # Check if target directory already exists and is not empty
            if path_obj.exists() and any(path_obj.iterdir()):
                self._update_feedback_status(
                    StatusTypes.INFO, "Directory exists and contains files - will prompt before overwriting")
                return

            # Path is valid
            self._update_feedback_status(
                StatusTypes.SUCCESS, "Installation path is valid")

        except Exception as e:
            self._update_feedback_status(
                StatusTypes.ERROR, f"Invalid path: {str(e)}")

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
