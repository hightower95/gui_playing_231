"""
Ping Module - Handles continuous ping operations
"""
import subprocess
import threading
import time
from typing import Callable, Optional


class PingController:
    """Handles ping operations with live output streaming"""

    def __init__(self, output_callback: Callable[[str], None]):
        """Initialize ping controller

        Args:
            output_callback: Function to call with each line of ping output
        """
        self.output_callback = output_callback
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.thread: Optional[threading.Thread] = None

    def start_pinging(self, ip: str) -> bool:
        """Start continuous ping to specified IP

        Args:
            ip: IP address or hostname to ping

        Returns:
            bool: True if ping started successfully, False otherwise
        """
        if self.is_running:
            self.output_callback(
                "❌ Ping already running. Stop current ping first.\n")
            return False

        try:
            # Validate IP/hostname is not empty
            if not ip.strip():
                self.output_callback(
                    "❌ Please enter an IP address or hostname.\n")
                return False

            self.output_callback(
                f"🚀 Starting continuous ping to {ip.strip()}...\n")
            self.output_callback("=" * 50 + "\n")

            # Start ping process in a separate thread
            self.is_running = True
            self.thread = threading.Thread(
                target=self._run_ping, args=(ip.strip(),))
            self.thread.daemon = True
            self.thread.start()

            return True

        except Exception as e:
            self.output_callback(f"❌ Error starting ping: {str(e)}\n")
            self.is_running = False
            return False

    def stop_pinging(self):
        """Stop the current ping operation"""
        if not self.is_running:
            return

        self.is_running = False

        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception as e:
                self.output_callback(f"⚠️ Error stopping ping: {str(e)}\n")

        self.output_callback("\n🛑 Ping stopped by user.\n")
        self.output_callback("=" * 50 + "\n")

    def _run_ping(self, ip: str):
        """Run the ping command in a separate thread

        Args:
            ip: IP address to ping
        """
        try:
            # Windows ping command with continuous mode (-t)
            cmd = ["ping", "-t", ip]

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Read output line by line
            while self.is_running and self.process.poll() is None:
                line = self.process.stdout.readline()
                if line:
                    # Add timestamp to each ping result
                    timestamp = time.strftime("%H:%M:%S")
                    formatted_line = f"[{timestamp}] {line.strip()}\n"
                    self.output_callback(formatted_line)
                else:
                    # Brief sleep to prevent busy waiting
                    time.sleep(0.01)

        except FileNotFoundError:
            self.output_callback(
                "❌ Error: 'ping' command not found. Check your system PATH.\n")
        except Exception as e:
            self.output_callback(f"❌ Ping error: {str(e)}\n")
        finally:
            self.is_running = False
            if self.process:
                try:
                    self.process.terminate()
                except:
                    pass


# Simple function interface for backwards compatibility
def start_pinging(ip: str, output_callback: Callable[[str], None]) -> PingController:
    """Start pinging an IP address

    Args:
        ip: IP address or hostname to ping
        output_callback: Function to call with ping output

    Returns:
        PingController: Controller object to manage the ping process
    """
    controller = PingController(output_callback)
    controller.start_pinging(ip)
    return controller
