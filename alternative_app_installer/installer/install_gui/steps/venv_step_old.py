
"""
Virtual Environment Creation Step - Creates and configures Python virtual environment using native tkinter

This step handles:
- Creating a Python virtual environment in the installation directory
- Validating Python installation and version compatibility
- Displaying progress and status during venv creation
- Updating shared state with venv information for later steps
- Supporting simulation mode for development/testing
- Uses only native Python libraries (tkinter, threading)
"""
import os
import sys
import subprocess
from pathlib import Path
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

from .base_step import BaseStep


class VenvCreationWorker(threading.Thread):
    """Worker thread for virtual environment creation to avoid blocking UI"""
    
    def __init__(self, python_executable, venv_path, installation_path, progress_queue, result_queue):
        super().__init__()
        self.python_executable = python_executable
        self.venv_path = venv_path
        self.installation_path = installation_path
        self.progress_queue = progress_queue  # Queue for progress messages
        self.result_queue = result_queue      # Queue for final result
        self.daemon = True  # Dies when main thread dies

    def run(self):
        """Execute venv creation in background thread with verbose output"""
        try:
            self.progress_updated.emit(StatusMessages.VENV_INITIALIZING)

            # Check if venv already exists
            venv_path = Path(self.venv_path)
            if venv_path.exists():
                self.progress_updated.emit(StatusMessages.VENV_REMOVING_OLD)
                import shutil
                shutil.rmtree(venv_path)
                self.progress_updated.emit(StatusMessages.VENV_OLD_REMOVED)

            # Create the virtual environment
            self.progress_updated.emit(
                f"{StatusMessages.VENV_CREATING_AT} {venv_path}...")

            # Run venv creation command with verbose output
            cmd = [self.python_executable, '-m',
                   'venv', str(venv_path), '--verbose']

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=self.installation_path,
                bufsize=1,  # Line buffered for real-time output
                universal_newlines=True
            )

            # Monitor process output in real-time
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output.strip():
                    self.progress_updated.emit(f"Output: {output.strip()}")

            # Check if creation was successful
            return_code = process.poll()

            if return_code == 0:
                self.progress_updated.emit(StatusMessages.VENV_VERIFYING)

                # Verify the venv was created successfully
                if self._verify_venv_creation(venv_path):
                    # Upgrade pip with verbose output for better visibility
                    self.progress_updated.emit(
                        StatusMessages.VENV_UPGRADING_PIP)
                    self._upgrade_pip_verbose(venv_path)

                    self.progress_updated.emit(
                        StatusMessages.VENV_READY_COMPLETE)
                    self.finished.emit(
                        True, "Virtual environment created and configured successfully")
                else:
                    self.finished.emit(
                        False, "Virtual environment verification failed")
            else:
                self.finished.emit(
                    False, f"Virtual environment creation failed (exit code: {return_code})")

        except Exception as e:
            self.finished.emit(
                False, f"Error during virtual environment creation: {str(e)}")

    def _upgrade_pip_verbose(self, venv_path: Path):
        """Upgrade pip with verbose output for better user feedback"""
        try:
            # Determine pip executable path
            if os.name == 'nt':  # Windows
                pip_exe = venv_path / 'Scripts' / 'pip.exe'
            else:  # Unix-like
                pip_exe = venv_path / 'bin' / 'pip'

            if not pip_exe.exists():
                self.progress_updated.emit(StatusMessages.VENV_PIP_NOT_FOUND)
                return

            # Run pip upgrade with verbose output
            cmd = [str(pip_exe), 'install', '--upgrade', 'pip', '--verbose']

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output.strip():
                    # Filter out excessive verbosity but keep meaningful updates
                    line = output.strip()
                    if any(keyword in line.lower() for keyword in ['collecting', 'downloading', 'installing', 'successfully']):
                        self.progress_updated.emit(f"Pip: {line}")

            if process.returncode == 0:
                self.progress_updated.emit(StatusMessages.VENV_PIP_UPGRADED)
            else:
                self.progress_updated.emit(StatusMessages.VENV_PIP_WARNINGS)

        except Exception as e:
            self.progress_updated.emit(
                f"{StatusMessages.VENV_PIP_FAILED}: {e}")

    def _verify_venv_creation(self, venv_path: Path) -> bool:
        """Verify that the virtual environment was created correctly"""
        try:
            # Check for essential directories and files
            if os.name == 'nt':  # Windows
                python_exe = venv_path / 'Scripts' / 'python.exe'
                activate_script = venv_path / 'Scripts' / 'activate.bat'
                pip_exe = venv_path / 'Scripts' / 'pip.exe'
            else:  # Unix-like
                python_exe = venv_path / 'bin' / 'python'
                activate_script = venv_path / 'bin' / 'activate'
                pip_exe = venv_path / 'bin' / 'pip'

            # Check if key files exist
            if not all([python_exe.exists(), activate_script.exists()]):
                return False

            # Test that Python executable works
            try:
                result = subprocess.run(
                    [str(python_exe), '--version'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return result.returncode == 0
            except (subprocess.TimeoutExpired, OSError):
                return False

        except Exception:
            return False


class CreateVenvStep(BaseStep):
    """
    Step to create a Python virtual environment for the application.
    """

    def __init__(self, installation_settings, shared_state):
        super().__init__(installation_settings, shared_state)
        self.status_label = None
        self.progress_bar = None
        self.output_text = None
        self.create_button = None
        self.worker = None

        # Venv configuration
        self._venv_name = self._get_venv_directory_name()
        self._venv_path = None
        self._python_executable = None
        self._creation_in_progress = False

    # ========================================================================
    # Required BaseStep Methods
    # ========================================================================

    def get_title(self) -> str:
        """Get the title for this step"""
        return "Setup App Environment"

    def get_description(self) -> str:
        """Get the description for this step"""
        return "Create a dedicated Python virtual environment for the application"

    def get_hint_text(self) -> str:
        """Get hint text for this step"""
        if self._is_simulation_enabled():
            return "Simulation mode: Virtual environment creation will be skipped"
        else:
            return "Click 'Create Environment' to set up the Python virtual environment"

    def can_complete(self) -> bool:
        """Check if step can be completed"""
        # Can complete if venv exists or simulation is enabled
        return self._is_venv_created() or self._is_simulation_enabled()

    def create_widgets(self, parent_widget, layout):
        """Create UI widgets for venv creation"""
        # Status information
        info_label = QLabel(f"Virtual Environment: {self._venv_name}")
        info_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(info_label)

        # Current status display
        self.status_label = QLabel("Ready to create virtual environment")
        apply_status_styling(self.status_label, StatusTypes.INFO)
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Action button
        button_row = QHBoxLayout()
        self.create_button = QPushButton(ButtonLabels.CREATE_ENVIRONMENT)
        self.create_button.clicked.connect(self._start_venv_creation)
        button_row.addWidget(self.create_button)
        button_row.addStretch()
        layout.addLayout(button_row)

        # Output text area (hidden initially, made longer for better visibility)
        self.output_text = QTextEdit()
        # Increased from 150 for better terminal visibility
        self.output_text.setMaximumHeight(300)
        # Set minimum height to ensure visibility
        self.output_text.setMinimumHeight(200)
        self.output_text.setVisible(False)
        self.output_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 9pt;
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
            }
        """)
        layout.addWidget(self.output_text)

        # Initial state check
        self._update_ui_state()

        layout.addStretch()

    def cleanup_widgets(self):
        """Clean up step-specific resources when transitioning away"""
        # Stop any running worker thread
        if self.worker and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait(3000)  # Wait up to 3 seconds for clean shutdown

        # Clear output text to prevent memory buildup
        if self.output_text:
            self.output_text.clear()

        # Reset creation state
        self._creation_in_progress = False

    def complete_step(self) -> bool:
        """Complete the virtual environment creation step"""
        if self._is_simulation_enabled():
            return self._complete_simulation()

        if not self._is_venv_created():
            QMessageBox.warning(
                None,
                DialogTitles.VENV_NOT_CREATED,
                "Please create the virtual environment before proceeding."
            )
            return False

        # Update shared state with ONLY venv_path - everything else can be derived
        try:
            venv_path = self._calculate_venv_path()
            self.update_shared_state("venv_path", str(venv_path))
            self.mark_completed()
            return True

        except Exception as e:
            QMessageBox.critical(
                None,
                DialogTitles.STATE_UPDATE_FAILED,
                f"Failed to update installation state:\n{e}"
            )
            return False

    # ========================================================================
    # Configuration and State Methods
    # ========================================================================

    def _get_venv_directory_name(self) -> str:
        """Get the virtual environment directory name from config"""
        try:
            return self.installation_settings.get(
                'Paths', 'default_venv', fallback='.test_venv')
        except:
            return '.test_venv'

    def _is_simulation_enabled(self) -> bool:
        """Check if simulation mode is enabled for testing"""
        try:
            return self.installation_settings.getboolean(
                'DEV', 'simulate_venv_complete', fallback=False)
        except:
            return False

    def _get_installation_path(self) -> str:
        """Get the installation path from shared state"""
        return self.shared_state.get('valid_installation_path', '')

    def _calculate_venv_path(self) -> Path:
        """Calculate the full path to the virtual environment"""
        install_path = self._get_installation_path()
        if not install_path:
            raise ValueError("Installation path not available")
        return Path(install_path) / self._venv_name

    def _find_python_executable(self) -> str:
        """Find the appropriate Python executable"""
        # Try common Python executables
        candidates = [
            sys.executable,  # Current Python
            'python',
            'python3',
            'py'  # Windows Python Launcher
        ]

        for candidate in candidates:
            if self._validate_python_executable(candidate):
                return candidate

        raise RuntimeError("No suitable Python executable found")

    def _validate_python_executable(self, executable: str) -> bool:
        """Validate that a Python executable is suitable for venv creation"""
        try:
            # Check if executable exists and can run
            result = subprocess.run(
                [executable, '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Check if venv module is available
                venv_result = subprocess.run(
                    [executable, '-m', 'venv', '--help'],
                    capture_output=True,
                    timeout=10
                )
                return venv_result.returncode == 0

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass

        return False

    # ========================================================================
    # Virtual Environment Creation Methods
    # ========================================================================

    def _start_venv_creation(self):
        """Start the virtual environment creation process"""
        if self._creation_in_progress:
            return

        try:
            # Validate prerequisites
            if not self._validate_prerequisites():
                return

            # Prepare for creation
            self._creation_in_progress = True
            self._update_ui_state()

            # Start worker thread
            self._start_worker_thread()

        except Exception as e:
            self._handle_creation_error(f"Failed to start venv creation: {e}")

    def _validate_prerequisites(self) -> bool:
        """Validate that all prerequisites for venv creation are met"""
        # Check installation path
        install_path = self._get_installation_path()
        if not install_path:
            QMessageBox.warning(
                None,
                DialogTitles.MISSING_INSTALLATION_PATH,
                "Installation folder must be selected first."
            )
            return False

        # Check if path exists and is writable
        install_dir = Path(install_path)
        if not install_dir.exists():
            try:
                install_dir.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                QMessageBox.warning(
                    None,
                    DialogTitles.PATH_NOT_ACCESSIBLE,
                    f"Cannot access installation directory:\n{e}"
                )
                return False

        # Find suitable Python executable
        try:
            self._python_executable = self._find_python_executable()
        except RuntimeError as e:
            QMessageBox.warning(
                None,
                DialogTitles.PYTHON_NOT_FOUND,
                f"Cannot find suitable Python installation:\n{e}"
            )
            return False

        # Calculate venv path
        try:
            self._venv_path = self._calculate_venv_path()
        except ValueError as e:
            QMessageBox.warning(None, DialogTitles.INVALID_PATH, str(e))
            return False

        return True

    def _start_worker_thread(self):
        """Start the background worker thread for venv creation"""
        self.worker = VenvCreationWorker(
            self._python_executable,
            str(self._venv_path),
            self._get_installation_path()
        )

        # Connect signals
        self.worker.progress_updated.connect(self._on_progress_update)
        self.worker.finished.connect(self._on_creation_finished)

        # Start the worker
        self.worker.start()

    def _on_progress_update(self, message: str):
        """Handle progress updates from worker thread"""
        self.output_text.append(message)
        self.status_label.setText(message)

    def _on_creation_finished(self, success: bool, message: str):
        """Handle completion of venv creation"""
        self._creation_in_progress = False

        if success:
            self._handle_creation_success(message)
        else:
            self._handle_creation_error(message)

        self._update_ui_state()

        # Clean up worker
        if self.worker:
            self.worker.deleteLater()
            self.worker = None

    # ========================================================================
    # State Management and UI Update Methods
    # ========================================================================

    def _is_venv_created(self) -> bool:
        """Check if virtual environment has been successfully created"""
        if not self._venv_path:
            try:
                self._venv_path = self._calculate_venv_path()
            except ValueError:
                return False

        # Check if venv directory exists and has the expected structure
        venv_dir = Path(self._venv_path)
        if not venv_dir.exists():
            return False

        # Check for essential venv files/directories
        if os.name == 'nt':  # Windows
            python_exe = venv_dir / 'Scripts' / 'python.exe'
            activate_script = venv_dir / 'Scripts' / 'activate.bat'
        else:  # Unix-like
            python_exe = venv_dir / 'bin' / 'python'
            activate_script = venv_dir / 'bin' / 'activate'

        return python_exe.exists() and activate_script.exists()

    def _update_ui_state(self):
        """Update UI elements based on current state"""
        if self._is_simulation_enabled():
            self._update_ui_for_simulation()
        elif self._creation_in_progress:
            self._update_ui_for_progress()
        elif self._is_venv_created():
            self._update_ui_for_completed()
        else:
            self._update_ui_for_ready()

    def _update_ui_for_simulation(self):
        """Update UI for simulation mode"""
        self.status_label.setText(StatusMessages.VENV_SIMULATION)
        apply_status_styling(self.status_label, StatusTypes.INFO)
        self.create_button.setText("Skip (Simulation)")
        self.create_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.output_text.setVisible(False)

    def _update_ui_for_ready(self):
        """Update UI for ready-to-create state"""
        self.status_label.setText(StatusMessages.VENV_READY)
        apply_status_styling(self.status_label, StatusTypes.INFO)
        self.create_button.setText(ButtonLabels.CREATE_ENVIRONMENT)
        self.create_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.output_text.setVisible(False)

    def _update_ui_for_progress(self):
        """Update UI during creation progress"""
        self.status_label.setText(StatusMessages.VENV_CREATING)
        apply_status_styling(self.status_label, StatusTypes.INFO)
        self.create_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.output_text.setVisible(True)

    def _update_ui_for_completed(self):
        """Update UI for completed state"""
        self.status_label.setText(StatusMessages.VENV_CREATED)
        apply_status_styling(self.status_label, StatusTypes.SUCCESS)
        self.create_button.setText("Recreate Environment")
        self.create_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.output_text.setVisible(True)

    # ========================================================================
    # Completion and Error Handling Methods
    # ========================================================================

    def _handle_creation_success(self, message: str):
        """Handle successful venv creation"""
        self.output_text.append(f"\nSuccess: {message}")
        self.status_label.setText(StatusMessages.VENV_CREATED)
        apply_status_styling(self.status_label, StatusTypes.SUCCESS)

    def _handle_creation_error(self, error_message: str):
        """Handle venv creation errors"""
        self.output_text.append(f"\nError: {error_message}")
        self.status_label.setText(StatusMessages.VENV_FAILED)
        apply_status_styling(self.status_label, StatusTypes.ERROR)

        QMessageBox.critical(
            None,
            DialogTitles.VENV_CREATION_FAILED,
            f"Failed to create virtual environment:\n\n{error_message}"
        )

    def _complete_simulation(self) -> bool:
        """Complete the step in simulation mode"""
        # Simulate venv creation for development/testing
        try:
            fake_venv_path = self._calculate_venv_path()
            self.update_shared_state("venv_path", str(fake_venv_path))
            self.mark_completed()
            return True
        except Exception as e:
            QMessageBox.critical(
                None,
                DialogTitles.STATE_UPDATE_FAILED,
                f"Failed to simulate venv creation:\n{e}"
            )
            return False


# Alias for backward compatibility
VenvStep = CreateVenvStep
