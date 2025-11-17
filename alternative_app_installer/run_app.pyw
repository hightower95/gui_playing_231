"""
ProductivityApp Main Launcher
Sophisticated launcher with auto-upgrade capabilities and utility functions
"""
from utilities.version_manager import (
    get_installed_version,
    should_upgrade,
    upgrade_to_version
)
import os
import subprocess
import sys
import configparser
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import threading
import socket

# Add utilities to path
sys.path.insert(0, str(Path(__file__).parent))


def load_launch_config(config_file):
    """Load launch configuration from file with safe defaults"""
    config = configparser.ConfigParser()

    if config_file.exists():
        config.read(config_file)

    # Return as dictionary with minimal defaults
    defaults = {
        'library_name': 'productivity_app',
        'venv_path': r'c:\Users\peter\OneDrive\Documents\Coding\gui\.venv_dev_install',
        'always_upgrade': 'true',
        'allow_upgrade_to_test_releases': 'false',
        'enable_log': 'false',
        'log_level': 'INFO',
        'auto_upgrade_major_version': 'false',
        'auto_upgrade_minor_version': 'true',
        'auto_upgrade_patches': 'true'
    }

    if config.has_section('DEFAULT'):
        defaults.update(dict(config['DEFAULT']))

    return defaults


def get_venv_python(config):
    """Get venv Python path from config"""
    # Get venv path from config
    venv_path = config.get('venv_path', '')
    if not venv_path:
        return None

    venv_dir = Path(venv_path)
    if not venv_dir.exists():
        return None

    # Construct Python executable path
    if sys.platform == 'win32':
        python_path = venv_dir / 'Scripts' / 'python.exe'
    else:
        python_path = venv_dir / 'bin' / 'python'

    if python_path.exists():
        return python_path

    return None


# Function to handle socket communication
def socket_server(loading_root):
    print("Starting splash screen server...")

    def handle_client(client_socket):
        try:
            while True:
                message = client_socket.recv(1024).decode("utf-8")
                print(f"Received message: {message}")
                if message == "close":
                    loading_root.quit()
                    break
        except Exception as e:
            print(f"Socket error: {e}")
        finally:
            client_socket.close()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 65432))  # Bind to localhost and port 65432
    server.listen(1)  # Allow only one connection

    print("Splash screen server listening on localhost:65432")
    client_socket, _ = server.accept()
    handle_client(client_socket)
    server.close()


# Function to create a simple loading screen
def show_loading_screen():
    loading_root = tk.Tk()
    loading_root.title("Loading")
    loading_root.geometry("300x100")
    loading_label = tk.Label(
        loading_root, text="Loading, please wait...", font=("Arial", 12))
    loading_label.pack(expand=True)

    # Start the socket server in a separate thread
    server_thread = threading.Thread(
        target=socket_server, args=(loading_root,), daemon=True)
    server_thread.start()

    # Keep the window reference to close it later
    # Disable close button
    loading_root.protocol("WM_DELETE_WINDOW", lambda: None)
    loading_root.mainloop()
    return loading_root


# Function to start the loading screen in a separate thread
def start_loading_screen():
    loading_thread = threading.Thread(target=show_loading_screen, daemon=True)
    loading_thread.start()
    return loading_thread


# Function to stop the loading screen
def stop_loading_screen(loading_root):
    try:
        if loading_root:
            loading_root.quit()
    except AttributeError as e:
        pass
    except Exception as e:
        print(f"Error stopping loading screen: {e}")


def main():
    loading_thread = None
    try:
        # Start the loading screen
        loading_thread = start_loading_screen()

        app_dir = Path(__file__).parent.absolute()
        launch_config_file = app_dir / "launch_config.ini"

        # Load configuration
        config = load_launch_config(launch_config_file)

        # Get virtual environment python
        venv_python = get_venv_python(config)

        if venv_python is None:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Virtual Environment Not Found",
                                 "Could not find virtual environment.\\n\\n"
                                 "Please run the installer to set up the virtual environment.")
            return

    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Startup Error", f"Failed to initialize application: {e}")
        return

    # Windows flag to hide console
    creation_flags = 0x08000000 if sys.platform == 'win32' else 0

    try:
        # Step 1: Intelligent version management with auto-upgrade
        current_version = get_installed_version(
            venv_python, config['library_name'])

        if current_version:
            # Check if we should upgrade based on auto-upgrade settings
            target_version = should_upgrade(
                current_version, config, venv_python, config['library_name'])

            if target_version:
                # Perform the upgrade
                upgrade_success = upgrade_to_version(
                    venv_python, config['library_name'], target_version)

                if not upgrade_success:
                    # Log upgrade failure but continue with current version
                    print(
                        f"Warning: Upgrade from {current_version} to {target_version} failed")
        else:
            # Library not installed, try to install it
            try:
                subprocess.run(
                    [str(venv_python), "-m", "pip",
                     "install", config['library_name']],
                    capture_output=True, text=True, timeout=300, check=True
                )
            except subprocess.CalledProcessError:
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("Installation Failed",
                                     f"Could not install {config['library_name']}")
                return

        # Step 2: Create runner script that handles launch config
        runner_script = f'''
import sys
import configparser
from pathlib import Path

# Load launch config
app_dir = Path(__name__).parent
config = configparser.ConfigParser()
config_file = app_dir / "launch_config.ini"
launch_config = dict()
if config_file.exists():
    config.read(config_file)
    if config.has_section('DEFAULT'):
        launch_config = dict(config['DEFAULT'])

# Import and run the library
try:
    import {config['library_name']}
    {config['library_name']}.start(launch_config)
except Exception as e:
    print("Runtime error: " + str(e))
    raise
'''

        # Step 3: Run the application with UTF-8 support
        env = os.environ.copy()
        env['PYTHONUTF8'] = '1'

        result = subprocess.run(
            [str(venv_python), "-X", "utf8", "-c", runner_script],
            cwd=str(app_dir),
            capture_output=True,
            text=True,
            creationflags=creation_flags,
            env=env
        )

        # Handle errors
        if result.returncode != 0:
            error_msg = "Application failed"
            if result.stderr:
                error_msg += f":\\n\\n{result.stderr.strip()}"
            else:
                error_msg += f" with exit code: {result.returncode}"

            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Application Error", error_msg)

    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Startup Error", f"Failed to start application: {e}")

    finally:
        # Stop the loading screen
        if loading_thread:
            stop_loading_screen(loading_thread)


if __name__ == "__main__":
    main()
