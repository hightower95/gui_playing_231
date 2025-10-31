"""Step 2: Create Virtual Environment"""
import os
import venv
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import threading


class VenvStep:
    def __init__(self, wizard):
        self.wizard = wizard
        self.venv_btn = None
        self.venv_progress = None
        self.venv_status = None

    def build_ui(self, parent):
        """Build the UI for venv creation"""
        frame = ttk.Frame(parent)
        frame.pack(fill="x")

        self.venv_btn = ttk.Button(frame, text="Create Virtual Environment",
                                   command=self.run_threaded)
        self.venv_btn.pack(anchor="w", pady=(0, 5))

        self.venv_progress = ttk.Progressbar(
            frame, length=300, mode='indeterminate')
        self.venv_progress.pack(anchor="w", pady=(0, 5))

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
        venv_dir = install_dir / ".venv"

        try:
            self.venv_status.config(text="⏳ Creating virtual environment...")
            self.venv_progress.start(10)
            self.wizard.log(f"Creating venv at {venv_dir}")

            if venv_dir.exists():
                self.wizard.log(
                    "Venv directory already exists, skipping creation")
                self.venv_status.config(
                    text="✅ Virtual environment already exists", foreground="green")
            else:
                venv.create(venv_dir, with_pip=True)
                self.wizard.log("Venv created successfully")
                self.venv_status.config(
                    text="✅ Virtual environment created", foreground="green")

            self.wizard.step_status["venv"] = True

        except Exception as e:
            self.wizard.log(f"Venv creation failed: {e}", "error")
            self.venv_status.config(text=f"❌ Failed: {e}", foreground="red")
            self.wizard.step_status["venv"] = False

        finally:
            self.venv_progress.stop()
            self.venv_btn.config(state=tk.NORMAL)
            self.wizard.running_step = False
            self.wizard.update_progress()

    def auto_detect(self):
        """Auto-detect if venv exists"""
        install_dir = Path(self.wizard.install_path.get())
        venv_dir = install_dir / ".venv"
        python_exe = venv_dir / ("Scripts" if os.name == "nt" else "bin") / \
            ("python.exe" if os.name == "nt" else "python")

        if venv_dir.exists() and python_exe.exists():
            self.venv_status.config(
                text="✅ Virtual environment already exists", foreground="green")
            self.wizard.step_status["venv"] = True
            self.wizard.log("Auto-detected existing venv")
