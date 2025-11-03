"""Step 4: Install Library"""
import os
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import configparser
from pyirc_bootstrapper import pip_exists_with_correct_sections

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

        config.read(config_file)

        # Get venv directory name from config
        self.venv_dir_name = config.get('Paths', 'venv_dir', fallback='.venv')

        # Get main library path from config
        main_library_str = config.get(
            'Dependencies', 'core_libraries', fallback='')
        if main_library_str:
            self.main_library_path = Path(main_library_str)
        else:
            raise Exception("Main library path not specified in config.ini")

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
        info_text = f"Main library: {self.main_library_path.name}"
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
            frame, length=300, mode='determinate', value=0)
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
                                   "Please complete Step 3 (Configure PyIRC) first.")
            return

        # Double-check PyIRC configuration
        if not pip_exists_with_correct_sections():
            messagebox.showerror("PyIRC Not Configured",
                                 "PyIRC configuration is missing or invalid. "
                                 "Please complete Step 3 first.")
            return

        self.wizard.running_step = True
        self.install_btn.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.execute, daemon=True)
        thread.start()

    def execute(self):
        """Install the library"""
        install_dir = Path(self.wizard.install_path.get())
        venv_python = install_dir / self.venv_dir_name / \
            ("Scripts/python.exe" if os.name == "nt" else "bin/python")

        self.wizard.log("=== Starting Step 4: Library Installation ===")
        self.wizard.log(f"Install directory: {install_dir}")
        self.wizard.log(f"Virtual environment Python: {venv_python}")
        self.wizard.log(f"Main library path: {self.main_library_path}")
        self.wizard.log(f"Additional packages: {self.additional_packages}")

        try:
            if not venv_python.exists():
                self.wizard.log(
                    f"Python executable not found at {venv_python}", "error")
                self.install_status.config(
                    text="❌ venv Python not found", foreground="red")
                self.wizard.step_status["library"] = False
                return

            # Step 1: Install main library
            self.install_progress.config(mode='indeterminate')
            self.install_progress.start(10)
            self.install_status.config(
                text=f"⏳ Installing {self.main_library_path.name}...")
            self.wizard.log(
                f"Installing main library from {self.main_library_path}")

            # Use CREATE_NO_WINDOW only if not in debug mode
            creation_flags = 0 if self.wizard.debug_mode else CREATE_NO_WINDOW
            capture_output = not self.wizard.debug_mode  # Don't capture if in debug mode
            self.wizard.log(
                f"Debug mode: {self.wizard.debug_mode}, using creation_flags: {creation_flags}, capture_output: {capture_output}")

            result = subprocess.run(
                [str(venv_python), "-m", "pip", "install",
                 str(self.main_library_path)],
                capture_output=capture_output,
                text=True,
                timeout=300,
                creationflags=creation_flags
            )

            # Log pip output for debugging (only if we captured it)
            if capture_output:
                if result.stdout:
                    self.wizard.log(f"Pip stdout: {result.stdout}")
                if result.stderr:
                    self.wizard.log(f"Pip stderr: {result.stderr}")

            if result.returncode != 0:
                self.wizard.log(
                    f"Main library installation failed with return code: {result.returncode}", "error")
                self.wizard.log(
                    f"Command: {' '.join([str(venv_python), '-m', 'pip', 'install', str(self.main_library_path)])}", "error")

                # Show error message, using stderr only if we captured it
                error_msg = result.stderr[:
                                          50] if capture_output and result.stderr else f"Return code: {result.returncode}"
                self.install_status.config(
                    text=f"❌ Install failed: {error_msg}", foreground="red")
                self.wizard.step_status["library"] = False
                return

            self.wizard.log("Main library installed successfully")
            self.wizard.log(
                f"Installation command: {' '.join([str(venv_python), '-m', 'pip', 'install', str(self.main_library_path)])}")

            # Step 2: Install additional packages if specified
            if self.additional_packages:
                self.install_status.config(
                    text="⏳ Installing additional packages...")
                self.wizard.log(
                    f"Installing additional packages: {self.additional_packages}")

                result = subprocess.run(
                    [str(venv_python), "-m", "pip", "install"] +
                    self.additional_packages,
                    capture_output=capture_output,
                    text=True,
                    timeout=300,
                    creationflags=creation_flags
                )

                # Log additional packages output for debugging (only if we captured it)
                if capture_output:
                    if result.stdout:
                        self.wizard.log(
                            f"Additional packages pip stdout: {result.stdout}")
                    if result.stderr:
                        self.wizard.log(
                            f"Additional packages pip stderr: {result.stderr}")

                if result.returncode != 0:
                    self.wizard.log(
                        f"Additional packages installation failed with return code: {result.returncode}", "warning")
                    self.wizard.log(
                        f"Additional packages command: {' '.join([str(venv_python), '-m', 'pip', 'install'] + self.additional_packages)}", "warning")
                else:
                    self.wizard.log(
                        "Additional packages installed successfully")
                    self.wizard.log(
                        f"Additional packages command: {' '.join([str(venv_python), '-m', 'pip', 'install'] + self.additional_packages)}")

            # Success!
            installed_list = [self.main_library_path.name] + \
                self.additional_packages
            self.install_status.config(
                text=f"✅ Installed: {', '.join(installed_list)}", foreground="green")
            self.wizard.step_status["library"] = True
            self.wizard.log(
                "=== Step 4: Library Installation Completed Successfully ===")

            # Trigger Step 5 to check if it can auto-create files
            if hasattr(self.wizard.files_step, 'auto_create_files'):
                self.wizard.after(
                    1000, self.wizard.files_step.auto_create_files)

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

    def auto_detect(self):
        """Auto-detect if libraries are already installed"""
        # Check DEV section for simulation first
        config = configparser.ConfigParser()
        config_file = Path(__file__).parent / "config.ini"

        try:
            config.read(config_file)
            if config.getboolean('DEV', 'simulate_library_complete', fallback=False):
                self.install_status.config(
                    text="✅ Libraries (simulated)", foreground="orange")
                self.wizard.step_status["library"] = True
                self.wizard.log(
                    "DEV: Simulating library installation completion")

                # Trigger Step 5 to check if it can auto-create files (same as real completion)
                if hasattr(self.wizard.files_step, 'auto_create_files'):
                    self.wizard.after(
                        1000, self.wizard.files_step.auto_create_files)
                return
        except Exception:
            pass  # Continue with normal detection if config read fails

        install_dir = Path(self.wizard.install_path.get())
        venv_python = install_dir / self.venv_dir_name / \
            ("Scripts/python.exe" if os.name == "nt" else "bin/python")

        if not venv_python.exists():
            self.install_status.config(
                text="❓ Virtual environment not found", foreground="gray")
            self.wizard.step_status["library"] = False
            return

        try:
            # Check if main library is installed
            result = subprocess.run([
                str(venv_python), "-c", f"import {self.main_library_path}"
            ], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                self.install_status.config(
                    text="✅ Libraries already installed", foreground="green")
                self.wizard.step_status["library"] = True
                self.wizard.log("Auto-detected existing library installation")
            else:
                self.install_status.config(
                    text="❓ Libraries not installed", foreground="gray")
                self.wizard.step_status["library"] = False

        except (subprocess.TimeoutExpired, Exception) as e:
            self.wizard.log(f"Auto-detect library error: {e}", "warning")
            self.install_status.config(
                text="❓ Could not verify installation", foreground="gray")
            self.wizard.step_status["library"] = False
