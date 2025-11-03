"""Step 2: Create Virtual Environment"""
import os
import sys
import venv
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import configparser


class VenvStep:
    def __init__(self, wizard):
        self.wizard = wizard
        self.venv_btn = None
        self.venv_status = None
        self.venv_dir_name = self.load_venv_dir_name()

    def load_venv_dir_name(self):
        """Load venv directory name from config.ini"""
        config = configparser.ConfigParser()
        config_file = Path(__file__).parent / "config.ini"

        try:
            config.read(config_file)
            return config.get('Paths', 'venv_dir', fallback='.venv')
        except Exception:
            return '.venv'

    def build_ui(self, parent):
        """Build the UI for venv creation"""
        frame = ttk.Frame(parent)
        frame.pack(fill="x")

        self.venv_btn = ttk.Button(frame, text="Create Virtual Environment",
                                   command=self.run_threaded)
        self.venv_btn.pack(anchor="w", pady=(0, 5))

        self.venv_status = ttk.Label(
            frame, text="⏸ Not run yet", foreground="gray")
        self.venv_status.pack(anchor="w")

    def run_threaded(self):
        """Run venv creation in a separate thread"""
        if self.wizard.running_step:
            messagebox.showwarning(
                "Busy", "Another step is running. Please wait.")
            return

        if not self.wizard.step_status["folder"]:
            messagebox.showwarning("Step 1 Required",
                                   "Please complete Step 1 (Select folder) first.")
            return

        self.wizard.running_step = True
        self.venv_btn.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.execute, daemon=True)
        thread.start()

    def execute(self):
        """Create the virtual environment"""
        install_dir = Path(self.wizard.install_path.get())
        venv_dir = install_dir / self.venv_dir_name

        try:
            self.venv_status.config(text="⏳ Creating virtual environment...")
            self.wizard.log(f"Creating venv at {venv_dir}")
            self.wizard.log(f"Python executable: {sys.executable}")
            self.wizard.log(f"Target directory: {install_dir}")

            if venv_dir.exists():
                self.wizard.log(
                    "Venv directory already exists, checking validity...")
                python_exe = venv_dir / ("Scripts" if os.name == "nt" else "bin") / \
                    ("python.exe" if os.name == "nt" else "python")

                if python_exe.exists():
                    self.wizard.log(
                        f"Valid Python executable found at: {python_exe}")
                    self.wizard.log(
                        "Venv directory already exists and is valid, skipping creation")
                    self.venv_status.config(
                        text=f"✅ Virtual environment already exists at {venv_dir}", foreground="green")
                else:
                    self.wizard.log(
                        "Venv directory exists but no valid Python executable found, recreating...")
                    import shutil
                    shutil.rmtree(venv_dir)
                    self.wizard.log("Removed invalid venv directory")
                    self.wizard.log("Creating new virtual environment...")
                    venv.create(venv_dir, with_pip=True)
                    self.wizard.log(
                        f"Venv created successfully at: {venv_dir}")
                    self.venv_status.config(
                        text=f"✅ Virtual environment created at {venv_dir}", foreground="green")
            else:
                self.wizard.log("Creating new virtual environment...")
                venv.create(venv_dir, with_pip=True)
                self.wizard.log(f"Venv created successfully at: {venv_dir}")

                # Verify creation
                python_exe = venv_dir / ("Scripts" if os.name == "nt" else "bin") / \
                    ("python.exe" if os.name == "nt" else "python")
                if python_exe.exists():
                    self.wizard.log(
                        f"Verified Python executable at: {python_exe}")
                else:
                    self.wizard.log(
                        f"Warning: Python executable not found at expected location: {python_exe}", "warning")

                self.venv_status.config(
                    text=f"✅ Virtual environment created at {venv_dir}", foreground="green")

            self.wizard.step_status["venv"] = True
            self.wizard.log("Step 2 (venv creation) completed successfully")

        except Exception as e:
            self.wizard.log(f"Venv creation failed: {e}", "error")
            self.venv_status.config(text=f"❌ Failed: {e}", foreground="red")
            self.wizard.step_status["venv"] = False

        finally:
            self.venv_btn.config(state=tk.NORMAL)
            self.wizard.running_step = False
            self.wizard.update_progress()

    def auto_detect(self):
        """Auto-detect if venv exists"""
        # Check DEV section for simulation first
        config = configparser.ConfigParser()
        config_file = Path(__file__).parent / "config.ini"

        install_dir = Path(self.wizard.install_path.get())
        venv_dir = install_dir / self.venv_dir_name

        try:
            config.read(config_file)
            if config.getboolean('DEV', 'simulate_venv_complete', fallback=False):
                self.venv_status.config(
                    text=f"✅ Virtual environment (simulated) at {venv_dir}", foreground="orange")
                self.wizard.step_status["venv"] = True
                self.wizard.log("DEV: Simulating venv creation completion")
                return
        except Exception:
            pass  # Continue with normal detection if config read fails
        python_exe = venv_dir / ("Scripts" if os.name == "nt" else "bin") / \
            ("python.exe" if os.name == "nt" else "python")

        if venv_dir.exists() and python_exe.exists():
            self.venv_status.config(
                text=f"✅ Virtual environment already exists at {venv_dir}", foreground="green")
            self.wizard.step_status["venv"] = True
            self.wizard.log("Auto-detected existing venv")
        else:
            # Virtual environment doesn't exist or is invalid
            self.venv_status.config(
                text=f"❌ Virtual environment not found at {venv_dir}", foreground="red")
            self.wizard.step_status["venv"] = False
            self.wizard.log(f"Virtual environment not found at {venv_dir}")
