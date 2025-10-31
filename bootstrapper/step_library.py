"""Step 4: Install Library"""
import os
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import configparser

# Windows-specific flag to hide console window
if sys.platform == "win32":
    import subprocess
    CREATE_NO_WINDOW = 0x08000000
else:
    CREATE_NO_WINDOW = 0


class LibraryStep:
    def __init__(self, wizard):
        self.wizard = wizard
        self.install_btn = None
        self.install_progress = None
        self.install_status = None
        self.main_library_path = None
        self.additional_packages = []
        self.load_config()

    def load_config(self):
        """Load library configuration from config.ini"""
        config = configparser.ConfigParser()
        config_file = Path(__file__).parent / "config.ini"

        # Get the parent folder of bootstrapper as the main library
        self.main_library_path = Path(__file__).parent.parent

        try:
            config.read(config_file)
            packages_str = config.get(
                'Dependencies', 'additional_packages', fallback='')
            # Parse comma-separated packages and strip whitespace
            self.additional_packages = [
                pkg.strip() for pkg in packages_str.split(',')
                if pkg.strip()
            ]
            self.wizard.log(f"Main library: {self.main_library_path}")
            self.wizard.log(f"Additional packages: {self.additional_packages}")
        except Exception as e:
            self.wizard.log(
                f"Failed to read dependencies from config.ini: {e}", "warning")
            self.additional_packages = []

    def build_ui(self, parent):
        """Build the UI for library installation"""
        frame = ttk.Frame(parent)
        frame.pack(fill="x")

        # Show what will be installed
        info_text = f"Main library: {self.main_library_path.name} (editable mode)"
        ttk.Label(frame, text=info_text, foreground="blue").pack(
            anchor="w", pady=(0, 2))

        if self.additional_packages:
            deps_text = f"Additional: {', '.join(self.additional_packages)}"
            ttk.Label(frame, text=deps_text, foreground="gray").pack(
                anchor="w", pady=(0, 5))

        self.install_btn = ttk.Button(frame, text="Install Libraries",
                                      command=self.run_threaded)
        self.install_btn.pack(anchor="w", pady=(5, 5))

        self.install_progress = ttk.Progressbar(
            frame, length=300, mode='indeterminate')
        self.install_progress.pack(anchor="w", pady=(0, 5))

        self.install_status = ttk.Label(
            frame, text="⏸ Not installed", foreground="gray")
        self.install_status.pack(anchor="w")

    def run_threaded(self):
        """Run library installation in a separate thread"""
        if self.wizard.running_step:
            messagebox.showwarning(
                "Busy", "Another step is running. Please wait.")
            return

        if not self.wizard.step_status["pyirc"]:
            messagebox.showwarning("Step 3 Required",
                                   "Please complete Step 3 (Configure token) first.")
            return

        self.wizard.running_step = True
        self.install_btn.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.execute, daemon=True)
        thread.start()

    def execute(self):
        """Install the library"""
        install_dir = Path(self.wizard.install_path.get())
        venv_python = install_dir / \
            (".venv/Scripts/python.exe" if os.name == "nt" else ".venv/bin/python")

        try:
            if not venv_python.exists():
                self.wizard.log(
                    f"Python executable not found at {venv_python}", "error")
                self.install_status.config(
                    text="❌ venv Python not found", foreground="red")
                self.wizard.step_status["library"] = False
                return

            # Step 1: Upgrade pip
            self.install_status.config(text="⏳ Upgrading pip...")
            self.install_progress.start(10)
            self.wizard.log("Upgrading pip")

            result = subprocess.run(
                [str(venv_python), "-m", "pip", "install", "--upgrade", "pip"],
                capture_output=True,
                text=True,
                timeout=120,
                creationflags=CREATE_NO_WINDOW
            )

            if result.returncode != 0:
                self.wizard.log(
                    f"Pip upgrade warning: {result.stderr}", "warning")

            # Step 2: Install main library in editable mode
            self.install_status.config(
                text=f"⏳ Installing {self.main_library_path.name} (editable)...")
            self.wizard.log(
                f"Installing main library from {self.main_library_path}")

            result = subprocess.run(
                [str(venv_python), "-m", "pip", "install",
                 "-e", str(self.main_library_path)],
                capture_output=True,
                text=True,
                timeout=300,
                creationflags=CREATE_NO_WINDOW
            )

            if result.returncode != 0:
                self.wizard.log(
                    f"Main library installation failed: {result.stderr}", "error")
                self.install_status.config(
                    text=f"❌ Install failed: {result.stderr[:50]}", foreground="red")
                self.wizard.step_status["library"] = False
                return

            self.wizard.log("Main library installed successfully")

            # Step 3: Install additional packages if specified
            if self.additional_packages:
                self.install_status.config(
                    text="⏳ Installing additional packages...")
                self.wizard.log(
                    f"Installing additional packages: {self.additional_packages}")

                result = subprocess.run(
                    [str(venv_python), "-m", "pip", "install"] +
                    self.additional_packages,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    creationflags=CREATE_NO_WINDOW
                )

                if result.returncode != 0:
                    self.wizard.log(
                        f"Additional packages warning: {result.stderr}", "warning")
                else:
                    self.wizard.log(
                        "Additional packages installed successfully")

            # Success!
            installed_list = [self.main_library_path.name] + \
                self.additional_packages
            self.install_status.config(
                text=f"✅ Installed: {', '.join(installed_list)}", foreground="green")
            self.wizard.step_status["library"] = True

        except subprocess.TimeoutExpired:
            self.wizard.log("Installation timed out", "error")
            self.install_status.config(
                text="❌ Installation timed out", foreground="red")
            self.wizard.step_status["library"] = False
        except Exception as e:
            self.wizard.log(f"Library installation error: {e}", "error")
            self.install_status.config(
                text=f"❌ Error: {str(e)[:50]}", foreground="red")
            self.wizard.step_status["library"] = False
        finally:
            self.install_progress.stop()
            self.install_btn.config(state=tk.NORMAL)
            self.wizard.running_step = False
            self.wizard.update_progress()
