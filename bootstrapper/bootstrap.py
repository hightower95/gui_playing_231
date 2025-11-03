"""
Bootstrap Wizard - Main Application
Modular setup wizard for project installation
"""
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import logging
import configparser

# Import step modules
from step_folder import FolderStep
from step_venv import VenvStep
from step_token import TokenStep
from step_library import LibraryStep
from step_files import FilesStep


class SetupWizard(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Setup logging first
        self.setup_logging()
        
        # Load app name from config
        self.app_name = self.load_app_name()
        self.title(f"{self.app_name} - Setup Wizard")
        self.geometry("800x900")
        self.resizable(False, False)

        self.log("Setup Wizard started")

        # State tracking - default to the directory where bootstrap.py is located
        # This is more reliable than cwd() which can be unpredictable when launched from IDE
        script_dir = Path(__file__).parent.parent.resolve()
        self.log(f"Script directory: {script_dir}")
        self.install_path = tk.StringVar(value=str(script_dir))
        self.pyirc_token = tk.StringVar()
        self.step_status = {
            "folder": False,
            "venv": False,
            "pyirc": False,
            "library": False,
            "files": False
        }

        # Track section labels for strikethrough styling
        self.section_labels = {}

        # Load debug setting from config
        self.debug_mode = self.load_debug_setting()

        # Track if steps are being executed
        self.running_step = False

        # Initialize step handlers
        self.folder_step = FolderStep(self)
        self.venv_step = VenvStep(self)
        self.token_step = TokenStep(self)
        self.library_step = LibraryStep(self)
        self.files_step = FilesStep(self)

        self.build_ui()

    def setup_logging(self):
        """Setup logging to file only (no console output)"""
        # Save logs in bootstrapper/logs folder
        log_dir = Path(__file__).parent / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "setup_wizard.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file)
                # Removed StreamHandler() to prevent console window
            ]
        )
        self.logger = logging.getLogger(__name__)

    def log(self, message, level="info"):
        """Log a message"""
        if level == "info":
            self.logger.info(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "warning":
            self.logger.warning(message)

    def load_debug_setting(self):
        """Load debug setting from config.ini"""
        config = configparser.ConfigParser()
        config_file = Path(__file__).parent / "config.ini"

        try:
            config.read(config_file)
            debug_str = config.get('Settings', 'debug', fallback='false')
            debug_mode = debug_str.lower() in ('true', '1', 'yes', 'on')
            self.log(f"Debug mode: {debug_mode}")
            return debug_mode
        except Exception as e:
            self.log(f"Failed to read debug setting: {e}", "warning")
            return False

    def load_app_name(self):
        """Load app name from config.ini"""
        config = configparser.ConfigParser()
        config_file = Path(__file__).parent / "config.ini"

        try:
            config.read(config_file)
            app_name = config.get('Settings', 'app_name', fallback='My Application')
            self.log(f"App name: {app_name}")
            return app_name
        except Exception as e:
            self.log(f"Failed to read app name: {e}", "warning")
            return "My Application"

    def build_ui(self):
        """Build the main UI"""
        # Main container
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Title
        ttk.Label(main_frame, text=f"{self.app_name} - Setup Wizard", font=(
            "Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 20))

        # Progress overview
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.pack(fill="x", pady=(0, 10))
        self.progress_label = ttk.Label(
            self.progress_frame, text="Progress: 0/5 steps completed")
        self.progress_label.pack(side="left")

        # Overall progress bar
        self.overall_progress = ttk.Progressbar(
            self.progress_frame, length=200, mode='determinate')
        self.overall_progress.pack(side="right")

        # Build each step section
        self.section(main_frame, "1️⃣ Select Installation Folder",
                     self.folder_step.build_ui, "folder")

        self.section(main_frame, "2️⃣ Create Virtual Environment",
                     self.venv_step.build_ui, "venv")

        self.section(main_frame, "3️⃣ Configure PyIRC",
                     self.token_step.build_ui, "pyirc")

        # Dynamic title for Step 4 based on DEV settings
        library_title = "4️⃣ Install Library"
        if hasattr(self.library_step, 'skip_local_index') and self.library_step.skip_local_index:
            library_title += " [Local index disabled]"

        self.section(main_frame, library_title,
                     self.library_step.build_ui, "library")

        self.section(main_frame, "5️⃣ Verify Required Files",
                     self.files_step.build_ui, "files")

        # Finish buttons frame
        finish_frame = ttk.Frame(main_frame)
        finish_frame.pack(pady=15)

        self.exit_btn = ttk.Button(
            finish_frame, text="Exit", command=self.exit_app, state=tk.DISABLED)
        self.exit_btn.pack(side="left", padx=(0, 10))

        self.show_me_btn = ttk.Button(
            finish_frame, text="Show Me 📂", command=self.show_files, state=tk.DISABLED)
        self.show_me_btn.pack(side="left")

        # Auto-detect completed steps
        self.after(100, self.auto_detect_completion)

    def section(self, parent, title, builder_fn, step_key=None):
        """Create a labeled section frame"""
        box = ttk.Labelframe(parent, text=title, padding=10)
        box.pack(fill="x", pady=5)

        # Store reference to the labelframe for strikethrough styling
        if step_key:
            self.section_labels[step_key] = box

        builder_fn(box)
        return box

    def update_progress(self):
        """Update overall progress bar and enable/disable finish button"""
        completed = sum(1 for status in self.step_status.values() if status)
        total = len(self.step_status)

        # Update progress bar
        progress_percent = (completed / total) * 100
        self.overall_progress['value'] = progress_percent

        # Update progress label
        self.progress_label.config(
            text=f"Progress: {completed}/{total} steps completed")

        # Update section titles with strikethrough for completed steps
        self.update_section_styling()

        # Refresh Step 5 status when any step completes
        if hasattr(self, 'files_step') and hasattr(self.files_step, 'refresh_status'):
            self.files_step.refresh_status()

        # Enable finish buttons only if all steps complete
        if hasattr(self, 'exit_btn') and hasattr(self, 'show_me_btn'):
            if completed == total:
                self.exit_btn.config(state=tk.NORMAL)
                self.show_me_btn.config(state=tk.NORMAL)
                self.log("All steps completed!")
            else:
                self.exit_btn.config(state=tk.DISABLED)
                self.show_me_btn.config(state=tk.DISABLED)

    def update_section_styling(self):
        """Update section titles to show strikethrough for completed steps"""
        # Define original titles (dynamic for library step)
        library_title = "4️⃣ Install Library"
        if hasattr(self.library_step, 'skip_local_index') and self.library_step.skip_local_index:
            library_title += " [Local index disabled]"

        original_titles = {
            "folder": "1️⃣ Select Installation Folder",
            "venv": "2️⃣ Create Virtual Environment",
            "pyirc": "3️⃣ Configure PyIRC",
            "library": library_title,
            "files": "5️⃣ Verify Required Files"
        }

        for step_key, labelframe in self.section_labels.items():
            original_title = original_titles.get(step_key, "")
            if self.step_status.get(step_key, False):
                # Step completed - add strikethrough styling
                completed_title = f"✅ {original_title}"
                # Note: tkinter doesn't support strikethrough, so we use checkmark instead
                labelframe.config(text=completed_title)
            else:
                # Step not completed - use original title
                labelframe.config(text=original_title)

    def auto_detect_completion(self):
        """Auto-detect if steps are already completed"""
        self.folder_step.auto_detect()
        self.venv_step.auto_detect()
        self.token_step.auto_detect()
        self.library_step.auto_detect()
        self.files_step.auto_detect()

        # Update progress
        self.update_progress()

    def exit_app(self):
        """Exit the setup wizard"""
        self.log("Setup wizard exited by user")
        self.destroy()

    def show_files(self):
        """Show the installation folder with run_app.pyw highlighted"""
        import subprocess
        import os

        install_path = Path(self.install_path.get())
        run_app_path = install_path / "run_app.pyw"

        try:
            if os.name == 'nt':  # Windows
                if run_app_path.exists():
                    # Open explorer and select the file
                    subprocess.run(['explorer', '/select,', str(run_app_path)])
                else:
                    # Just open the folder
                    subprocess.run(['explorer', str(install_path)])
            else:  # macOS/Linux
                if run_app_path.exists():
                    subprocess.run(['open', '-R', str(run_app_path)])  # macOS
                else:
                    subprocess.run(['open', str(install_path)])  # macOS
        except Exception as e:
            # Fallback: show a message with the path
            messagebox.showinfo("Files Created",
                                f"Setup completed successfully!\n\n"
                                f"Installation folder: {install_path}\n"
                                f"Main app: {run_app_path}\n\n"
                                f"Double-click run_app.pyw to start the application!")

    def finish(self):
        """Complete the setup and close the wizard (legacy method for compatibility)"""
        self.exit_app()


if __name__ == "__main__":
    try:
        app = SetupWizard()
        app.mainloop()
    except Exception as e:
        import traceback
        print(f"Error starting wizard: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")
