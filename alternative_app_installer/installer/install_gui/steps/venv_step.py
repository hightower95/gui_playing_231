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
        self.venv_path = Path(venv_path)  # Ensure it's a Path object
        self.installation_path = installation_path
        self.progress_queue = progress_queue  # Queue for progress messages
        self.result_queue = result_queue      # Queue for final result
        self.daemon = True  # Dies when main thread dies

    def run(self):
        """Execute venv creation following user requirements:
        1. If venv exists and works, skip creation
        2. Only create venv if needed 
        3. Always verify with 'pip show pip' before claiming success
        """
        try:
            self.progress_queue.put("🔄 Worker thread started successfully")
            self.progress_queue.put("🔧 Checking virtual environment status...")
            self.progress_queue.put(f"📍 Target location: {self.venv_path}")
            self.progress_queue.put(
                f"🐍 Python executable: {self.python_executable}")

            # Step 1: Check if venv already exists and is functional
            if self.venv_path.exists():
                self.progress_queue.put(
                    "📁 Virtual environment directory found")
                self.progress_queue.put(
                    "🔍 Testing existing virtual environment...")

                if self._test_existing_venv():
                    self.progress_queue.put(
                        "✅ Existing virtual environment is working perfectly!")
                    self.progress_queue.put(
                        "⏩ Skipping creation - using existing environment")
                    self.result_queue.put(
                        (True, "Existing virtual environment verified and ready"))
                    return
                else:
                    self.progress_queue.put(
                        "⚠️ Existing virtual environment is not functional")
                    self.progress_queue.put(
                        "🗑️ Removing broken virtual environment...")
                    self._remove_broken_venv()

            # Step 2: Create new virtual environment
            self.progress_queue.put("🏗️ Creating new virtual environment...")
            self.progress_queue.put(
                f"📁 Absolute path: {self.venv_path.resolve()}")

            if not self._create_venv():
                self.progress_queue.put(
                    "❌ Virtual environment creation failed")
                self.result_queue.put(
                    (False, "Failed to create virtual environment"))
                return

            # Step 3: Verify the new venv works before claiming success
            self.progress_queue.put(
                "� Verifying newly created virtual environment...")
            if self._test_existing_venv():
                self.progress_queue.put(
                    "🎉 Virtual environment created and verified successfully!")
                self.result_queue.put(
                    (True, "Virtual environment created and configured successfully"))
            else:
                self.progress_queue.put(
                    "❌ Virtual environment was created but is not functional")
                self.result_queue.put(
                    (False, "Virtual environment created but failed verification"))

        except Exception as e:
            self.progress_queue.put(
                f"� Error during virtual environment creation: {e}")
            self.result_queue.put(
                (False, f"Error during virtual environment creation: {e}"))

    def _test_existing_venv(self):
        """Test if existing virtual environment is functional using 'pip show pip'"""
        try:
            # Get the python executable path from the venv
            if sys.platform.startswith('win'):
                venv_python = self.venv_path / "Scripts" / "python.exe"
            else:
                venv_python = self.venv_path / "bin" / "python"

            if not venv_python.exists():
                self.progress_queue.put(
                    "❌ Virtual environment python executable not found")
                return False

            self.progress_queue.put(
                "🧪 Running 'pip show pip' to test venv functionality...")
            self.progress_queue.put(
                f"▶️ Command: {str(venv_python)} -m pip show pip")

            # Run pip show pip to verify the venv works
            result = subprocess.run(
                [str(venv_python), "-m", "pip", "show", "pip"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.installation_path
            )

            # Show the pip output to the user
            self.progress_queue.put("=" * 40)
            self.progress_queue.put("📄 pip show pip output:")
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        self.progress_queue.put(f"   {line}")

            if result.stderr:
                self.progress_queue.put("⚠️ Error output:")
                for line in result.stderr.strip().split('\n'):
                    if line.strip():
                        self.progress_queue.put(f"   {line}")

            self.progress_queue.put("=" * 40)
            self.progress_queue.put(f"📊 Return code: {result.returncode}")

            if result.returncode == 0 and "Name: pip" in result.stdout:
                self.progress_queue.put(
                    "✅ Virtual environment pip test successful")
                return True
            else:
                self.progress_queue.put(
                    f"❌ Virtual environment pip test failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.progress_queue.put("❌ Virtual environment test timed out")
            return False
        except Exception as e:
            self.progress_queue.put(
                f"❌ Error testing virtual environment: {e}")
            return False

    def _remove_broken_venv(self):
        """Remove a broken virtual environment with Windows-compatible permissions handling"""
        try:
            import shutil
            import stat
            import os

            # Windows-specific: Handle read-only files that can't be deleted
            def handle_remove_readonly(func, path, exc):
                """Error handler for removing read-only files on Windows"""
                if os.path.exists(path):
                    os.chmod(path, stat.S_IWRITE)
                    func(path)

            shutil.rmtree(self.venv_path, onerror=handle_remove_readonly)
            self.progress_queue.put("✅ Broken virtual environment removed")
        except Exception as e:
            self.progress_queue.put(
                f"⚠️ Warning: Could not fully remove broken environment: {e}")

    def _create_venv(self):
        """Create a new virtual environment"""
        try:
            # Use --clear flag to ensure clean creation
            cmd = [self.python_executable, '-m',
                   'venv', '--clear', str(self.venv_path)]

            self.progress_queue.put(f"▶️ Running command: {' '.join(cmd)}")
            self.progress_queue.put("=" * 60)

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=self.installation_path
            )

            stdout, _ = process.communicate(timeout=180)

            if process.returncode == 0:
                self.progress_queue.put(
                    "✅ Virtual environment creation completed")
                return True
            else:
                self.progress_queue.put(
                    f"❌ Virtual environment creation failed with code: {process.returncode}")
                if stdout:
                    self.progress_queue.put(f"Output: {stdout}")
                return False

        except subprocess.TimeoutExpired:
            self.progress_queue.put("❌ Virtual environment creation timed out")
            return False
        except Exception as e:
            self.progress_queue.put(
                f"💥 Error creating virtual environment: {e}")
            return False

            # Check if venv already exists
            # Remove existing venv if it exists with Windows-compatible permissions handling
            if self.venv_path.exists():
                self.progress_queue.put(
                    "🗑️ Removing existing virtual environment...")
                import shutil
                import stat
                import os

                try:
                    # Windows-specific: Handle read-only files that can't be deleted
                    def handle_remove_readonly(func, path, exc):
                        """Error handler for removing read-only files on Windows"""
                        if os.path.exists(path):
                            os.chmod(path, stat.S_IWRITE)
                            func(path)

                    shutil.rmtree(self.venv_path,
                                  onerror=handle_remove_readonly)
                    self.progress_queue.put("✅ Existing environment removed")
                except Exception as e:
                    self.progress_queue.put(
                        f"⚠️ Warning: Could not fully remove existing environment: {e}")
                    self.progress_queue.put(
                        "📝 Using --clear flag to ensure clean creation")

            # Create the virtual environment with --clear flag for robust creation
            self.progress_queue.put(f"🏗️ Creating virtual environment...")
            self.progress_queue.put(
                f"📁 Absolute path: {self.venv_path.resolve()}")

            # Use --clear flag to ensure clean creation even if removal failed
            cmd = [self.python_executable, '-m',
                   'venv', '--clear', str(self.venv_path)]

            self.progress_queue.put(f"▶️ Running command: {' '.join(cmd)}")
            self.progress_queue.put("=" * 60)

            self.progress_queue.put("🚀 Starting subprocess...")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=self.installation_path,
                bufsize=1,  # Line buffered for real-time output
                universal_newlines=True
            )
            self.progress_queue.put(
                f"📋 Process started with PID: {process.pid}")

            # Monitor process output in real-time with timeout (Windows-compatible)
            import time

            # 3 minutes timeout for venv creation (increased for Windows)
            timeout_seconds = 180
            start_time = time.time()
            output_lines = []

            while True:
                # Check if process has finished
                return_code = process.poll()
                if return_code is not None:
                    self.progress_queue.put(
                        f"📊 Process finished with return code: {return_code}")
                    break

                # Check for timeout
                elapsed = time.time() - start_time
                if elapsed > timeout_seconds:
                    self.progress_queue.put(
                        "⏰ Timeout reached, terminating process...")
                    process.terminate()
                    try:
                        # Give 5 seconds to terminate gracefully
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()  # Force kill if needed
                    self.result_queue.put(
                        (False, "Virtual environment creation timed out"))
                    return

                # Show progress every 5 seconds
                if int(elapsed) % 5 == 0 and elapsed > 0:
                    self.progress_queue.put(
                        f"⏳ Still running... ({int(elapsed)}s elapsed)")

                # Small delay to prevent tight loop
                time.sleep(1)

            # Get all output after process completes
            try:
                stdout, stderr = process.communicate(timeout=10)
                if stdout:
                    self.progress_queue.put("📜 Process output:")
                    for line in stdout.strip().split('\n'):
                        if line.strip():
                            self.progress_queue.put(f"  {line.strip()}")
                if stderr:
                    self.progress_queue.put("⚠️ Process errors:")
                    for line in stderr.strip().split('\n'):
                        if line.strip():
                            self.progress_queue.put(f"  {line.strip()}")
            except subprocess.TimeoutExpired:
                self.progress_queue.put(
                    "⚠️ Warning: Process cleanup timed out")
                process.kill()

            # Check if creation was successful
            return_code = process.poll()

            if return_code == 0:
                self.progress_queue.put("=" * 60)
                self.progress_queue.put(
                    "✅ VIRTUAL ENVIRONMENT CREATED SUCCESSFULLY")
                self.progress_queue.put("Verifying virtual environment...")

                # Verify the venv was created successfully
                if self._verify_venv_creation(self.venv_path):
                    # Test pip functionality to ensure venv is working properly
                    self.progress_queue.put("Testing pip functionality...")
                    self._test_pip_functionality(self.venv_path)

                    self.progress_queue.put("🎉 Virtual environment ready!")
                    self.result_queue.put(
                        (True, "Virtual environment created and configured successfully"))
                else:
                    self.result_queue.put(
                        (False, "Virtual environment verification failed"))
            else:
                self.result_queue.put(
                    (False, f"Virtual environment creation failed (exit code: {return_code})"))

        except Exception as e:
            self.result_queue.put(
                (False, f"Error during virtual environment creation: {str(e)}"))

    def _test_pip_functionality(self, venv_path: Path):
        """Test pip functionality to verify the virtual environment is working properly"""
        try:
            # Determine pip executable path
            if os.name == 'nt':  # Windows
                pip_exe = venv_path / 'Scripts' / 'pip.exe'
            else:  # Unix-like
                pip_exe = venv_path / 'bin' / 'pip'

            if not pip_exe.exists():
                self.progress_queue.put(
                    "❌ Pip executable not found - venv may be corrupted")
                return

            # Test 1: Check pip version
            self.progress_queue.put("🔍 Testing pip version...")
            version_cmd = [str(pip_exe), '--version']

            try:
                version_result = subprocess.run(
                    version_cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if version_result.returncode == 0:
                    self.progress_queue.put(
                        f"✅ Pip version: {version_result.stdout.strip()}")
                else:
                    self.progress_queue.put(
                        "❌ Pip version check failed - venv may be corrupted")
                    return
            except subprocess.TimeoutExpired:
                self.progress_queue.put(
                    "❌ Pip version check timed out - venv may be corrupted")
                return
            except Exception as e:
                self.progress_queue.put(f"❌ Pip version check error: {e}")
                return

            # Test 2: Use 'pip show pip' to verify pip package itself is installed
            self.progress_queue.put("🔍 Verifying pip package installation...")
            show_cmd = [str(pip_exe), 'show', 'pip']

            try:
                show_result = subprocess.run(
                    show_cmd,
                    capture_output=True,
                    text=True,
                    timeout=15
                )

                if show_result.returncode == 0 and show_result.stdout.strip():
                    # Extract key info from pip show output
                    lines = show_result.stdout.strip().split('\n')
                    # Show first few lines (Name, Version, Summary)
                    for line in lines[:3]:
                        if line.strip():
                            self.progress_queue.put(f"✅ {line.strip()}")
                    self.progress_queue.put(
                        "✅ Pip package verification successful")
                else:
                    self.progress_queue.put(
                        "❌ Pip show command failed - venv may be corrupted")
                    self.progress_queue.put(
                        f"   Return code: {show_result.returncode}")
                    if show_result.stderr:
                        self.progress_queue.put(
                            f"   Error: {show_result.stderr.strip()}")
                    return

            except subprocess.TimeoutExpired:
                self.progress_queue.put(
                    "❌ Pip show command timed out - venv may be corrupted")
                return
            except Exception as e:
                self.progress_queue.put(f"❌ Pip show command error: {e}")
                return

            # Test 3: List installed packages to verify pip environment is functional
            self.progress_queue.put("🔍 Checking installed packages...")
            list_cmd = [str(pip_exe), 'list', '--format=columns']

            try:
                list_result = subprocess.run(
                    list_cmd,
                    capture_output=True,
                    text=True,
                    timeout=15
                )

                if list_result.returncode == 0:
                    lines = list_result.stdout.strip().split('\n')
                    if len(lines) >= 2:  # Header + at least one package
                        package_count = len(lines) - 2  # Subtract header lines
                        self.progress_queue.put(
                            f"✅ Found {package_count} installed packages")
                        # Show first few packages as examples
                        for line in lines[:4]:  # Header + first 2 packages
                            if line.strip():
                                self.progress_queue.put(f"   {line.strip()}")
                    else:
                        self.progress_queue.put(
                            "⚠️  No packages listed - minimal venv installation")
                else:
                    self.progress_queue.put("❌ Package listing failed")
                    return

            except subprocess.TimeoutExpired:
                self.progress_queue.put("❌ Package listing timed out")
                return
            except Exception as e:
                self.progress_queue.put(f"❌ Package listing error: {e}")
                return

            self.progress_queue.put("=" * 60)
            self.progress_queue.put(
                "✅ ALL PIP TESTS PASSED - VIRTUAL ENVIRONMENT IS FUNCTIONAL")
            self.progress_queue.put("=" * 60)

        except Exception as e:
            self.progress_queue.put(
                f"❌ ERROR during pip functionality test: {e}")
            self.progress_queue.put(
                "⚠️  Virtual environment may not be fully functional")

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
    Uses native tkinter for UI components.
    """

    def __init__(self, installation_settings, shared_state):
        super().__init__(installation_settings, shared_state)

        # UI components
        self.status_label = None
        self.progress_bar = None
        self.output_text = None
        self.create_button = None

        # Worker thread and queues
        self.worker = None
        self.progress_queue = queue.Queue()
        self.result_queue = queue.Queue()

        # Venv configuration
        self._venv_name = self._get_venv_directory_name()
        self._venv_path = None
        self._python_executable = None
        self._creation_in_progress = False
        # Track if verification has been completed this session
        self._verification_completed = False

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
        """Check if step can be completed - only after venv is created AND verified"""
        # Can complete if venv exists AND has been verified, or simulation is enabled
        return (self._is_venv_created() and self.is_completed()) or self._is_simulation_enabled()

    def create_widgets(self, parent_frame: tk.Frame):
        """Create UI widgets for venv creation using tkinter"""
        # Status information
        info_label = ttk.Label(parent_frame, text=f"Virtual Environment: {self._venv_name}",
                               font=("Arial", 10, "bold"))
        info_label.pack(pady=(0, 10))

        # Current status display
        self.status_label = ttk.Label(
            parent_frame, text="⏳ Virtual environment not created yet - Complete Step button disabled")
        self.status_label.pack(pady=(0, 10))

        # Progress bar
        self.progress_bar = ttk.Progressbar(parent_frame, mode='indeterminate')
        self.progress_bar.pack(fill="x", pady=(0, 10))
        self.progress_bar.pack_forget()  # Hidden initially

        # Action button
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(fill="x", pady=(0, 10))

        self.create_button = ttk.Button(button_frame, text="Create Environment",
                                        command=self._start_venv_creation)
        self.create_button.pack(side="left")

        # Output text area (hidden initially, made longer for better visibility)
        self.output_text = scrolledtext.ScrolledText(parent_frame, height=15, width=80,
                                                     font=("Courier New", 9),
                                                     bg="#1e1e1e", fg="#d4d4d4",
                                                     insertbackground="#d4d4d4")
        self.output_text.pack(fill="both", expand=True, pady=(10, 0))
        self.output_text.pack_forget()  # Hidden initially

        # Initial state check
        self._update_ui_state()

        # Start monitoring queues
        parent_frame.after(100, self._check_queues)

    def cleanup_widgets(self):
        """Clean up step-specific resources when transitioning away"""
        # Stop any running worker thread
        if self.worker and self.worker.is_alive():
            # We can't force kill the thread, but we can clean up
            self.worker = None

        # DON'T clear output text - preserve the log for user review
        # The output text provides valuable feedback about what happened
        # and should persist until the user moves to a different step

        # Reset creation state
        self._creation_in_progress = False

    def complete_step(self) -> bool:
        """Complete the virtual environment creation step"""
        if self._is_simulation_enabled():
            return self._complete_simulation()

        if not self._is_venv_created():
            messagebox.showwarning(
                "Virtual Environment Not Created",
                "Please create the virtual environment before proceeding."
            )
            return False

        # Update shared state with ONLY venv_path - everything else can be derived
        try:
            venv_path = self._calculate_venv_path()
            self.update_shared_state("venv_path", str(venv_path))
            # Don't mark completed here - only mark completed after verification in _handle_creation_success
            return True

        except Exception as e:
            messagebox.showerror(
                "State Update Failed",
                f"Failed to update installation state:\n{e}"
            )
            return False

    def _append_output(self, text: str):
        """Append text to the output widget for immediate user feedback"""
        if self.output_text:
            self.output_text.insert(tk.END, text + "\n")
            self.output_text.see(tk.END)  # Auto-scroll to bottom
            self.output_text.update()  # Force immediate update

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
        """Check if simulation mode is enabled"""
        try:
            return self.installation_settings.getboolean(
                'DEV', 'simulate_venv_complete', fallback=False)
        except:
            return False

    def _get_installation_path(self) -> str:
        """Get the installation path from shared state"""
        install_path = self.get_shared_state("valid_installation_path", None)

        if install_path is None:
            raise ValueError("Installation path not set in shared state")
        return install_path

    def _calculate_venv_path(self) -> Path:
        """Calculate the full path to the virtual environment directory"""
        install_path = self._get_installation_path()
        if not install_path:
            raise ValueError("Installation path not set")

        return Path(install_path) / self._venv_name

    def _find_python_executable(self) -> str:
        """Find suitable Python executable for venv creation"""
        # Try current Python executable first
        python_exe = sys.executable
        if self._test_python_executable(python_exe):
            return python_exe

        # Try common Python names
        for name in ['python', 'python3', 'py']:
            try:
                result = subprocess.run(
                    [name, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return name
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

        raise RuntimeError("No suitable Python installation found")

    def _test_python_executable(self, python_exe: str) -> bool:
        """Test if a Python executable can create virtual environments"""
        try:
            # Test that venv module is available
            venv_result = subprocess.run(
                [python_exe, '-m', 'venv', '--help'],
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

        # Reset verification flag when starting new creation/verification
        self._verification_completed = False

        # Show immediate feedback in terminal
        self._append_output("=" * 60)
        self._append_output("🚀 STARTING VIRTUAL ENVIRONMENT CREATION")
        self._append_output("=" * 60)

        try:
            # Validate prerequisites
            if not self._validate_prerequisites():
                self._append_output("❌ Prerequisites validation failed")
                return

            # Show the absolute path that will be created
            self._append_output(f"📁 Virtual environment will be created at:")
            self._append_output(f"   {self._venv_path}")
            self._append_output(
                f"🐍 Using Python executable: {self._python_executable}")
            self._append_output("")

            # Prepare for creation
            self._creation_in_progress = True
            self._update_ui_state()

            # Start worker thread
            self._start_worker_thread()

        except Exception as e:
            self._handle_creation_error(f"Failed to start venv creation: {e}")
            self._append_output(f"❌ ERROR: {e}")

    def _validate_prerequisites(self) -> bool:
        """Validate that all prerequisites for venv creation are met"""
        # Check installation path
        install_path = self._get_installation_path()
        if not install_path:
            messagebox.showwarning(
                "Missing Installation Path",
                "Installation folder must be selected first."
            )
            return False

        # Check if path exists and is writable
        install_dir = Path(install_path)
        if not install_dir.exists():
            try:
                install_dir.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                messagebox.showwarning(
                    "Path Not Accessible",
                    f"Cannot access installation directory:\n{e}"
                )
                return False

        # Find suitable Python executable
        try:
            self._python_executable = self._find_python_executable()
        except RuntimeError as e:
            messagebox.showwarning(
                "Python Not Found",
                f"Cannot find suitable Python installation:\n{e}"
            )
            return False

        # Calculate venv path
        try:
            self._venv_path = self._calculate_venv_path()
        except ValueError as e:
            messagebox.showwarning("Invalid Path", str(e))
            return False

        return True

    def _start_worker_thread(self):
        """Start the background worker thread for venv creation"""
        try:
            self.worker = VenvCreationWorker(
                self._python_executable,
                str(self._venv_path),
                self._get_installation_path(),
                self.progress_queue,
                self.result_queue
            )

            # Start the worker
            self.worker.start()
            self._append_output(
                f"🔄 Worker thread started (Thread ID: {self.worker.ident})")

            # Ensure queue checking starts
            if self.status_label:
                self.status_label.after(100, self._check_queues)
                self._append_output("📡 Queue monitoring started")

        except Exception as e:
            self._append_output(f"❌ Failed to start worker thread: {e}")
            self._handle_creation_error(f"Worker thread failed: {e}")

    def _check_queues(self):
        """Check for messages from worker thread"""
        try:
            # Check for progress messages
            while True:
                try:
                    message = self.progress_queue.get_nowait()
                    self._on_progress_update(message)
                except queue.Empty:
                    break

            # Check for result
            try:
                success, message = self.result_queue.get_nowait()
                self._on_creation_finished(success, message)
            except queue.Empty:
                pass

        except Exception as e:
            print(f"Error checking queues: {e}")

        # Schedule next check if still in progress
        if self._creation_in_progress and self.status_label:
            self.status_label.after(100, self._check_queues)

    def _on_progress_update(self, message: str):
        """Handle progress updates from worker thread"""
        if self.output_text:
            self.output_text.insert(tk.END, message + "\n")
            self.output_text.see(tk.END)

        if self.status_label:
            self.status_label.config(text=message)

    def _on_creation_finished(self, success: bool, message: str):
        """Handle completion of venv creation"""
        self._creation_in_progress = False

        if success:
            self._handle_creation_success(message)
        else:
            self._handle_creation_error(message)

        self._update_ui_state()

        # Clean up worker
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
        elif self._verification_completed:
            self._update_ui_for_completed()
        else:
            self._update_ui_for_ready()

    def _update_ui_for_simulation(self):
        """Update UI for simulation mode"""
        if self.status_label:
            self.status_label.config(
                text="Simulation mode - venv creation will be skipped")
        if self.create_button:
            self.create_button.config(text="Skip (Simulation)", state="normal")
        if self.progress_bar:
            self.progress_bar.pack_forget()
        if self.output_text:
            self.output_text.pack_forget()

    def _update_ui_for_ready(self):
        """Update UI for ready-to-create state"""
        # Check if there's an existing venv directory (even if not verified)
        venv_path = self._calculate_venv_path()
        venv_exists = Path(venv_path).exists()

        if self.status_label:
            if venv_exists:
                # Venv directory exists but hasn't been verified yet
                self.status_label.config(
                    text="Virtual environment found - needs verification",
                    foreground="black")  # Black text for unverified state
            else:
                # No venv directory found
                self.status_label.config(
                    text="⏳ Ready to create virtual environment - Complete Step button disabled until verification",
                    foreground="black")  # Default black text

        if self.create_button:
            button_text = "Verify Environment" if venv_exists else "Create Environment"
            self.create_button.config(
                text=button_text, state="normal")
        if self.progress_bar:
            self.progress_bar.pack_forget()
        if self.output_text:
            self.output_text.pack_forget()

    def _update_ui_for_progress(self):
        """Update UI during creation progress"""
        if self.status_label:
            self.status_label.config(
                text="⏳ Creating and verifying virtual environment... Complete Step button disabled",
                foreground="black")  # Reset to black during progress
        if self.create_button:
            self.create_button.config(state="disabled")
        if self.progress_bar:
            self.progress_bar.pack(fill="x", pady=(0, 10))
            self.progress_bar.start()  # Start animation
        if self.output_text:
            self.output_text.pack(fill="both", expand=True, pady=(10, 0))

    def _update_ui_for_completed(self):
        """Update UI for completed state"""
        if self.status_label:
            self.status_label.config(
                text="✅ Virtual environment created and verified! Complete Step button enabled",
                foreground="#28a745")  # Green text color
        if self.create_button:
            self.create_button.config(
                text="Setup Environment", state="normal")
        if self.progress_bar:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
        if self.output_text:
            self.output_text.pack(fill="both", expand=True, pady=(10, 0))

    # ========================================================================
    # Completion and Error Handling Methods
    # ========================================================================

    def _handle_creation_success(self, message: str):
        """Handle successful venv creation"""
        # Set verification completed flag
        self._verification_completed = True

        if self.output_text:
            self.output_text.insert(tk.END, f"\nSuccess: {message}\n")
            self.output_text.see(tk.END)
        if self.status_label:
            self.status_label.config(
                text="Virtual environment created and verified successfully! ✅",
                foreground="#28a745")  # Green text color

        # Mark as completed - this will trigger the callback automatically
        self.mark_completed()

        # Update the local UI state
        self._update_ui_for_completed()

    def _handle_creation_error(self, error_message: str):
        """Handle venv creation errors"""
        if self.output_text:
            self.output_text.insert(tk.END, f"\nError: {error_message}\n")
            self.output_text.see(tk.END)
        if self.status_label:
            self.status_label.config(
                text="Virtual environment creation failed")

        messagebox.showerror(
            "Virtual Environment Creation Failed",
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
            messagebox.showerror(
                "State Update Failed",
                f"Failed to simulate venv creation:\n{e}"
            )
            return False


# Alias for backward compatibility
VenvStep = CreateVenvStep
