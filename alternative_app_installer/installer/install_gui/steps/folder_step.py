"""
Folder Selection Step - Allows user to choose installation directory using native tkinter

This step handles:
- Displaying current/default installation path
- Allowing user to browse for different folder
- Validating the selected path
- Updating shared state with validated path
- Uses only native Python libraries (tkinter)
"""
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging

from .base_step import BaseStep


class GetFolderStep(BaseStep):
    """Installation step for selecting the target installation folder using tkinter"""

    def __init__(self, installation_settings, shared_state):
        super().__init__(installation_settings, shared_state)

        # UI components
        self.path_display = None
        self.path_entry = None
        self.status_label = None
        self.browse_button = None

        # State
        self._current_path = ""
        self._default_path = self._get_default_installation_path()
        self._is_path_valid = False

    # ========================================================================
    # Required BaseStep Methods
    # ========================================================================

    def get_title(self) -> str:
        return "Choose Installation Folder"

    def get_description(self) -> str:
        return "Select where the application should be installed"

    def get_hint_text(self) -> str:
        return "Choose a folder for the application installation"

    def can_complete(self) -> bool:
        """Check if step can be completed"""
        return self._is_path_valid and bool(self._current_path.strip())

    def create_widgets(self, parent_frame: tk.Frame):
        """Create UI widgets for folder selection using tkinter"""
        # Path display section
        path_frame = ttk.LabelFrame(
            parent_frame, text="Installation Path", padding=10)
        path_frame.pack(fill="x", pady=(0, 15))

        # Current path entry
        self.path_entry = ttk.Entry(path_frame, font=("Arial", 9))
        self.path_entry.pack(fill="x", pady=(0, 10))
        self.path_entry.bind('<KeyRelease>', self._on_path_changed)
        self.path_entry.bind('<FocusOut>', self._on_path_changed)

        # Browse button
        button_frame = ttk.Frame(path_frame)
        button_frame.pack(fill="x")

        self.browse_button = ttk.Button(button_frame, text="Browse...",
                                        command=self._browse_for_folder)
        self.browse_button.pack(side="left")

        # Status label
        self.status_label = ttk.Label(path_frame, text="")
        self.status_label.pack(pady=(10, 0))

        # Load initial path
        self._load_initial_path()

        # Debug output
        print(
            f"DEBUG: Folder step initialized with path: {self._current_path}")
        print(f"DEBUG: Path valid: {self._is_path_valid}")
        print(f"DEBUG: Can complete: {self.can_complete()}")

        # Always notify completion state after initial setup
        self.notify_completion_state_changed()

    def complete_step(self) -> bool:
        """Complete the folder selection step"""
        logging.info(
            f"Folder step: Attempting to complete with path: {self._current_path}")

        if not self.can_complete():
            logging.warning(
                f"Folder step: Cannot complete - invalid path: {self._current_path}")
            messagebox.showwarning(
                "Invalid Path",
                "Please select a valid installation folder before proceeding."
            )
            return False

        # Update shared state with validated path
        logging.info(
            f"Folder step: Validation successful, setting installation path: {self._current_path}")
        self.update_shared_state("valid_installation_path", self._current_path)
        self.mark_completed()
        return True

    def cleanup_widgets(self):
        """Clean up when step becomes inactive"""
        # Nothing specific to clean up for this step
        pass

    # ========================================================================
    # Path Management Methods
    # ========================================================================

    def _load_initial_path(self):
        """Load the initial installation path"""
        # Try to get from shared state first
        existing_path = self.get_shared_state("valid_installation_path", "")

        if existing_path:
            self._current_path = existing_path
        else:
            # Get default from config
            self._current_path = self._get_default_installation_path()

        # Update UI and validate
        if self.path_entry:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, self._current_path)

        self._validate_current_path()

    def _get_default_installation_path(self) -> str:
        """Get the default installation path from configuration"""
        try:
            # Get default folder config value (template substitution already done)
            default_folder_path = self.installation_settings.get(
                'Step_Select_Folder', 'default_installation_folder',
                fallback=str(Path.home())
            )
            logging.debug(
                f"Folder step: Retrieved default installation path from config: {default_folder_path}")

            # The path should already be substituted by run_installer.pyw
            return default_folder_path

        except Exception:
            fallback_path = str(Path.home())
            logging.warning(
                f"Folder step: Using fallback path due to config error: {fallback_path}")
            return fallback_path

    def _browse_for_folder(self):
        """Open folder browser dialog"""
        initial_dir = self._default_path  # must be default path else user gets a confusing / irritating experience

        logging.info(
            f"Folder step: Opening folder browser dialog with initial directory: {initial_dir}")

        # Use tkinter's native folder dialog
        selected_path = filedialog.askdirectory(
            title="Select Installation Folder",
            initialdir=initial_dir
        )

        if selected_path:
            logging.info(
                f"Folder step: User selected path via browser: {selected_path}")
            self._current_path = selected_path
            if self.path_entry:
                self.path_entry.delete(0, tk.END)
                self.path_entry.insert(0, selected_path)
            self._validate_current_path()
        else:
            logging.debug("Folder step: User cancelled folder browser dialog")

    def _on_path_changed(self, event=None):
        """Handle manual path entry changes"""
        if self.path_entry:
            old_path = self._current_path
            self._current_path = self.path_entry.get().strip()
            if old_path != self._current_path:
                logging.debug(
                    f"Folder step: Path manually changed from '{old_path}' to '{self._current_path}'")
            self._validate_current_path()

    # ========================================================================
    # Validation Methods
    # ========================================================================

    def _validate_current_path(self):
        """Validate the current path and update UI"""
        old_can_complete = self.can_complete()

        if not self._current_path:
            self._is_path_valid = False
            self._update_status("No path selected", "error")
        else:
            path_obj = Path(self._current_path)

            # Check if path is writable
            if not self._is_path_writable(path_obj):
                self._is_path_valid = False
                self._update_status("Path is not writable", "error")
            # Check if path is not a system directory
            elif self._is_system_directory(path_obj):
                self._is_path_valid = False
                self._update_status(
                    "Cannot install in system directory", "error")
            else:
                # Path is valid
                self._is_path_valid = True
                self._update_status("Path is valid", "success")

        # Notify if completion state changed
        new_can_complete = self.can_complete()
        if old_can_complete != new_can_complete:
            self.notify_completion_state_changed()

    def _is_path_writable(self, path: Path) -> bool:
        """Check if path is writable"""
        try:
            logging.debug(f"Folder step: Checking if path is writable: {path}")
            # If path doesn't exist, check if parent is writable
            if not path.exists():
                # Find the first existing parent
                test_path = path
                while not test_path.exists() and test_path.parent != test_path:
                    test_path = test_path.parent
                logging.debug(
                    f"Folder step: Testing parent path for writability: {test_path}")

                if test_path.exists():
                    writable = os.access(str(test_path), os.W_OK)
                    logging.debug(
                        f"Folder step: Parent path writable: {writable}")
                    return writable
                else:
                    logging.debug(
                        "Folder step: No existing parent found, path not writable")
                    return False

            # Path exists, check if it's writable
            writable = os.access(str(path), os.W_OK)
            logging.debug(f"Folder step: Existing path writable: {writable}")
            return writable
        except Exception as e:
            logging.error(f"Folder step: Error checking path writability: {e}")
            return False

    def _is_system_directory(self, path: Path) -> bool:
        """Check if path is a system directory that should be avoided"""
        try:
            path_str = str(path).lower()
            logging.debug(
                f"Folder step: Checking if path is system directory: {path_str}")

            # Common system directories to avoid
            system_dirs = [
                'c:\\windows',
                'c:\\program files',
                'c:\\program files (x86)',
                'c:\\system32',
                'c:\\users\\public',
                '/usr',
                '/bin',
                '/sbin',
                '/etc',
                '/var',
                '/sys',
                '/proc'
            ]

            for sys_dir in system_dirs:
                if path_str.startswith(sys_dir):
                    logging.debug(
                        f"Folder step: Path is system directory (matches {sys_dir})")
                    return True

            logging.debug("Folder step: Path is not a system directory")
            return False
        except Exception as e:
            logging.error(f"Folder step: Error checking system directory: {e}")
            return False

    # ========================================================================
    # UI Update Methods
    # ========================================================================

    def _update_status(self, message: str, status_type: str):
        """Update the status label with appropriate styling"""
        if not self.status_label:
            return

        self.status_label.config(text=message)

        # Apply basic color styling
        if status_type == "success":
            self.status_label.config(foreground="green")
        elif status_type == "error":
            self.status_label.config(foreground="red")
        elif status_type == "warning":
            self.status_label.config(foreground="orange")
        else:
            self.status_label.config(foreground="black")

    # ========================================================================
    # Testing and Development Methods
    # ========================================================================

    def simulate_folder_selection(self, folder_path: str) -> bool:
        """Simulate folder selection for testing purposes"""
        self._current_path = folder_path
        if self.path_entry:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder_path)

        self._validate_current_path()
        return self._is_path_valid


# Alias for backward compatibility
FolderStep = GetFolderStep
