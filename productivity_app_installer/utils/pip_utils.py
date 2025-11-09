"""
Pip Installation Utilities
Provides user feedback and progress tracking for pip installations
"""
import subprocess
import threading
import time
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any
import tkinter as tk
from tkinter import ttk


class PipInstallationProgress:
    """
    Manages pip installation with real-time progress feedback
    """

    def __init__(self, logger_func: Optional[Callable[[str, str], None]] = None):
        """
        Initialize pip installation progress manager

        Args:
            logger_func: Function to log messages (message, level)
        """
        self.logger = logger_func or self._default_logger
        self.is_running = False
        self.current_process = None

    def _default_logger(self, message: str, level: str = "info"):
        """Default logger that prints to console"""
        print(f"[{level.upper()}] {message}")

    def install_with_progress(
        self,
        python_path: Path,
        packages: List[str],
        progress_callback: Optional[Callable[[str], None]] = None,
        index_url: Optional[str] = None,
        timeout: int = 300,
        show_console: bool = False
    ) -> Dict[str, Any]:
        """
        Install packages with progress feedback

        Args:
            python_path: Path to Python executable
            packages: List of package names/paths to install
            progress_callback: Function to call with progress updates
            index_url: Custom index URL (if any)
            timeout: Installation timeout in seconds
            show_console: Whether to show console window

        Returns:
            Dict with installation results
        """
        if self.is_running:
            return {"success": False, "error": "Installation already in progress"}

        self.is_running = True

        try:
            # Build pip command
            cmd = [str(python_path), "-m", "pip", "install", "--verbose"]

            if index_url:
                cmd.extend(["--index-url", index_url])

            cmd.extend(packages)

            self.logger(f"Starting pip installation: {' '.join(cmd)}")

            if progress_callback:
                progress_callback("Starting installation...")

            # Set up subprocess flags
            creation_flags = 0 if show_console else 0x08000000  # CREATE_NO_WINDOW

            # Start the installation process
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=creation_flags,
                bufsize=1,
                universal_newlines=True
            )

            # Monitor output in real-time
            output_lines = []

            while True:
                output = self.current_process.stdout.readline()
                if output == '' and self.current_process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    output_lines.append(line)
                    self.logger(f"PIP: {line}")

                    # Extract progress information for user feedback
                    if progress_callback:
                        progress_message = self._extract_progress_message(line)
                        if progress_message:
                            progress_callback(progress_message)

            # Get final return code
            return_code = self.current_process.poll()

            result = {
                "success": return_code == 0,
                "return_code": return_code,
                "output": output_lines,
                "command": cmd
            }

            if return_code == 0:
                self.logger("Installation completed successfully")
                if progress_callback:
                    progress_callback("Installation completed successfully!")
            else:
                error_msg = f"Installation failed with return code {return_code}"
                self.logger(error_msg, "error")
                result["error"] = error_msg
                if progress_callback:
                    progress_callback(f"Installation failed: {error_msg}")

            return result

        except subprocess.TimeoutExpired:
            if self.current_process:
                self.current_process.kill()
            error_msg = f"Installation timed out after {timeout} seconds"
            self.logger(error_msg, "error")
            if progress_callback:
                progress_callback(error_msg)
            return {"success": False, "error": error_msg}

        except Exception as e:
            error_msg = f"Installation error: {str(e)}"
            self.logger(error_msg, "error")
            if progress_callback:
                progress_callback(error_msg)
            return {"success": False, "error": error_msg}

        finally:
            self.is_running = False
            self.current_process = None

    def _extract_progress_message(self, pip_output: str) -> Optional[str]:
        """
        Extract user-friendly progress messages from pip output

        Args:
            pip_output: Raw pip output line

        Returns:
            User-friendly progress message or None
        """
        line = pip_output.lower()

        # Common pip progress indicators
        if "collecting" in line:
            return f"Collecting dependencies..."
        elif "downloading" in line:
            if "%" in pip_output:
                return f"Downloading packages..."
            else:
                return "Downloading packages..."
        elif "installing collected packages" in line:
            return "Installing packages..."
        elif "successfully installed" in line:
            return "Installation completed!"
        elif "running setup.py" in line:
            return "Building package..."
        elif "building wheel" in line:
            return "Building package wheel..."
        elif "requirement already satisfied" in line:
            return "Checking existing packages..."
        elif "using cached" in line:
            return "Using cached packages..."

        # Extract package names being processed
        if "collecting" in line and " " in pip_output:
            try:
                package_name = pip_output.split()[1]
                return f"Collecting {package_name}..."
            except:
                pass

        return None

    def cancel_installation(self):
        """Cancel the current installation if running"""
        if self.is_running and self.current_process:
            self.logger("Canceling installation...", "warning")
            self.current_process.terminate()
            # Give it a moment to terminate gracefully
            time.sleep(1)
            if self.current_process.poll() is None:
                self.current_process.kill()
            self.is_running = False


class TkinterPipProgress:
    """
    Tkinter-specific pip installation with progress bar and status updates
    """

    def __init__(self, parent_widget, logger_func: Optional[Callable[[str, str], None]] = None):
        """
        Initialize Tkinter pip progress

        Args:
            parent_widget: Parent Tkinter widget
            logger_func: Function to log messages
        """
        self.parent = parent_widget
        self.pip_manager = PipInstallationProgress(logger_func)
        self.progress_bar = None
        self.status_label = None
        self.cancel_button = None

    def create_progress_ui(self) -> tuple:
        """
        Create progress UI elements

        Returns:
            Tuple of (progress_bar, status_label, cancel_button)
        """
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self.parent,
            mode='indeterminate',
            length=300
        )

        # Status label
        self.status_label = ttk.Label(
            self.parent,
            text="Preparing installation...",
            foreground="blue"
        )

        # Cancel button
        self.cancel_button = ttk.Button(
            self.parent,
            text="Cancel Installation",
            command=self._cancel_installation,
            state=tk.DISABLED
        )

        return self.progress_bar, self.status_label, self.cancel_button

    def install_with_ui_feedback(
        self,
        python_path: Path,
        packages: List[str],
        completion_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        **kwargs
    ):
        """
        Install packages with UI feedback

        Args:
            python_path: Path to Python executable
            packages: List of packages to install
            completion_callback: Called when installation completes
            **kwargs: Additional arguments for install_with_progress
        """
        if self.progress_bar:
            self.progress_bar.start(10)

        if self.cancel_button:
            self.cancel_button.config(state=tk.NORMAL)

        def progress_update(message: str):
            """Update UI with progress message"""
            if self.status_label:
                self.status_label.config(text=message)
                self.parent.update_idletasks()

        def run_installation():
            """Run installation in background thread"""
            result = self.pip_manager.install_with_progress(
                python_path=python_path,
                packages=packages,
                progress_callback=progress_update,
                **kwargs
            )

            # Update UI on completion
            self.parent.after(0, lambda: self._installation_complete(
                result, completion_callback))

        # Start installation in background thread
        thread = threading.Thread(target=run_installation, daemon=True)
        thread.start()

    def _installation_complete(self, result: Dict[str, Any], completion_callback: Optional[Callable] = None):
        """Handle installation completion on main thread"""
        # Stop progress bar
        if self.progress_bar:
            self.progress_bar.stop()

        # Update status
        if self.status_label:
            if result["success"]:
                self.status_label.config(
                    text="✅ Installation completed!", foreground="green")
            else:
                error_msg = result.get("error", "Unknown error")
                self.status_label.config(
                    text=f"❌ Installation failed: {error_msg}", foreground="red")

        # Disable cancel button
        if self.cancel_button:
            self.cancel_button.config(state=tk.DISABLED)

        # Call completion callback
        if completion_callback:
            completion_callback(result)

    def _cancel_installation(self):
        """Cancel the installation"""
        self.pip_manager.cancel_installation()
        if self.status_label:
            self.status_label.config(
                text="❌ Installation cancelled", foreground="orange")
        if self.progress_bar:
            self.progress_bar.stop()
        if self.cancel_button:
            self.cancel_button.config(state=tk.DISABLED)
