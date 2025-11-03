"""
Bootstrap Wizard - Main Application
Modular setup wizard for project installation
"""
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import logging

# Import step modules
from step_folder import FolderStep
from step_venv import VenvStep
from step_token import TokenStep
from step_library import LibraryStep
from step_files import FilesStep


class SetupWizard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Project Setup Wizard")
        self.geometry("800x800")
        self.resizable(False, False)

        # Setup logging
        self.setup_logging()
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

    def build_ui(self):
        """Build the main UI"""
        # Main container
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Title
        ttk.Label(main_frame, text="Project Setup Wizard", font=(
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

        self.section(main_frame, "4️⃣ Install Library",
                     self.library_step.build_ui, "library")

        self.section(main_frame, "5️⃣ Verify Required Files",
                     self.files_step.build_ui, "files")

        # Finish button
        self.finish_btn = ttk.Button(
            main_frame, text="Finish 🎉", command=self.finish, state=tk.DISABLED)
        self.finish_btn.pack(pady=15)

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

        # Enable finish button only if all steps complete (and button exists)
        if hasattr(self, 'finish_btn'):
            if completed == total:
                self.finish_btn.config(state=tk.NORMAL)
                self.log("All steps completed!")
            else:
                self.finish_btn.config(state=tk.DISABLED)

    def update_section_styling(self):
        """Update section titles to show strikethrough for completed steps"""
        # Define original titles
        original_titles = {
            "folder": "1️⃣ Select Installation Folder",
            "venv": "2️⃣ Create Virtual Environment",
            "pyirc": "3️⃣ Configure PyIRC",
            "library": "4️⃣ Install Library",
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

        # Update progress
        self.update_progress()

    def finish(self):
        """Complete the setup and close the wizard"""
        self.log("Setup wizard completed successfully")

        log_file = Path(__file__).parent / "logs" / "setup_wizard.log"
        summary = "Setup completed successfully!\n\n"
        summary += f"Installation folder: {self.install_path.get()}\n"
        summary += f"Log file: {log_file}\n"

        messagebox.showinfo("Setup Complete", summary)
        self.destroy()


if __name__ == "__main__":
    try:
        app = SetupWizard()
        app.mainloop()
    except Exception as e:
        import traceback
        print(f"Error starting wizard: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")
