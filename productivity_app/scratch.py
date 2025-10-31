import os
import sys
import subprocess
import venv
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import logging
from datetime import datetime


class SetupWizard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Project Setup Wizard")
        self.geometry("800x600")
        self.resizable(False, False)

        # Setup logging
        self.setup_logging()
        self.log("Setup Wizard started")

        # State tracking
        self.install_path = tk.StringVar(value=str(Path.cwd()))
        self.pyirc_token = tk.StringVar()
        self.step_status = {
            "folder": False,
            "venv": False,
            "pyirc": False,
            "library": False,
            "files": False
        }

        # Initialize UI references
        self.finish_btn = None

        # Track if steps are being executed
        self.running_step = False

        self.build_ui()

    def setup_logging(self):
        """Setup logging to file and memory"""
        log_file = Path.cwd() / "setup_wizard.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
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
        # Main container with scrollbar
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

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

        # ---- Step 1: Select folder ----
        self.section(main_frame, "1️⃣ Select Installation Folder",
                     self.build_select_folder)

        # ---- Step 2: Create venv ----
        self.venv_section = self.section(main_frame, "2️⃣ Create Virtual Environment",
                                         self.build_create_venv)

        # ---- Step 3: Configure PyIRC ----
        self.pyirc_section = self.section(
            main_frame, "3️⃣ Configure PyIRC", self.build_pyirc)

        # ---- Step 4: Install Library ----
        self.library_section = self.section(main_frame, "4️⃣ Install my_library",
                                            self.build_install_library)

        # ---- Step 5: Check Required Files ----
        self.files_section = self.section(main_frame, "5️⃣ Verify Required Files",
                                          self.build_check_files)

        # ---- Finish button ----
        self.finish_btn = ttk.Button(
            main_frame, text="Finish 🎉", command=self.finish, state=tk.DISABLED)
        self.finish_btn.pack(pady=15)

        # Auto-detect completed steps
        self.after(100, self.auto_detect_completion)

    def section(self, parent, title, builder_fn):
        box = ttk.Labelframe(parent, text=title, padding=10)
        box.pack(fill="x", pady=5)
        builder_fn(box)
        return box

    # --- Step 1 ---
    def build_select_folder(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill="x")

        ttk.Label(frame, text="Select or confirm installation folder:").pack(
            anchor="w", pady=(0, 5))

        entry_frame = ttk.Frame(frame)
        entry_frame.pack(fill="x", pady=(0, 5))

        ttk.Entry(entry_frame, textvariable=self.install_path,
                  width=70).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(entry_frame, text="Browse...",
                   command=self.browse_folder).pack(side="left")

        self.folder_status = ttk.Label(
            frame, text="⏸ Not validated", foreground="gray")
        self.folder_status.pack(anchor="w", pady=(5, 0))

    def browse_folder(self):
        folder = filedialog.askdirectory(
            initialdir=self.install_path.get(), title="Select Installation Folder")
        if folder:
            self.install_path.set(folder)
            self.log(f"Folder selected: {folder}")
            self.update_folder_status()

    def update_folder_status(self):
        folder = Path(self.install_path.get())
        try:
            if folder.exists() and folder.is_dir():
                self.folder_status.config(
                    text="✅ Folder OK", foreground="green")
                self.step_status["folder"] = True
                self.log(f"Folder validated: {folder}")
            else:
                # Try to create the folder
                folder.mkdir(parents=True, exist_ok=True)
                self.folder_status.config(
                    text="✅ Folder created", foreground="green")
                self.step_status["folder"] = True
                self.log(f"Folder created: {folder}")
        except Exception as e:
            self.folder_status.config(
                text=f"❌ Invalid folder: {str(e)}", foreground="red")
            self.step_status["folder"] = False
            self.log(f"Folder validation failed: {e}", "error")
        self.update_progress()

    # --- Step 2 ---
    def build_create_venv(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill="x")

        self.venv_btn = ttk.Button(frame, text="Create Virtual Environment",
                                   command=self.create_venv_threaded)
        self.venv_btn.pack(anchor="w", pady=(0, 5))

        self.venv_progress = ttk.Progressbar(
            frame, length=300, mode='indeterminate')
        self.venv_progress.pack(anchor="w", pady=(0, 5))

        self.venv_status = ttk.Label(
            frame, text="⏸ Not run yet", foreground="gray")
        self.venv_status.pack(anchor="w")

    def create_venv_threaded(self):
        """Run venv creation in a separate thread to avoid blocking UI"""
        if self.running_step:
            messagebox.showwarning(
                "Busy", "Another step is running. Please wait.")
            return

        if not self.step_status["folder"]:
            messagebox.showwarning("Step 1 Required",
                                   "Please complete Step 1 (Select folder) first.")
            return

        self.running_step = True
        self.venv_btn.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.create_venv, daemon=True)
        thread.start()

    def create_venv(self):
        install_dir = Path(self.install_path.get())
        venv_dir = install_dir / ".venv"

        try:
            self.venv_status.config(text="⏳ Creating virtual environment...")
            self.venv_progress.start(10)
            self.log(f"Creating venv at {venv_dir}")

            if venv_dir.exists():
                self.log("Venv directory already exists, skipping creation")
                self.venv_status.config(
                    text="✅ Virtual environment already exists", foreground="green")
            else:
                venv.create(venv_dir, with_pip=True)
                self.log("Venv created successfully")
                self.venv_status.config(
                    text="✅ Virtual environment created", foreground="green")

            self.step_status["venv"] = True

        except Exception as e:
            self.log(f"Venv creation failed: {e}", "error")
            self.venv_status.config(text=f"❌ Failed: {e}", foreground="red")
            self.step_status["venv"] = False

        finally:
            self.venv_progress.stop()
            self.venv_btn.config(state=tk.NORMAL)
            self.running_step = False
            self.update_progress()

    # --- Step 3 ---
    def build_pyirc(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill="x")

        ttk.Label(frame, text="Paste your PyIRC token below:").pack(
            anchor="w", pady=(0, 5))

        token_frame = ttk.Frame(frame)
        token_frame.pack(fill="x", pady=(0, 5))

        ttk.Entry(token_frame, textvariable=self.pyirc_token,
                  width=60, show="*").pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(token_frame, text="Save Token",
                   command=self.validate_pyirc).pack(side="left")

        self.pyirc_status = ttk.Label(
            frame, text="⏸ Not configured", foreground="gray")
        self.pyirc_status.pack(anchor="w")

    def validate_pyirc(self):
        if not self.step_status["venv"]:
            messagebox.showwarning("Step 2 Required",
                                   "Please complete Step 2 (Create venv) first.")
            return

        token = self.pyirc_token.get().strip()
        install_dir = Path(self.install_path.get())

        try:
            if not token:
                self.pyirc_status.config(
                    text="❌ Token is empty", foreground="red")
                self.step_status["pyirc"] = False
                return

            # Save token to a config file
            config_file = install_dir / ".pyirc"
            config_file.write_text(f"token={token}\n")
            self.log(f"PyIRC token saved to {config_file}")

            self.pyirc_status.config(text="✅ Token saved", foreground="green")
            self.step_status["pyirc"] = True

        except Exception as e:
            self.log(f"PyIRC token save failed: {e}", "error")
            self.pyirc_status.config(
                text=f"❌ Save failed: {e}", foreground="red")
            self.step_status["pyirc"] = False

        finally:
            self.update_progress()

    # --- Step 4 ---
    def build_install_library(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill="x")

        self.install_btn = ttk.Button(frame, text="Install my_library",
                                      command=self.install_library_threaded)
        self.install_btn.pack(anchor="w", pady=(0, 5))

        self.install_progress = ttk.Progressbar(
            frame, length=300, mode='indeterminate')
        self.install_progress.pack(anchor="w", pady=(0, 5))

        self.install_status = ttk.Label(
            frame, text="⏸ Not installed", foreground="gray")
        self.install_status.pack(anchor="w")

    def install_library_threaded(self):
        """Run library installation in a separate thread"""
        if self.running_step:
            messagebox.showwarning(
                "Busy", "Another step is running. Please wait.")
            return

        if not self.step_status["pyirc"]:
            messagebox.showwarning("Step 3 Required",
                                   "Please complete Step 3 (Configure PyIRC) first.")
            return

        self.running_step = True
        self.install_btn.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.install_library, daemon=True)
        thread.start()

    def install_library(self):
        install_dir = Path(self.install_path.get())
        venv_python = install_dir / \
            (".venv/Scripts/python.exe" if os.name == "nt" else ".venv/bin/python")

        try:
            if not venv_python.exists():
                self.log(
                    f"Python executable not found at {venv_python}", "error")
                self.install_status.config(
                    text="❌ venv Python not found", foreground="red")
                self.step_status["library"] = False
                return

            self.install_status.config(text="⏳ Upgrading pip...")
            self.install_progress.start(10)
            self.log("Upgrading pip")

            result = subprocess.run(
                [str(venv_python), "-m", "pip", "install", "--upgrade", "pip"],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                self.log(f"Pip upgrade warning: {result.stderr}", "warning")

            self.install_status.config(text="⏳ Installing my_library...")
            self.log("Installing my_library")

            # For demo purposes, install a real package (requests)
            # Replace 'requests' with 'my_library' when you have the actual package
            result = subprocess.run(
                [str(venv_python), "-m", "pip", "install", "requests"],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                self.log("Library installed successfully")
                self.install_status.config(
                    text="✅ Library installed successfully", foreground="green")
                self.step_status["library"] = True
            else:
                self.log(
                    f"Library installation failed: {result.stderr}", "error")
                self.install_status.config(
                    text=f"❌ Install failed: {result.stderr[:50]}", foreground="red")
                self.step_status["library"] = False

        except subprocess.TimeoutExpired:
            self.log("Installation timed out", "error")
            self.install_status.config(
                text="❌ Installation timed out", foreground="red")
            self.step_status["library"] = False
        except Exception as e:
            self.log(f"Library installation error: {e}", "error")
            self.install_status.config(
                text=f"❌ Error: {str(e)[:50]}", foreground="red")
            self.step_status["library"] = False
        finally:
            self.install_progress.stop()
            self.install_btn.config(state=tk.NORMAL)
            self.running_step = False
            self.update_progress()

    # --- Step 5 ---
    def build_check_files(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill="x")

        self.check_files_btn = ttk.Button(frame, text="Check Files",
                                          command=self.check_required_files)
        self.check_files_btn.pack(anchor="w", pady=(0, 5))

        self.file_labels = {}
        for fname in ["start_program.bat", "update.bat", "config.yml"]:
            lbl = ttk.Label(frame, text=f"⏸ {fname}", foreground="gray")
            lbl.pack(anchor="w")
            self.file_labels[fname] = lbl

        # Add "Create missing files" button
        self.create_files_btn = ttk.Button(frame, text="Create Missing Files",
                                           command=self.create_missing_files, state=tk.DISABLED)
        self.create_files_btn.pack(anchor="w", pady=(5, 0))

    def check_required_files(self):
        if not self.step_status["library"]:
            messagebox.showwarning("Step 4 Required",
                                   "Please complete Step 4 (Install library) first.")
            return

        install_dir = Path(self.install_path.get())
        all_present = True
        missing_files = []

        for fname, lbl in self.file_labels.items():
            file_path = install_dir / fname
            exists = file_path.exists()
            if exists:
                lbl.config(text=f"✅ {fname}", foreground="green")
                self.log(f"File found: {fname}")
            else:
                lbl.config(text=f"❌ {fname} (missing)", foreground="red")
                self.log(f"File missing: {fname}", "warning")
                all_present = False
                missing_files.append(fname)

        self.step_status["files"] = all_present

        if not all_present:
            self.create_files_btn.config(state=tk.NORMAL)
        else:
            self.create_files_btn.config(state=tk.DISABLED)

        self.update_progress()

    def create_missing_files(self):
        """Create template files for missing required files"""
        install_dir = Path(self.install_path.get())

        templates = {
            "start_program.bat": "@echo off\ncd /d %~dp0\ncall .venv\\Scripts\\activate.bat\npython main.py\npause\n",
            "update.bat": "@echo off\ncd /d %~dp0\ncall .venv\\Scripts\\activate.bat\npip install --upgrade my_library\npause\n",
            "config.yml": "# Configuration file\napp_name: My Application\nversion: 1.0.0\n"
        }

        created = []
        for fname, lbl in self.file_labels.items():
            file_path = install_dir / fname
            if not file_path.exists():
                try:
                    file_path.write_text(templates.get(fname, f"# {fname}\n"))
                    lbl.config(text=f"✅ {fname} (created)", foreground="green")
                    created.append(fname)
                    self.log(f"Created file: {fname}")
                except Exception as e:
                    self.log(f"Failed to create {fname}: {e}", "error")

        if created:
            messagebox.showinfo("Files Created",
                                f"Created {len(created)} file(s):\n" + "\n".join(created))
            self.check_required_files()  # Re-check

    # --- Progress tracking ---
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

        # Enable finish button only if all steps complete
        if completed == total:
            self.finish_btn.config(state=tk.NORMAL)
            self.log("All steps completed!")
        else:
            self.finish_btn.config(state=tk.DISABLED)

    def auto_detect_completion(self):
        """Auto-detect if steps are already completed"""
        install_dir = Path(self.install_path.get())

        # Check if folder exists
        if install_dir.exists():
            self.update_folder_status()

        # Check if venv exists
        venv_dir = install_dir / ".venv"
        if venv_dir.exists() and (venv_dir / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")).exists():
            self.venv_status.config(
                text="✅ Virtual environment already exists", foreground="green")
            self.step_status["venv"] = True
            self.log("Auto-detected existing venv")

        # Check if PyIRC config exists
        pyirc_file = install_dir / ".pyirc"
        if pyirc_file.exists():
            self.pyirc_status.config(
                text="✅ Token already configured", foreground="green")
            self.step_status["pyirc"] = True
            self.log("Auto-detected PyIRC config")

        # Update progress
        self.update_progress()

    # --- Finish ---
    def finish(self):
        """Complete the setup and close the wizard"""
        self.log("Setup wizard completed successfully")

        summary = "Setup completed successfully!\n\n"
        summary += f"Installation folder: {self.install_path.get()}\n"
        summary += f"Log file: {Path.cwd() / 'setup_wizard.log'}\n"

        messagebox.showinfo("Setup Complete", summary)
        self.destroy()


if __name__ == "__main__":
    app = SetupWizard()
    app.mainloop()
