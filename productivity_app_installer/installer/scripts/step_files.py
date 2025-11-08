"""Step 5: Verify Required Files"""
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import configparser
from file_operations import FileOperationsManager
from constants import (
    BOOTSTRAP_CONFIG_FILE, REQUIRED_FILES, LAUNCH_CONFIG_FILE, 
    DEFAULT_APP_NAME, DEFAULT_VENV_DIR, DEFAULT_LIBRARY_NAME, DEFAULT_CONFIG
)


class FilesStep:
    def __init__(self, wizard):
        self.wizard = wizard
        self.status_label = None
        self.success_label = None
        self.required_files = REQUIRED_FILES + ["utils"]  # utils is a folder
        self.config = self._load_installation_config()
        self.auto_generate_files = self.config.get('auto_generate_files', True)

    def _load_installation_config(self):
        """Load configuration from installation_settings.ini"""
        config = configparser.ConfigParser()
        config_file = Path(__file__).parent.parent / BOOTSTRAP_CONFIG_FILE

        # Default configuration
        installation_config = DEFAULT_CONFIG.copy()

        try:
            config.read(config_file)

            # Load settings from various sections
            if config.has_section('Settings'):
                installation_config['app_name'] = config.get('Settings', 'app_name',
                                                             fallback=installation_config['app_name'])

            if config.has_section('Dependencies'):
                installation_config['library_name'] = config.get('Dependencies', 'core_libraries',
                                                                 fallback=installation_config['library_name'])

            if config.has_section('Paths'):
                installation_config['venv_dir_name'] = config.get('Paths', 'venv_dir',
                                                                  fallback=installation_config['venv_dir_name'])

            if config.has_section('DEV'):
                installation_config['auto_generate_files'] = config.getboolean('DEV', 'auto_generate_files',
                                                                               fallback=installation_config['auto_generate_files'])
                installation_config['debug'] = config.getboolean('DEV', 'debug',
                                                                 fallback=installation_config['debug'])

        except Exception as e:
            self.wizard.log(
                f"Warning: Could not load installation config: {e}")

        return installation_config

    def build_ui(self, parent):
        """Build the UI for file creation"""
        frame = ttk.Frame(parent)
        frame.pack(fill="x")

        # Status label for auto-creation
        self.status_label = ttk.Label(
            frame, text=self.get_waiting_message(), foreground="gray")
        self.status_label.pack(anchor="w", pady=(0, 5))

        # Auto-generation status info
        if not self.auto_generate_files:
            auto_info_label = ttk.Label(
                frame, text="⚙️ Auto-generation disabled - files must be created manually",
                foreground="blue", font=("", 9))
            auto_info_label.pack(anchor="w", pady=(0, 5))

        # Success message (initially hidden)
        self.success_label = ttk.Label(
            frame, text="", foreground="green", font=("", 11, "bold"))
        self.success_label.pack(anchor="w", pady=(5, 10))

        # Manual create button (only show if prerequisites are met but files not created)
        self.create_manual_btn = ttk.Button(frame, text="🔧 Create Files Manually",
                                            command=self.create_files_manually)
        # Initially hidden, will be shown when appropriate

        # Auto-create files if all prerequisites are complete
        if self.all_prerequisites_complete():
            self.auto_create_files()
        else:
            # Show manual button if not auto-creating
            self.update_manual_button_visibility()

    def all_prerequisites_complete(self):
        """Check if all prerequisite steps (1-4) are complete"""
        # Check if skip_local_index is enabled to determine if PyIRC is required
        config = configparser.ConfigParser()
        config_file = Path(__file__).parent.parent / BOOTSTRAP_CONFIG_FILE

        try:
            config.read(config_file)
            skip_local_index = config.getboolean(
                'DEV', 'skip_local_index', fallback=False)
        except Exception:
            skip_local_index = False

        if skip_local_index:
            # When skipping local index, PyIRC is not required
            required_steps = ["folder", "venv", "library"]
        else:
            # Normal operation requires PyIRC
            required_steps = ["folder", "venv", "pyirc", "library"]

        return all(self.wizard.step_status.get(step, False) for step in required_steps)

    def get_waiting_message(self):
        """Get appropriate waiting message based on which steps are incomplete"""
        # Check if skip_local_index is enabled to determine if PyIRC is required
        config = configparser.ConfigParser()
        config_file = Path(__file__).parent.parent / BOOTSTRAP_CONFIG_FILE

        try:
            config.read(config_file)
            skip_local_index = config.getboolean(
                'DEV', 'skip_local_index', fallback=False)
        except Exception:
            skip_local_index = False

        incomplete_steps = []
        step_names = {
            "folder": "Step 1 (Folder)",
            "venv": "Step 2 (Virtual Environment)",
            "library": "Step 4 (Library)"
        }

        # Only include PyIRC if not skipping local index
        if not skip_local_index:
            step_names["pyirc"] = "Step 3 (PyIRC)"

        for step, name in step_names.items():
            if not self.wizard.step_status.get(step, False):
                incomplete_steps.append(name)

        if not incomplete_steps:
            return "✅ All prerequisites complete!"
        elif len(incomplete_steps) == 1:
            return f"⏸ Waiting for {incomplete_steps[0]} to complete..."
        else:
            return f"⏸ Waiting for steps: {', '.join(incomplete_steps)}"

    def update_manual_button_visibility(self):
        """Show or hide the manual create button based on current state"""
        if hasattr(self, 'create_manual_btn'):
            if (self.all_prerequisites_complete() and
                    not self.wizard.step_status.get("files", False)):
                self.create_manual_btn.pack(anchor="w", pady=(5, 5))
            else:
                self.create_manual_btn.pack_forget()

    def create_files_manually(self):
        """Create files manually with dialog"""
        # Update status to show we're creating files
        if self.status_label:
            self.status_label.config(
                text="🔧 Creating application files...", foreground="blue")

        # Small delay to show the status update
        self.wizard.after(100, self._perform_manual_creation)

    def _perform_manual_creation(self):
        """Perform the actual manual file creation"""
        # Check which files exist before creation
        install_dir = Path(self.wizard.install_path.get())
        existing_files = []
        for fname in self.required_files:
            file_path = install_dir / fname
            if file_path.exists():
                existing_files.append(fname)

        # Create the files
        self.create_files(show_dialog=True)

        # Provide feedback based on what happened
        if existing_files and len(existing_files) == len(self.required_files):
            # All files already existed
            if self.status_label:
                self.status_label.config(
                    text="ℹ️ All files already exist!", foreground="orange")
        elif existing_files:
            # Some files existed, some were created
            created_count = len(self.required_files) - len(existing_files)
            if self.status_label:
                self.status_label.config(
                    text=f"✅ Created {created_count} files, {len(existing_files)} already existed", foreground="green")
        else:
            # All files were newly created
            if self.status_label:
                self.status_label.config(
                    text=f"✅ Created all {len(self.required_files)} files successfully!", foreground="green")

        # Check if all files now exist and mark step as complete
        self._check_completion_after_manual_creation()

        self.update_manual_button_visibility()

    def _check_completion_after_manual_creation(self):
        """Check if Step 5 is now complete after manual file creation"""
        install_dir = Path(self.wizard.install_path.get())

        # Check if required files exist
        required_paths = [
            install_dir / REQUIRED_FILES[0],  # run_app.pyw
            install_dir / REQUIRED_FILES[1],  # launch_config.ini
            install_dir / "utils"
        ]

        all_files_exist = all(path.exists() for path in required_paths)

        if all_files_exist:
            # Mark step as complete
            self.wizard.step_status["files"] = True
            self.wizard.log(
                "Step 5 completed - Manual file creation successful")

            # Show completion message
            if self.success_label:
                self.success_label.config(
                    text=f"🎉 Setup Complete! run_app.pyw now exists - close this installer and double-click run_app.pyw to start {self.config['app_name']}")

            # Update overall progress
            self.wizard.update_progress()

    def refresh_status(self):
        """Refresh the status display based on current step completion"""
        if hasattr(self, 'status_label') and self.status_label:
            if self.all_prerequisites_complete():
                # Don't auto-trigger if files are already created
                if not self.wizard.step_status.get("files", False):
                    self.auto_create_files()
            else:
                self.status_label.config(
                    text=self.get_waiting_message(), foreground="gray")

        # Update manual button visibility
        self.update_manual_button_visibility()

    def auto_create_files(self):
        """Automatically create required files"""
        if not self.all_prerequisites_complete():
            if self.status_label:
                self.status_label.config(
                    text=self.get_waiting_message(), foreground="gray")
            return

        # Check if auto-generation is enabled
        if not self.auto_generate_files:
            if self.status_label:
                self.status_label.config(
                    text="✅ Ready to create files (auto-generation disabled)", foreground="blue")
            # Show manual button since auto-generation is disabled
            self.update_manual_button_visibility()
            return

        # Update status
        if self.status_label:
            self.status_label.config(
                text="🔧 Creating application files...", foreground="blue")

        # Hide manual button since we're auto-creating
        if hasattr(self, 'create_manual_btn'):
            self.create_manual_btn.pack_forget()

        # Create files immediately
        self.wizard.after(500, self.create_files_silently)

    def create_files_silently(self):
        """Silently create files and show success message"""
        self.create_files(show_dialog=False)

    def create_files(self, show_dialog=True):
        """Create launcher files for the application using new file operations"""
        install_dir = Path(self.wizard.install_path.get())

        try:
            # Use the new file operations manager
            # Go up to productivity_app_installer
            installer_root = Path(__file__).parent.parent.parent
            file_ops = FileOperationsManager(installer_root)
            success = file_ops.setup_files_in_target_folder(
                target_folder=install_dir,
                config=self.config,
                overwrite=True
            )

            if success:
                self.wizard.log("Successfully set up all application files")

                if show_dialog:
                    messagebox.showinfo("Files Created",
                                        f"Successfully created application files!\n\n"
                                        f"Double-click run_app.pyw to start {self.config['app_name']}!")
                else:
                    # Silent mode - show success in UI
                    if self.status_label:
                        self.status_label.config(
                            text="✅ Application files created successfully!", foreground="green")
                    if self.success_label:
                        self.success_label.config(
                            text=f"🎉 Setup Complete! run_app.pyw now exists - close this installer and double-click run_app.pyw to start {self.config['app_name']}")

                    # Mark step as complete
                    self.wizard.step_status["files"] = True
                    self.wizard.update_progress()
                    self.wizard.log(
                        "Step 5 completed - All files created successfully")
            else:
                error_msg = "Failed to create application files"
                self.wizard.log(error_msg, "error")
                if show_dialog:
                    messagebox.showerror("File Creation Failed", error_msg)
                elif self.status_label:
                    self.status_label.config(
                        text="❌ File creation failed", foreground="red")

        except Exception as e:
            error_msg = f"Error creating files: {e}"
            self.wizard.log(error_msg, "error")
            if show_dialog:
                messagebox.showerror("File Creation Error", error_msg)
            elif self.status_label:
                self.status_label.config(
                    text="❌ File creation error", foreground="red")

    def auto_detect(self):
        """Auto-detect if files should be created"""
        # Check DEV section for simulation first
        config = configparser.ConfigParser()
        config_file = Path(__file__).parent.parent / BOOTSTRAP_CONFIG_FILE

        try:
            config.read(config_file)
            if config.getboolean('DEV', 'simulate_files_complete', fallback=False):
                if hasattr(self, 'status_label') and self.status_label:
                    self.status_label.config(
                        text="✅ Application files (simulated)", foreground="orange")
                if hasattr(self, 'success_label') and self.success_label:
                    self.success_label.config(
                        text=f"🎉 Setup Complete (Simulated)! run_app.pyw would exist")
                self.wizard.step_status["files"] = True
                self.wizard.log("DEV: Simulating files creation completion")
                self.wizard.update_progress()
                return
        except Exception:
            pass  # Continue with normal detection if config read fails

        if self.all_prerequisites_complete():
            if hasattr(self, 'status_label'):
                self.auto_create_files()
