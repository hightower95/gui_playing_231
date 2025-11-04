"""Step 2: Create Virtual Environment"""
import os
import sys
import venv
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from .base_step import BaseStep
from .constants import *
from .threading_utils import run_async


class VenvStep(BaseStep):
    def __init__(self, wizard):
        super().__init__(wizard)

    def get_step_key(self) -> str:
        return STEP_VENV

    def build_ui(self, parent):
        """Build the UI for venv creation"""
        frame = ttk.Frame(parent)
        frame.pack(fill="x")

        self.create_action_button(frame, BTN_CREATE_VENV, self.run_threaded)
        self.create_status_label(frame, STATUS_NOT_RUN)

    @run_async()
    def run_threaded(self):
        """Run venv creation in a separate thread"""
        prerequisites = self.check_prerequisites()
        if prerequisites:
            messagebox.showwarning("Missing Requirements",
                                   f"Please complete: {', '.join(prerequisites)}")
            return

        self.execute()

    def check_prerequisites(self) -> list:
        """Check if folder step is completed"""
        missing = []
        if not self.wizard.step_status[STEP_FOLDER]:
            missing.append("folder selection")
        return missing

    def execute(self):
        """Create the virtual environment"""
        install_dir = self.get_install_path()
        venv_dir = self.get_venv_path()

        try:
            self.update_status(STATUS_RUNNING, COLOR_BLUE)
            self.log(f"Creating venv at {venv_dir}")
            self.log(f"Python executable: {sys.executable}")
            self.log(f"Target directory: {install_dir}")

            if venv_dir.exists():
                self.log("Venv directory already exists, checking validity...")
                python_exe = venv_dir / ("Scripts" if os.name == "nt" else "bin") / \
                    ("python.exe" if os.name == "nt" else "python")

                if python_exe.exists():
                    self.log(f"Valid Python executable found at: {python_exe}")
                    self.log(
                        "Venv directory already exists and is valid, skipping creation")
                    self.update_status(
                        f"✅ Virtual environment already exists at {venv_dir}", COLOR_GREEN)
                else:
                    self.log(
                        "Venv directory exists but no valid Python executable found, recreating...")
                    shutil.rmtree(venv_dir)
                    self.log("Removed invalid venv directory")
                    self.log("Creating new virtual environment...")
                    venv.create(venv_dir, with_pip=True)
                    self.log(f"Venv created successfully at: {venv_dir}")
                    self.update_status(
                        f"✅ Virtual environment created at {venv_dir}", COLOR_GREEN)
            else:
                self.log("Creating new virtual environment...")
                venv.create(venv_dir, with_pip=True)
                self.log(f"Venv created successfully at: {venv_dir}")

                # Verify creation
                python_exe = venv_dir / ("Scripts" if os.name == "nt" else "bin") / \
                    ("python.exe" if os.name == "nt" else "python")
                if python_exe.exists():
                    self.log(f"Verified Python executable at: {python_exe}")
                else:
                    self.log(
                        f"Warning: Python executable not found at expected location: {python_exe}", "warning")

                self.update_status(
                    f"✅ Virtual environment created at {venv_dir}", COLOR_GREEN)

            self.mark_complete()
            self.log("Step 2 (venv creation) completed successfully")

        except Exception as e:
            self.log(f"Venv creation failed: {e}", "error")
            self.update_status(f"❌ Failed: {e}", COLOR_RED)
            self.mark_incomplete()

    def auto_detect(self):
        """Auto-detect if venv exists"""
        # Check DEV section for simulation first
        if self.is_simulated():
            venv_dir = self.get_venv_path()
            self.update_status(
                f"✅ Virtual environment (simulated) at {venv_dir}", COLOR_ORANGE)
            self.mark_complete()
            self.log("DEV: Simulating venv creation completion")
            return

        venv_dir = self.get_venv_path()
        python_exe = venv_dir / ("Scripts" if os.name == "nt" else "bin") / \
            ("python.exe" if os.name == "nt" else "python")

        if venv_dir.exists() and python_exe.exists():
            self.update_status(
                f"✅ Virtual environment already exists at {venv_dir}", COLOR_GREEN)
            self.mark_complete()
            self.log("Auto-detected existing venv")
        else:
            # Virtual environment doesn't exist or is invalid
            self.update_status(
                f"❌ Virtual environment not found at {venv_dir}", COLOR_RED)
            self.mark_incomplete()
            self.wizard.log(f"Virtual environment not found at {venv_dir}")
