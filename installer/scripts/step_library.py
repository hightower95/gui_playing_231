"""Step 4: Install Library"""
import os
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import configparser
from .pyirc_bootstrapper import pip_exists_with_correct_sections

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
        """Load library configuration from installation_settings.ini"""
        config = configparser.ConfigParser()
        config_file = Path(__file__).parent.parent / \
            "installation_settings.ini"  # Go up one level from scripts/

        config.read(config_file)

        # Get venv directory name from config
        self.venv_dir_name = config.get('Paths', 'venv_dir', fallback='.venv')

        # Get DEV settings
        self.skip_local_index = config.getboolean(
            'DEV', 'skip_local_index', fallback=False)
        if self.skip_local_index:
            self.wizard.log(
                "DEV: Skip local index enabled - will use PyPI directly")

        # Get main library from config (can be a package name or path)
        main_library_str = config.get(
            'Dependencies', 'core_libraries', fallback='')
        if main_library_str:
            # If it looks like a file path, use Path, otherwise treat as package name
            if '/' in main_library_str or '\\' in main_library_str or main_library_str.endswith(('.whl', '.tar.gz')):
                self.main_library_path = Path(main_library_str)
            else:
                # It's a package name, store as string
                self.main_library_path = main_library_str
        else:
            raise Exception(
                "Main library not specified in installation_settings.ini")

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
                f"Failed to read dependencies from installation_settings.ini: {e}", "warning")
            self.additional_packages = []

    def build_pip_command(self, venv_python, packages):
        """Build pip install command with appropriate index settings"""
        cmd = [str(venv_python), "-m", "pip", "install"]

        # Add index-url to skip local PyIRC configuration if requested
        if self.skip_local_index:
            cmd.extend(["--index-url", "https://pypi.org/simple/"])
            self.wizard.log("Using PyPI directly (skipping local index)")

        # Add the packages to install
        if isinstance(packages, (list, tuple)):
            cmd.extend(str(pkg) for pkg in packages)
        else:
            cmd.append(str(packages))

        return cmd

    def build_ui(self, parent):
        """Build the UI for library installation"""
        frame = ttk.Frame(parent)
        frame.pack(fill="x")

        # Show what will be installed
        main_lib_name = self.main_library_path.name if isinstance(
            self.main_library_path, Path) else self.main_library_path
        info_text = f"Main library: {main_lib_name}"
        ttk.Label(frame, text=info_text, foreground="blue").pack(
            anchor="w", pady=(0, 2))

        if self.additional_packages:
            deps_text = f"Additional: {', '.join(self.additional_packages)}"
            ttk.Label(frame, text=deps_text, foreground="gray").pack(
                anchor="w", pady=(0, 2))

        # Show index URL information
        if self.skip_local_index:
            index_text = "📦 Index: PyPI (https://pypi.org/simple/) [Local index disabled]"
            index_color = "orange"
        else:
            index_text = "📦 Index: Local PyIRC configuration"
            index_color = "green"

        ttk.Label(frame, text=index_text, foreground=index_color).pack(
            anchor="w", pady=(0, 2))

        # Show simulation status if enabled
        config = configparser.ConfigParser()
        config_file = Path(__file__).parent.parent / \
            "installation_settings.ini"

        try:
            config.read(config_file)
            if config.getboolean('DEV', 'simulate_library_complete', fallback=False):
                sim_text = "🎭 Simulation: Step completion is simulated"
                ttk.Label(frame, text=sim_text, foreground="purple").pack(
                    anchor="w", pady=(0, 5))
            else:
                # Add spacing when no simulation
                ttk.Frame(frame, height=3).pack(pady=(0, 3))
        except Exception:
            # Add spacing when config read fails
            ttk.Frame(frame, height=3).pack(pady=(0, 3))

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

        # Check PyIRC requirements only if not skipping local index
        if not self.skip_local_index:
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
        else:
            self.wizard.log(
                "DEV: Skipping PyIRC validation (using PyPI directly)")

        self.wizard.running_step = True
        self.install_btn.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.execute, daemon=True)
        thread.start()

    def execute(self):
        """Install the library"""
        install_dir = Path(self.wizard.install_path.get())
        venv_python = install_dir / self.venv_dir_name / \
            ("Scripts/python.exe" if os.name == "nt" else "bin/python")

        self.wizard.log("=== LIBRARY INSTALLATION - DETAILED LOG ===")
        self.wizard.log(f"Install directory: {install_dir}")
        self.wizard.log(f"Expected venv name: {self.venv_dir_name}")
        self.wizard.log(f"Virtual environment Python: {venv_python}")
        self.wizard.log(f"Main library path: {self.main_library_path}")
        self.wizard.log(f"Additional packages: {self.additional_packages}")
        self.wizard.log(f"Skip local index: {self.skip_local_index}")

        # Log index URL configuration
        if self.skip_local_index:
            self.wizard.log(
                "Index URL: Using PyPI directly (https://pypi.org/simple/) - DEV MODE")
        else:
            self.wizard.log("Index URL: Using local PyIRC configuration")

        try:
            # Verify venv Python exists and get detailed info
            if not venv_python.exists():
                self.wizard.log(
                    f"ERROR: Python executable not found at {venv_python}", "error")
                self.wizard.log(f"Checked path: {venv_python.absolute()}", "error")
                self.wizard.log(f"Parent directory exists: {venv_python.parent.exists()}", "error")
                if venv_python.parent.exists():
                    self.wizard.log(f"Contents of {venv_python.parent}: {list(venv_python.parent.iterdir())}", "error")
                self.install_status.config(
                    text="❌ venv Python not found at startup", foreground="red")
                self.wizard.step_status["library"] = False
                return

            # Verify which Python we're actually using
            try:
                python_version_result = subprocess.run([
                    str(venv_python), "--version"
                ], capture_output=True, text=True, timeout=10)
                self.wizard.log(f"Venv Python version: {python_version_result.stdout.strip()}")
                self.wizard.log(f"Venv Python path verified: {venv_python.absolute()}")
            except Exception as e:
                self.wizard.log(f"Could not get venv Python version: {e}", "warning")

            # Step 1: Install main library
            self.install_progress.config(mode='indeterminate')
            self.install_progress.start(10)
            main_lib_name = self.main_library_path.name if isinstance(
                self.main_library_path, Path) else self.main_library_path
            self.install_status.config(
                text=f"⏳ Installing {main_lib_name}...")
            self.wizard.log(
                f"Installing main library from {self.main_library_path}")

            # Always capture output for verbose logging, but show console in debug mode
            creation_flags = 0 if self.wizard.debug_mode else CREATE_NO_WINDOW
            self.wizard.log(f"Debug mode: {self.wizard.debug_mode}")
            self.wizard.log(f"Creation flags: {creation_flags}")

            # Build pip command with appropriate index settings
            pip_cmd = self.build_pip_command(
                venv_python, self.main_library_path)
            
            self.wizard.log(f"Executing pip command: {' '.join(pip_cmd)}")
            self.wizard.log("--- PIP EXECUTION START ---")

            result = subprocess.run(
                pip_cmd,
                capture_output=True,  # Always capture for logging
                text=True,
                timeout=300,
                creationflags=creation_flags
            )

            # Always log pip output for verbose logging
            self.wizard.log(f"Pip return code: {result.returncode}")
            if result.stdout:
                self.wizard.log("=== PIP STDOUT ===")
                self.wizard.log(result.stdout)
            if result.stderr:
                self.wizard.log("=== PIP STDERR ===")
                self.wizard.log(result.stderr)
            self.wizard.log("--- PIP EXECUTION END ---")

            if result.returncode != 0:
                self.wizard.log(
                    f"Main library installation failed with return code: {result.returncode}", "error")
                self.wizard.log(
                    f"Command: {' '.join(pip_cmd)}", "error")

                # Show error message
                error_msg = result.stderr[:50] if result.stderr else f"Return code: {result.returncode}"
                self.install_status.config(
                    text=f"❌ Install failed: {error_msg}", foreground="red")
                self.wizard.step_status["library"] = False
                return

            self.wizard.log("Main library installed successfully")
            self.wizard.log(
                f"Installation command: {' '.join(pip_cmd)}")

            # Step 2: Install additional packages if specified
            if self.additional_packages:
                self.install_status.config(
                    text="⏳ Installing additional packages...")
                self.wizard.log(
                    f"Installing additional packages: {self.additional_packages}")

                # Build pip command for additional packages
                additional_pip_cmd = self.build_pip_command(
                    venv_python, self.additional_packages)
                
                self.wizard.log(f"Executing additional packages command: {' '.join(additional_pip_cmd)}")
                self.wizard.log("--- ADDITIONAL PACKAGES PIP EXECUTION START ---")

                result = subprocess.run(
                    additional_pip_cmd,
                    capture_output=True,  # Always capture for logging
                    text=True,
                    timeout=300,
                    creationflags=creation_flags
                )

                # Always log additional packages output for verbose logging
                self.wizard.log(f"Additional packages pip return code: {result.returncode}")
                if result.stdout:
                    self.wizard.log("=== ADDITIONAL PACKAGES PIP STDOUT ===")
                    self.wizard.log(result.stdout)
                if result.stderr:
                    self.wizard.log("=== ADDITIONAL PACKAGES PIP STDERR ===")
                    self.wizard.log(result.stderr)
                self.wizard.log("--- ADDITIONAL PACKAGES PIP EXECUTION END ---")

                if result.returncode != 0:
                    self.wizard.log(
                        f"Additional packages installation failed with return code: {result.returncode}", "warning")
                    self.wizard.log(
                        f"Additional packages command: {' '.join(additional_pip_cmd)}", "warning")
                else:
                    self.wizard.log(
                        "Additional packages installed successfully")
                    self.wizard.log(
                        f"Additional packages command: {' '.join(additional_pip_cmd)}")

            # Success!
            main_lib_name = self.main_library_path.name if isinstance(
                self.main_library_path, Path) else self.main_library_path
            installed_list = [main_lib_name] + \
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
        config_file = Path(__file__).parent.parent / \
            "installation_settings.ini"

        try:
            config.read(config_file)
            if config.getboolean('DEV', 'simulate_library_complete', fallback=False):
                self.install_status.config(
                    text="✅ Libraries (simulated completion)", foreground="purple")
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

        self.wizard.log("=== LIBRARY AUTO-DETECTION ===")
        self.wizard.log(f"Checking for libraries in venv: {venv_python}")
        self.wizard.log(f"Venv directory: {self.venv_dir_name}")
        self.wizard.log(f"Install directory: {install_dir}")

        if not venv_python.exists():
            self.wizard.log(f"Venv Python not found at: {venv_python}")
            self.install_status.config(
                text="❓ Virtual environment not found at startup", foreground="gray")
            self.wizard.step_status["library"] = False
            return

        try:
            # Run pip list to check installed packages
            pip_list_cmd = [str(venv_python), "-m", "pip", "list", "--format=freeze"]
            self.wizard.log(f"Running: {' '.join(pip_list_cmd)}")
            
            result = subprocess.run(pip_list_cmd, capture_output=True, text=True, timeout=15)
            
            self.wizard.log(f"Pip list return code: {result.returncode}")
            if result.stdout:
                self.wizard.log("=== PIP LIST OUTPUT ===")
                self.wizard.log(result.stdout)
            if result.stderr:
                self.wizard.log("=== PIP LIST STDERR ===")
                self.wizard.log(result.stderr)

            if result.returncode != 0:
                self.wizard.log(
                    f"Failed to run pip list: {result.stderr}", "warning")
                self.install_status.config(
                    text="❓ Could not check installed packages", foreground="gray")
                self.wizard.step_status["library"] = False
                return

            # Parse installed packages
            installed_packages = {}
            for line in result.stdout.strip().split('\n'):
                if '==' in line:
                    package_name, version = line.split('==', 1)
                    installed_packages[package_name.lower()] = version

            self.wizard.log(
                f"Found {len(installed_packages)} installed packages in venv")

            # Check if main library is installed
            main_lib_name = (self.main_library_path.name if isinstance(
                self.main_library_path, Path) else self.main_library_path).lower()
            main_lib_installed = main_lib_name in installed_packages

            # Check additional packages
            additional_installed = []
            additional_missing = []
            for pkg in self.additional_packages:
                pkg_name = pkg.lower()
                if pkg_name in installed_packages:
                    additional_installed.append(
                        f"{pkg}=={installed_packages[pkg_name]}")
                else:
                    additional_missing.append(pkg)

            # Determine status
            if main_lib_installed and not additional_missing:
                # All packages are installed
                installed_list = [
                    f"{main_lib_name}=={installed_packages[main_lib_name]}"] + additional_installed
                self.install_status.config(
                    text=f"✅ Already installed: {', '.join([pkg.split('==')[0] for pkg in installed_list])}",
                    foreground="green")
                self.wizard.step_status["library"] = True
                self.wizard.log(
                    f"Auto-detected installed packages: {', '.join(installed_list)}")
            elif main_lib_installed and additional_missing:
                # Main library installed but some additional packages missing
                self.install_status.config(
                    text=f"⚠️ {main_lib_name} installed, missing: {', '.join(additional_missing)}",
                    foreground="orange")
                self.wizard.step_status["library"] = False
                self.wizard.log(
                    f"Main library {main_lib_name} found, but missing additional packages: {additional_missing}")
            else:
                # Main library not installed
                self.install_status.config(
                    text=f"❓ {main_lib_name} not installed", foreground="gray")
                self.wizard.step_status["library"] = False
                self.wizard.log(
                    f"Main library {main_lib_name} not found in pip list")

        except (subprocess.TimeoutExpired, Exception) as e:
            self.wizard.log(f"Auto-detect library error: {e}", "warning")
            self.install_status.config(
                text="❓ Could not verify installation", foreground="gray")
            self.wizard.step_status["library"] = False
