"""
Generate Files Step - Generate deployment files from templates and shared state

This step handles:
- Reading shared state from previous steps
- Loading and processing templates 
- Generating run_app.pyw with configuration
- Generating update_app.pyw with version management
- Generating launch_config.ini from shared state
- Copying utils directory for runtime support
- Uses only native Python libraries (tkinter)
"""
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from configparser import ConfigParser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging

from .base_step import BaseStep


class GenerateFilesStep(BaseStep):
    def __init__(self, installation_settings: ConfigParser, shared_state: Dict[str, Any]):
        super().__init__(installation_settings, shared_state)

        # State variables
        self._generation_in_progress = False
        self._files_generated = False

        # UI components will be initialized in create_widgets
        self.folder_label = None
        self.generate_button = None
        self.open_folder_button = None
        self._checklist_labels = {}

    @property
    def _target_folder(self) -> Path:
        """Get target folder from shared state"""
        folder_path = self.get_shared_state("valid_installation_path", "")
        if not folder_path:
            return None
        return Path(folder_path)

    # ========================================================================
    # Required BaseStep Methods
    # ========================================================================

    def get_title(self) -> str:
        return "Generate Files"

    def get_description(self) -> str:
        return "Generate deployment files from templates and configuration"

    def get_hint_text(self) -> str:
        return "Generate run_app.pyw, update_app.pyw, and launch_config.ini"

    def can_complete(self) -> bool:
        """Check if step can be completed"""
        return self._files_generated

    def create_widgets(self, parent_frame: tk.Frame):
        """Create UI widgets for file generation"""

        # Display target folder info (read-only)
        folder_frame = ttk.LabelFrame(
            parent_frame, text="Target Folder", padding=10)
        folder_frame.pack(fill="x", pady=(0, 15))

        installation_folder = self.get_shared_state(
            "valid_installation_path", "")
        if installation_folder:
            folder_text = f"Files will be generated in: {installation_folder}"
            folder_color = "black"
        else:
            folder_text = "⚠️ No installation folder set - check previous steps"
            folder_color = "red"

        self.folder_label = ttk.Label(folder_frame, text=folder_text,
                                      font=("Arial", 9), foreground=folder_color)
        self.folder_label.pack(anchor="w")

        # Generation checklist
        self._create_checklist(parent_frame)

        # Generate button
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(fill="x", pady=(0, 10))

        self.generate_button = ttk.Button(button_frame, text="Generate Files",
                                          command=self._start_file_generation)
        self.generate_button.pack(side="left")

        # Open folder button - initially disabled until files are generated
        self.open_folder_button = ttk.Button(button_frame, text="Open Folder",
                                             command=self._open_target_folder)
        self.open_folder_button.pack(side="left", padx=(10, 0))

        # Initial state
        self._update_ui_state()

    def complete_step(self) -> bool:
        """Complete the file generation step"""
        if not self.can_complete():
            messagebox.showwarning(
                "Generation Not Complete",
                "Please generate deployment files before proceeding."
            )
            return False

        # Update shared state
        self.update_shared_state("files_generated", True)

        self.mark_completed()
        return True

    def cleanup_widgets(self):
        """Clean up when step becomes inactive"""
        pass

    # ========================================================================
    # UI Methods
    # ========================================================================

    def _create_checklist(self, parent_frame: tk.Frame):
        """Create the generation checklist"""
        checklist_frame = ttk.LabelFrame(
            parent_frame, text="Generation Progress", padding=10)
        checklist_frame.pack(fill="x", pady=(0, 15))

        checklist_items = [
            ("run_app", "1. run_app.pyw"),
            ("update_app", "2. update_app.pyw"),
            ("launch_config", "3. launch_config.ini"),
            ("utilities", "4. utilities/")
        ]

        for key, text in checklist_items:
            frame = ttk.Frame(checklist_frame)
            frame.pack(fill="x", pady=2)

            label = ttk.Label(frame, text=text, font=("Arial", 9))
            label.pack(side="left")

            status_label = ttk.Label(
                frame, text="⏳ Pending", font=("Arial", 9))
            status_label.pack(side="right")

            self._checklist_labels[key] = status_label

    def _update_checklist_item(self, key: str, text: str, color: str = "black"):
        """Update a checklist item"""
        if key in self._checklist_labels:
            self._checklist_labels[key].config(text=text, foreground=color)

    def _update_ui_state(self):
        """Update UI elements based on current state"""
        can_generate = self._target_folder is not None and not self._generation_in_progress

        if self.generate_button:
            self.generate_button.config(
                state="normal" if can_generate else "disabled")

        # Open folder button should be enabled when files are generated and target folder exists
        can_open_folder = (self._target_folder is not None and
                           self._files_generated and
                           (self._target_folder / "run_app.pyw").exists())

        if self.open_folder_button:
            self.open_folder_button.config(
                state="normal" if can_open_folder else "disabled")

    def _open_target_folder(self):
        """Open the target folder with run_app.pyw selected"""
        logging.info("Generate files step: User clicked 'Open Folder' button")

        if not self._target_folder or not self._files_generated:
            logging.warning(
                "Generate files step: Cannot open folder - files not generated yet")
            messagebox.showwarning(
                "No Files Generated",
                "Please generate files first before opening the folder."
            )
            return

        run_app_path = self._target_folder / "run_app.pyw"
        if not run_app_path.exists():
            logging.error(
                f"Generate files step: run_app.pyw not found at expected path: {run_app_path}")
            messagebox.showerror(
                "File Not Found",
                f"run_app.pyw not found in {self._target_folder}"
            )
            return

        logging.info(
            f"Generate files step: Opening file explorer with selected file: {run_app_path}")

        try:
            # Use Windows explorer with /select parameter to highlight the file
            import subprocess
            result = subprocess.run(
                ['explorer', '/select,', str(run_app_path)],
                capture_output=True, text=True)

            # Explorer often returns non-zero exit codes even when successful
            # So we don't check the return code for the /select command

        except Exception as e:
            # Fallback: just open the folder
            try:
                import subprocess
                subprocess.run(['explorer', str(self._target_folder)])
            except Exception as e2:
                messagebox.showerror(
                    "Unable to Open Folder",
                    f"Failed to open folder: {e}\nFallback also failed: {e2}"
                )

    # ========================================================================
    # File Generation Methods
    # ========================================================================

    def _start_file_generation(self):
        """Start the file generation process"""
        if self._generation_in_progress:
            return

        if not self._target_folder:
            logging.error("Generate files step: No target folder available")
            messagebox.showerror("No Installation Folder",
                                 "Installation folder not found. Please complete the folder selection step first.")
            return

        logging.info(
            f"Generate files step: Starting file generation in: {self._target_folder}")

        try:
            self._generation_in_progress = True
            self._update_ui_state()

            # Generate each file
            logging.info("Generate files step: Generating run_app.pyw")
            self._generate_run_app()

            logging.info("Generate files step: Generating update_app.pyw")
            self._generate_update_app()

            logging.info("Generate files step: Generating launch_config.ini")
            self._generate_launch_config()

            logging.info("Generate files step: Copying utilities directory")
            self._copy_utilities()

            # Mark as completed
            self._files_generated = True
            self.notify_completion_state_changed()
            self._update_ui_state()  # Update button states

            logging.info(
                "Generate files step: File generation completed successfully")
            messagebox.showinfo("Generation Complete",
                                f"Files generated successfully in:\\n{self._target_folder}")

        except Exception as e:
            logging.error(f"Generate files step: File generation failed: {e}")
            messagebox.showerror("Generation Error",
                                 f"Failed to generate files: {e}")
            # Reset checklist on error
            for key in self._checklist_labels:
                self._update_checklist_item(key, "❌ Failed", "red")
        finally:
            self._generation_in_progress = False
            self._update_ui_state()  # Update button states
            self._update_ui_state()

    def _generate_run_app(self):
        """Generate run_app.pyw from template"""
        self._update_checklist_item("run_app", "⏳ Generating...", "blue")

        template_path = self._get_template_path("run_app.pyw")
        target_path = self._target_folder / "run_app.pyw"

        # Read template
        with template_path.open('r', encoding='utf-8') as f:
            content = f.read()

        # Perform template substitution
        substitutions = self._get_launch_config_substitutions()
        for placeholder, value in substitutions.items():
            content = content.replace(f"{{{{{placeholder}}}}}", str(value))

        # Write to target
        with target_path.open('w', encoding='utf-8') as f:
            f.write(content)

        self._update_checklist_item("run_app", "✅ Generated", "#28a745")

    def _generate_update_app(self):
        """Generate update_app.pyw from template"""
        self._update_checklist_item("update_app", "⏳ Generating...", "blue")

        template_path = self._get_template_path("update_app.pyw")
        target_path = self._target_folder / "update_app.pyw"

        # Read template
        with template_path.open('r', encoding='utf-8') as f:
            content = f.read()

        # Perform template substitution
        substitutions = self._get_launch_config_substitutions()
        for placeholder, value in substitutions.items():
            content = content.replace(f"{{{{{placeholder}}}}}", str(value))

        # Write to target
        with target_path.open('w', encoding='utf-8') as f:
            f.write(content)

        self._update_checklist_item("update_app", "✅ Generated", "#28a745")

    def _generate_launch_config(self):
        """Generate launch_config.ini from template and shared state"""
        self._update_checklist_item("launch_config", "⏳ Generating...", "blue")

        template_path = self._get_template_path("launch_config.ini")
        target_path = self._target_folder / "launch_config.ini"

        # Read template
        with template_path.open('r', encoding='utf-8') as f:
            content = f.read()

        # Get substitution values from shared state
        substitutions = self._get_launch_config_substitutions()

        # Perform template substitution
        for placeholder, value in substitutions.items():
            content = content.replace(f"{{{{{placeholder}}}}}", str(value))

        # Write to target
        with target_path.open('w', encoding='utf-8') as f:
            f.write(content)

        self._update_checklist_item("launch_config", "✅ Generated", "#28a745")

    def _copy_utilities(self):
        """Copy utilities directory to target location"""
        self._update_checklist_item("utilities", "⏳ Copying...", "blue")

        # Find utilities directory in install_gui
        installer_dir = Path(__file__).resolve().parents[2]  # installer dir
        source_utilities = installer_dir / "install_gui" / "utilities"
        target_utilities = self._target_folder / "utilities"

        if not source_utilities.exists():
            raise FileNotFoundError(
                f"Utilities directory not found: {source_utilities}")

        # Remove existing utilities if present
        if target_utilities.exists():
            shutil.rmtree(target_utilities)

        # Copy utilities directory
        shutil.copytree(source_utilities, target_utilities)

        self._update_checklist_item("utilities", "✅ Copied", "#28a745")

    def _get_template_path(self, template_name: str) -> Path:
        """Get path to a template file"""
        # Templates are in installer/templates directory
        installer_dir = Path(__file__).resolve().parents[2]  # installer dir
        template_path = installer_dir / "templates" / template_name

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        return template_path

    def _get_launch_config_substitutions(self) -> Dict[str, str]:
        """Get template substitution values from shared state"""

        # Get values from shared state with defaults
        venv_path = self.get_shared_state("venv_path", "")
        installed_folder = self.get_shared_state("valid_installation_path", "")
        core_library = self.get_shared_state(
            "core_library", "productivity_app")

        # Get upgrade settings from config
        always_upgrade = self.installation_settings.getboolean(
            'Step_Install_Libraries', 'always_upgrade', fallback=True)
        allow_test_releases = self.installation_settings.getboolean(
            'Step_Install_Libraries', 'allow_upgrade_to_test_releases', fallback=False)

        # Get auto-upgrade settings
        auto_upgrade_major = self.installation_settings.getboolean(
            'DEFAULT', 'auto_upgrade_major_version', fallback=False)
        auto_upgrade_minor = self.installation_settings.getboolean(
            'DEFAULT', 'auto_upgrade_minor_version', fallback=True)
        auto_upgrade_patches = self.installation_settings.getboolean(
            'DEFAULT', 'auto_upgrade_patches', fallback=True)

        # Get logging settings
        enable_log = self.installation_settings.getboolean(
            'DEFAULT', 'enable_log', fallback=False)
        log_level = self.installation_settings.get(
            'DEFAULT', 'log_level', fallback='INFO')

        return {
            'VENV_PATH': venv_path,
            'LIBRARY_NAME': core_library,
            'ALWAYS_UPGRADE': str(always_upgrade).lower(),
            'ALLOW_UPGRADE_TO_TEST_RELEASES': str(allow_test_releases).lower(),
            'AUTO_UPGRADE_MAJOR_VERSION': str(auto_upgrade_major).lower(),
            'AUTO_UPGRADE_MINOR_VERSION': str(auto_upgrade_minor).lower(),
            'AUTO_UPGRADE_PATCHES': str(auto_upgrade_patches).lower(),
            'ENABLE_LOG': str(enable_log).lower(),
            'LOG_LEVEL': log_level,
            'INSTALLED_FOLDER': installed_folder,
            'INSTALLER_VERSION': '1.0.0',  # Could be dynamic
            'INSTALLATION_DATE': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


# Alias for backward compatibility
GenerateFiles = GenerateFilesStep
