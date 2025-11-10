"""
ProductivityApp Update Manager
Shows current version and available updates with a simple GUI
"""
import subprocess
import sys
import configparser
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox


def load_launch_config(config_file):
    """Load launch configuration from file"""
    config = configparser.ConfigParser()

    if config_file.exists():
        config.read(config_file)

    # Return as dictionary with minimal defaults
    defaults = {
        'library_name': '{{LIBRARY_NAME}}',
        'venv_path': '{{VENV_PATH}}',
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


def get_installed_version(venv_python, library_name):
    """Get the currently installed version of a library"""
    try:
        result = subprocess.run(
            [str(venv_python), "-m", "pip", "show", library_name],
            capture_output=True, text=True, timeout=30
        )

        if result.returncode == 0:
            for line in result.stdout.split('\\n'):
                if line.startswith('Version:'):
                    return line.split(':', 1)[1].strip()
        return None
    except Exception:
        return None


def get_all_versions(venv_python, library_name):
    """Get all available versions of a library"""
    try:
        result = subprocess.run(
            [str(venv_python), "-m", "pip", "index", "versions", library_name],
            capture_output=True, text=True, timeout=60
        )

        versions = []
        if result.returncode == 0:
            for line in result.stdout.split('\\n'):
                if 'Available versions:' in line:
                    version_part = line.split('Available versions:')[1].strip()
                    versions = [v.strip()
                                for v in version_part.split(',') if v.strip()]
                    break

        return versions
    except Exception:
        return []


def upgrade_to_version(venv_python, library_name, target_version):
    """Upgrade library to specific version"""
    try:
        result = subprocess.run(
            [str(venv_python), "-m", "pip", "install",
             f"{library_name}=={target_version}"],
            capture_output=True, text=True, timeout=300
        )
        return result.returncode == 0
    except Exception:
        return False


class UpdateManagerGUI:
    def __init__(self, config, venv_python, current_version):
        self.config = config
        self.venv_python = venv_python
        self.current_version = current_version

        self.root = tk.Tk()
        self.root.title("Update Manager")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        self.setup_ui()

    def setup_ui(self):
        # Current version info
        current_frame = ttk.LabelFrame(
            self.root, text="Current Version", padding=10)
        current_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(current_frame, text=f"Library: {self.config['library_name']}",
                  font=("Arial", 10, "bold")).pack(anchor="w")
        ttk.Label(current_frame, text=f"Installed: {self.current_version or 'Not installed'}",
                  font=("Arial", 9)).pack(anchor="w")

        # Available versions
        versions_frame = ttk.LabelFrame(
            self.root, text="Available Versions", padding=10)
        versions_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Version listbox
        listbox_frame = ttk.Frame(versions_frame)
        listbox_frame.pack(fill="both", expand=True)

        self.version_listbox = tk.Listbox(
            listbox_frame, font=("Courier New", 9))
        scrollbar = ttk.Scrollbar(
            listbox_frame, orient="vertical", command=self.version_listbox.yview)
        self.version_listbox.config(yscrollcommand=scrollbar.set)

        self.version_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Load available versions
        self.load_versions()

        # Buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(button_frame, text="Refresh",
                   command=self.load_versions).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Install Selected",
                   command=self.install_selected).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Close",
                   command=self.root.quit).pack(side="right", padx=5)

    def load_versions(self):
        """Load available versions from package index"""
        try:
            self.version_listbox.delete(0, tk.END)
            self.version_listbox.insert(0, "Loading...")
            self.root.update()

            # Get all available versions
            versions = get_all_versions(
                self.venv_python, self.config['library_name'])

            self.version_listbox.delete(0, tk.END)

            if versions:
                for version in reversed(versions):  # Show latest first
                    status = " (INSTALLED)" if version == self.current_version else ""
                    self.version_listbox.insert(tk.END, f"{version}{status}")
            else:
                self.version_listbox.insert(0, "No versions found")

        except Exception as e:
            self.version_listbox.delete(0, tk.END)
            self.version_listbox.insert(0, f"Error: {e}")

    def install_selected(self):
        """Install the selected version"""
        selection = self.version_listbox.curselection()
        if not selection:
            messagebox.showwarning(
                "No Selection", "Please select a version to install.")
            return

        selected_text = self.version_listbox.get(selection[0])
        # Extract version number (remove status text)
        version = selected_text.split(" ")[0]

        if version == self.current_version:
            messagebox.showinfo("Already Installed",
                                f"Version {version} is already installed.")
            return

        # Confirm upgrade
        if not messagebox.askyesno("Confirm Install",
                                   f"Install {self.config['library_name']} version {version}?"):
            return

        try:
            # Perform upgrade
            success = upgrade_to_version(
                self.venv_python, self.config['library_name'], version)

            if success:
                messagebox.showinfo(
                    "Success", f"Successfully installed version {version}")
                self.current_version = version
                self.load_versions()  # Refresh list
            else:
                messagebox.showerror(
                    "Failed", f"Failed to install version {version}")

        except Exception as e:
            messagebox.showerror("Error", f"Installation failed: {e}")


def main():
    try:
        app_dir = Path(__file__).parent.absolute()
        launch_config_file = app_dir / "launch_config.ini"

        # Load configuration
        config = load_launch_config(launch_config_file)

        # Get virtual environment
        venv_python = get_venv_python(config)

        if venv_python is None:
            messagebox.showerror("Virtual Environment Not Found",
                                 "Could not find virtual environment. Please run the installer first.")
            return

        # Get current version
        current_version = get_installed_version(
            venv_python, config['library_name'])

        # Launch update GUI
        app = UpdateManagerGUI(config, venv_python, current_version)
        app.root.mainloop()

    except Exception as e:
        messagebox.showerror(
            "Startup Error", f"Failed to initialize update manager: {e}")


if __name__ == "__main__":
    main()
