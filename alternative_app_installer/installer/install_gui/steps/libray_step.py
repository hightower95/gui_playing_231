"""
Library Installation Step - Install required Python libraries into the virtual environment

This step handles:
- Retrieving venv path from shared state
- Getting list of libraries to install from config
- Detecting latest stable versions
- Installing libraries via pip with progress tracking
- Verifying installation via pip show
- Detecting if libraries came from local index-url
- Uses only native Python libraries (tkinter)
"""
import os
import queue
import threading
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import re
from urllib.parse import urlparse

from .base_step import BaseStep
from ..utilities.version_manager import (
    get_latest_stable_version,
    get_installed_version,
    detect_local_index,
    get_all_versions,
    parse_version
)


class LibraryInstallationWorker(threading.Thread):
    """Background worker for library installation that writes a pip JSON report.

    Returns on the result_queue a tuple:
      (success: bool, message: str, report_path: Optional[str], stdout: str, stderr: str)
    """

    def __init__(self, venv_python: Path, libraries: List[str], progress_queue: queue.Queue, result_queue: queue.Queue):
        super().__init__()
        self.venv_python = venv_python
        self.libraries = libraries
        self.progress_queue = progress_queue
        self.result_queue = result_queue
        self.daemon = True

    def run(self):
        """Execute library installation and write pip --report JSON."""
        logging.info(
            f"Library step: Starting installation worker for libraries: {self.libraries}")
        logging.info(
            f"Library step: Using Python executable: {self.venv_python}")

        self.progress_queue.put("🔄 Starting library installation...")
        self.progress_queue.put(f"🐍 Using Python: {self.venv_python}")
        self.progress_queue.put(
            f"📦 Libraries to install: {', '.join(self.libraries)}")

        # Prepare pip report path under installer/logs
        try:
            installer_dir = Path(__file__).resolve().parents[3]
            logging.debug(f"Library worker: Resolved installer directory: {installer_dir}")
        except Exception as e:
            installer_dir = Path.cwd()
            logging.warning(f"Library worker: Failed to resolve installer dir, using cwd: {installer_dir} (error: {e})")

        logs_dir = installer_dir / 'logs'
        logging.debug(f"Library worker: Logs directory path: {logs_dir}")
        try:
            logs_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logging.error(f"Library worker: Failed to create logs directory: {e}")
            pass

        timestamp = int(time.time())
        report_path = logs_dir / f"pip_install_report_{timestamp}.json"
        logging.debug(f"Library worker: Pip report will be saved to: {report_path}")

        # Build command
        cmd = [str(self.venv_python), "-m", "pip", "install",
               "--report", str(report_path)] + self.libraries
        self.progress_queue.put(f"⚡ Running: {' '.join(cmd)}")
        logging.info(f"Library step: Executing pip command: {' '.join(cmd)}")

        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minutes timeout
                cwd=self.venv_python.parent.parent
            )

            logging.info(
                f"Library step: Pip install completed with return code: {process.returncode}")
            if process.stdout:
                logging.debug(
                    f"Library step: Pip stdout: {process.stdout[:500]}...")
            if process.stderr:
                logging.debug(
                    f"Library step: Pip stderr: {process.stderr[:500]}...")

            # Emit stdout/stderr to progress queue
            if process.stdout:
                self.progress_queue.put("📝 Installation stdout:")
                for line in process.stdout.split('\n'):
                    if line.strip():
                        self.progress_queue.put(f"   {line}")
            if process.stderr:
                self.progress_queue.put("📝 Installation stderr:")
                for line in process.stderr.split('\n'):
                    if line.strip():
                        self.progress_queue.put(f"   {line}")

            if process.returncode == 0:
                self.progress_queue.put(
                    "✅ Library installation completed successfully!")
                self.result_queue.put((True, "Libraries installed successfully", str(
                    report_path), process.stdout or "", process.stderr or ""))
            else:
                self.progress_queue.put(
                    f"❌ Library installation failed with code: {process.returncode}")
                self.result_queue.put((False, f"Installation failed: {process.stderr}", str(
                    report_path), process.stdout or "", process.stderr or ""))

        except subprocess.TimeoutExpired:
            self.progress_queue.put("❌ Library installation timed out")
            self.result_queue.put(
                (False, "Installation timed out", str(report_path), "", ""))
        except Exception as e:
            self.progress_queue.put(f"❌ Installation error: {e}")
            self.result_queue.put(
                (False, f"Installation error: {e}", str(report_path), "", str(e)))


class InstallLibraryStep(BaseStep):
    def __init__(self, installation_settings, shared_state, *args, **kwargs):
        super().__init__(installation_settings, shared_state, *args, **kwargs)

        # Worker thread and queues
        self.worker = None
        self.progress_queue = queue.Queue()
        self.result_queue = queue.Queue()

        # Library configuration
        self._core_library = None
        self._additional_libraries = []
        self._all_libraries = []
        self._venv_python = None
        self._installation_in_progress = False
        self._installation_completed = False
        self._install_output = ""  # Store installation output for local index detection
        self._last_install_report = None

        # UI widgets
        self.checklist_labels = {}
        self.output_text = None
        self.install_button = None
        self.progress_bar = None

    # ========================================================================
    # Required BaseStep Methods
    # ========================================================================

    def get_title(self) -> str:
        return "Install Libraries"

    def get_description(self) -> str:
        # venv_name = self._venv_python.parent.parent.name if self._venv_python else "UNKNOWN"

        # info_label = ttk.Label(parent_frame, text=info_text, font=("Arial", 9), foreground="#28a745")
        # info_label.pack(pady=(0, 10))
        return "Setup application environment"

    def get_hint_text(self) -> str:
        # if self._all_libraries:
        #     return f"Installing: {', '.join(self._all_libraries)}"
        # venv_name = self._venv_python if self._venv_python else "UNKNOWN"
        # info_text = f"Installing into virtual environment: {venv_name}"
        return "Installing required Python libraries into the virtual environment."

    def can_complete(self) -> bool:
        """Check if step can be completed"""
        return self._installation_completed

    def create_widgets(self, parent_frame: tk.Frame):
        """Create UI widgets for library installation"""
        # Get configuration first
        self._load_configuration()

        # Confirmation label that we're using the virtual environment
        # venv_name = self._venv_python.parent.parent.name
        # info_text = f"Installing into virtual environment: {venv_name}"
        # info_label = ttk.Label(parent_frame, text=info_text, font=("Arial", 9), foreground="#28a745")
        # info_label.pack(pady=(0, 10))

        # Checklist frame
        self._create_checklist(parent_frame)

        # Progress bar
        self.progress_bar = ttk.Progressbar(parent_frame, mode='indeterminate')
        self.progress_bar.pack(fill="x", pady=(0, 10))
        self.progress_bar.pack_forget()  # Hidden initially

        # Install button
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(fill="x", pady=(0, 10))

        self.install_button = ttk.Button(button_frame, text="Install Libraries",
                                         command=self._start_library_installation)
        self.install_button.pack(side="left")

        # Output text area
        self.output_text = scrolledtext.ScrolledText(parent_frame, height=12, width=80,
                                                     font=("Courier New", 9),
                                                     bg="#1e1e1e", fg="#d4d4d4",
                                                     insertbackground="#d4d4d4")
        self.output_text.pack(fill="both", expand=True, pady=(10, 0))
        self.output_text.pack_forget()  # Hidden initially

        # Initial state update
        self._update_ui_state()

        # Delay version check to ensure widgets are rendered first
        parent_frame.after(500, self._populate_initial_checklist)

        # Start monitoring queues
        parent_frame.after(100, self._check_queues)

    def complete_step(self) -> bool:
        """Complete the library installation step"""
        if not self.can_complete():
            messagebox.showwarning(
                "Installation Not Complete",
                "Please install and verify libraries before proceeding."
            )
            return False

        # Update shared state
        self.update_shared_state("libraries_installed", True)
        self.update_shared_state("core_library", self._core_library)
        self.update_shared_state("installed_libraries", self._all_libraries)

        self.mark_completed()
        return True

    def cleanup_widgets(self):
        """Clean up when step becomes inactive"""
        if self.worker and self.worker.is_alive():
            self.worker = None

    # ========================================================================
    # Configuration Methods
    # ========================================================================

    def _load_configuration(self):
        """Load configuration from settings and shared state"""
        # Get venv path from shared state
        venv_path = self.get_shared_state("venv_path", "")
        if not venv_path:
            raise ValueError(
                "Virtual environment path not found in shared state")

        # Construct Python executable path
        venv_dir = Path(venv_path)
        logging.debug(f"Library step: Virtual environment directory: {venv_dir}")
        if os.name == 'nt':  # Windows
            self._venv_python = venv_dir / 'Scripts' / 'python.exe'
        else:  # Unix-like
            self._venv_python = venv_dir / 'bin' / 'python'
        
        logging.debug(f"Library step: Python executable path: {self._venv_python}")

        if not self._venv_python.exists():
            raise ValueError(
                f"Python executable not found: {self._venv_python}")

        # Get libraries from config
        self._core_library = self.installation_settings.get(
            'Step_Install_Libraries', 'core_library', fallback='requests'
        )

        additional_str = self.installation_settings.get(
            'Step_Install_Libraries', 'additional_packages', fallback=''
        )

        if additional_str.strip():
            self._additional_libraries = [
                lib.strip() for lib in additional_str.split(',') if lib.strip()]
        else:
            self._additional_libraries = []

        # Combine all libraries
        self._all_libraries = [self._core_library] + self._additional_libraries

    # ========================================================================
    # Checklist Methods
    # ========================================================================

    def _create_checklist(self, parent_frame):
        """Create the installation checklist"""
        checklist_frame = ttk.LabelFrame(
            parent_frame, text="Installation Progress", padding=10)
        checklist_frame.pack(fill="x", pady=(0, 15))

        self.checklist_frame = checklist_frame

        # Get stable version setting (only applies to core library)
        get_stable = self.installation_settings.getboolean(
            'Step_Install_Libraries', 'get_latest_stable_version', fallback=True)

        # Create version text - stable only applies to core library
        if get_stable:
            version_text = f"1. Get {self._core_library} version (stable)"
        else:
            version_text = f"1. Get {self._core_library} version (latest)"

        # Create checklist items with library names
        libs_text = ', '.join(self._all_libraries)
        checklist_items = [
            ("version", version_text),
            ("index", "2. Using index-url"),
            ("installed", f"3. Install {libs_text}"),
            ("verified", "4. Verified (via pip show)")
        ]

        for key, text in checklist_items:
            frame = ttk.Frame(checklist_frame)
            frame.pack(fill="x", pady=2)

            label = ttk.Label(frame, text=text, font=("Arial", 9))
            label.pack(side="left")

            status_label = ttk.Label(
                frame, text="⏳ Pending", font=("Arial", 9))
            status_label.pack(side="right")

            self.checklist_labels[key] = status_label

    def _populate_initial_checklist(self):
        """Populate initial checklist information"""
        # Get latest version for core library (stable or latest based on config)
        try:
            if self._venv_python and self._core_library:
                get_stable = self.installation_settings.getboolean(
                    'Step_Install_Libraries', 'get_latest_stable_version', fallback=True)

                if get_stable:
                    latest_version = get_latest_stable_version(
                        self._venv_python, self._core_library)
                    version_type = "stable"
                else:
                    # Get all versions and pick latest (including non-stable)
                    all_versions = get_all_versions(
                        self._venv_python, self._core_library)
                    if all_versions:
                        sorted_versions = sorted(
                            all_versions, key=parse_version, reverse=True)
                        latest_version = sorted_versions[0]
                    else:
                        latest_version = None
                    version_type = "latest"

                if latest_version:
                    self._update_checklist_item(
                        "version", f"✓ Latest {version_type}: {latest_version}", "black")
                else:
                    self._update_checklist_item(
                        "version", f"⚠ Unable to detect {version_type}", "orange")
        except Exception:
            self._update_checklist_item(
                "version", "⚠ Unable to detect", "orange")

    def _update_checklist_item(self, key: str, text: str, color: str = "black"):
        """Update a checklist item"""
        if key in self.checklist_labels:
            self.checklist_labels[key].config(text=text, foreground=color)

    # ========================================================================
    # Installation Methods
    # ========================================================================

    def _start_library_installation(self):
        """Start the library installation process"""
        if self._installation_in_progress:
            return

        # Reset completion flag
        self._installation_completed = False

        # Show immediate feedback
        self._append_output("=" * 60)
        self._append_output("🚀 STARTING LIBRARY INSTALLATION")
        self._append_output("=" * 60)
        self._append_output(
            f"📦 Installing libraries: {', '.join(self._all_libraries)}")
        self._append_output(f"🐍 Using Python: {self._venv_python}")

        try:
            # Update UI state
            self._installation_in_progress = True
            self._update_ui_state()
            self._update_checklist_item(
                "installed", "⏳ Installing...", "black")

            # Start worker thread
            self.worker = LibraryInstallationWorker(
                self._venv_python,
                self._all_libraries,
                self.progress_queue,
                self.result_queue
            )
            self.worker.start()

        except Exception as e:
            self._append_output(f"❌ Error starting installation: {e}")
            self._installation_in_progress = False
            self._update_ui_state()

    def _check_queues(self):
        """Check for messages from worker thread"""
        # Process progress messages
        while not self.progress_queue.empty():
            try:
                message = self.progress_queue.get_nowait()
                self._append_output(message)
            except queue.Empty:
                break

        # Check for completion
        if not self.result_queue.empty():
            try:
                # Expect the new tuple: (success, message, report_path, stdout, stderr)
                success, message, report_path, stdout, stderr = self.result_queue.get_nowait()
                self._installation_in_progress = False

                # Save last install report for parsing
                self._last_install_report = report_path
                self._install_output = stdout + "\n" + stderr

                if success:
                    self._handle_installation_success(
                        message, self._install_output)
                else:
                    self._handle_installation_failure(message)
            except queue.Empty:
                pass

        # Continue monitoring
        if self.output_text and self.output_text.winfo_exists():
            self.output_text.master.after(100, self._check_queues)

    def _handle_installation_success(self, message: str, install_output: str = ""):
        """Handle successful library installation"""
        self._append_output(f"\nSuccess: {message}")

        # Update checklist for installation
        self._update_checklist_item("installed", "✅ Installed", "#28a745")

        # Store install output for local index detection
        self._install_output = install_output

        # Verify installation
        self._verify_installation()

    def _handle_installation_failure(self, message: str):
        """Handle failed library installation"""
        self._append_output(f"\nError: {message}")
        self._update_checklist_item("installed", "❌ Failed", "red")
        self._update_ui_state()

    def _verify_installation(self):
        """Verify library installation using pip show"""
        self._append_output("\n" + "=" * 40)
        self._append_output("🔍 VERIFYING INSTALLATION")
        self._append_output("=" * 40)

        try:
            # Check core library with full pip show output
            self._append_output(f"🔍 Running: pip show {self._core_library}")

            # Get and display full pip show output
            process = subprocess.run(
                [str(self._venv_python), "-m", "pip",
                 "show", self._core_library],
                capture_output=True, text=True, timeout=30
            )

            if process.returncode == 0 and process.stdout.strip():
                self._append_output("📝 pip show output:")
                for line in process.stdout.split('\n'):
                    if line.strip():
                        self._append_output(f"   {line}")

                # Extract version from output
                version = None
                for line in process.stdout.split('\n'):
                    if line.startswith('Version:'):
                        version = line.split(':', 1)[1].strip()
                        break

                if version:
                    self._append_output(
                        f"✅ {self._core_library} version: {version}")
                    self._update_checklist_item(
                        "verified", f"✅ Verified v{version}", "#28a745")

                    # Try to detect source from install report first
                    index_info = None
                    try:
                        index_info = self._parse_install_report(
                            self._last_install_report)
                    except Exception:
                        index_info = None

                    if index_info:
                        self._update_checklist_item(
                            "index", f"✅ {index_info}", "#28a745")
                        self._append_output(
                            f"📍 {self._core_library} installed from {index_info}")
                    else:
                        # Fallback to heuristics
                        if detect_local_index(self._venv_python, self._core_library, self._install_output):
                            self._update_checklist_item(
                                "index", "✅ Local index", "#28a745")
                            self._append_output(
                                f"📍 {self._core_library} installed from local index")
                        else:
                            self._update_checklist_item(
                                "index", "✅ PyPI", "#28a745")
                            self._append_output(
                                f"📍 {self._core_library} installed from PyPI")

                    # Mark as completed
                    self._installation_completed = True
                else:
                    self._append_output(
                        f"❌ Could not extract version for {self._core_library}")
                    self._update_checklist_item("verified", "❌ Failed", "red")
            else:
                self._append_output(
                    f"❌ {self._core_library} verification failed")
                if process.stderr:
                    self._append_output(f"   Error: {process.stderr}")
                self._update_checklist_item("verified", "❌ Failed", "red")

            # Check additional libraries with pip show
            for lib in self._additional_libraries:
                self._append_output(f"\n🔍 Running: pip show {lib}")
                lib_process = subprocess.run(
                    [str(self._venv_python), "-m", "pip", "show", lib],
                    capture_output=True, text=True, timeout=30
                )

                if lib_process.returncode == 0 and lib_process.stdout.strip():
                    self._append_output(f"📝 {lib} pip show output:")
                    for line in lib_process.stdout.split('\n'):
                        if line.strip():
                            self._append_output(f"   {line}")
                else:
                    self._append_output(
                        f"⚠ {lib} not found or failed verification")

        except Exception as e:
            self._append_output(f"❌ Verification error: {e}")
            self._update_checklist_item("verified", "❌ Error", "red")

        # Final UI update
        self._update_ui_state()

    def _parse_install_report(self, report_path: Optional[str]) -> Optional[str]:
        """Parse pip --report JSON and try to extract an index URL or host.

        Returns a human-friendly string such as 'PyPI' or 'hostname' or full URL,
        or None if not available.
        """
        if not report_path:
            return None

        try:
            p = Path(report_path)
            logging.debug(f"Library step: Checking pip report file: {p}")
            if not p.exists():
                logging.warning(f"Library step: Pip report file does not exist: {p}")
                return None

            with p.open('r', encoding='utf-8') as fh:
                data = json.load(fh)
        except Exception:
            return None

        # Search for URLs in the JSON dump
        try:
            dump = json.dumps(data)
        except Exception:
            dump = str(data)

        urls = re.findall(r'https?://[^\s"\']+', dump)
        if not urls:
            return None

        # Prefer a non-pypi host if present
        pypi_domains = {'pypi.org', 'files.pythonhosted.org',
                        'test.pypi.org', 'test-files.pythonhosted.org'}
        for u in urls:
            parsed = urlparse(u)
            netloc = parsed.netloc or ''
            if not any(domain in netloc for domain in pypi_domains):
                return netloc or u

        # Fallback: if only pypi urls found, return 'PyPI'
        return 'PyPI'

    def _append_output(self, message: str):
        """Append message to output text area"""
        if self.output_text and self.output_text.winfo_exists():
            self.output_text.insert(tk.END, message + "\n")
            self.output_text.see(tk.END)

    # ========================================================================
    # UI State Methods
    # ========================================================================

    def _update_ui_state(self):
        """Update UI elements based on current state"""
        if self._installation_in_progress:
            self._update_ui_for_progress()
        elif self._installation_completed:
            self._update_ui_for_completed()
        else:
            self._update_ui_for_ready()

    def _update_ui_for_ready(self):
        """Update UI for ready-to-install state"""
        if self.install_button:
            self.install_button.config(
                text="Install Libraries", state="normal")
        if self.progress_bar:
            self.progress_bar.pack_forget()
        if self.output_text:
            self.output_text.pack_forget()

    def _update_ui_for_progress(self):
        """Update UI during installation progress"""
        if self.install_button:
            self.install_button.config(state="disabled")
        if self.progress_bar:
            self.progress_bar.pack(fill="x", pady=(0, 10))
            self.progress_bar.start()
        if self.output_text:
            self.output_text.pack(fill="both", expand=True, pady=(10, 0))

    def _update_ui_for_completed(self):
        """Update UI for completed state"""
        if self.install_button:
            self.install_button.config(
                text="Reinstall Libraries", state="normal")
        if self.progress_bar:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()

        # Notify completion state change
        self.notify_completion_state_changed()


# Alias for backward compatibility
LibraryStep = InstallLibraryStep
