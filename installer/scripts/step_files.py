"""Step 5: Verify Required Files"""
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import configparser


class FilesStep:
    def __init__(self, wizard):
        self.wizard = wizard
        self.status_label = None
        self.success_label = None
        self.required_files = ["run_app.pyw",
                               "launch_config.ini", "update.pyw", "about.pyw"]
        self.app_name = self.load_app_name()
        self.library_name = self.load_library_name()
        self.help_page = self.load_help_page()
        self.venv_dir_name = self.load_venv_dir_name()
        self.auto_generate_files = self.load_auto_generate_files()

    def load_auto_generate_files(self):
        """Load auto_generate_files setting from config.ini"""
        config = configparser.ConfigParser()
        config_file = Path(__file__).parent / "config.ini"

        try:
            config.read(config_file)
            return config.getboolean('DEV', 'auto_generate_files', fallback=True)
        except Exception:
            return True

    def load_venv_dir_name(self):
        """Load venv directory name from config.ini"""
        config = configparser.ConfigParser()
        config_file = Path(__file__).parent / "config.ini"

        try:
            config.read(config_file)
            return config.get('Paths', 'venv_dir', fallback='.venv')
        except Exception:
            return '.venv'

    def load_app_name(self):
        """Load app name from config.ini"""
        config = configparser.ConfigParser()
        config_file = Path(__file__).parent / "config.ini"

        try:
            config.read(config_file)
            return config.get('Settings', 'app_name', fallback='My Application')
        except Exception:
            return 'My Application'

    def load_library_name(self):
        """Load library name from config.ini"""
        config = configparser.ConfigParser()
        config_file = Path(__file__).parent / "config.ini"

        try:
            config.read(config_file)
            return config.get('Dependencies', 'core_libraries', fallback='my_library')
        except Exception:
            return 'my_library'

    def load_help_page(self):
        """Load help page URL from config.ini"""
        config = configparser.ConfigParser()
        config_file = Path(__file__).parent / "config.ini"

        try:
            config.read(config_file)
            return config.get('URLs', 'help_page', fallback='https://example.com/help')
        except Exception:
            return 'https://example.com/help'

    def build_ui(self, parent):
        """Build the UI for file creation"""
        frame = ttk.Frame(parent)
        frame.pack(fill="x")

        # Status label for auto-creation
        self.status_label = ttk.Label(
            frame, text=self.get_waiting_message(), foreground="gray")
        self.status_label.pack(anchor="w", pady=(0, 5))

        # Auto-generation status info
        if not self.auto_generate_files:
            auto_info_label = ttk.Label(
                frame, text="⚙️ Auto-generation disabled - files must be created manually",
                foreground="blue", font=("", 9))
            auto_info_label.pack(anchor="w", pady=(0, 5))

        # Success message (initially hidden)
        self.success_label = ttk.Label(
            frame, text="", foreground="green", font=("", 11, "bold"))
        self.success_label.pack(anchor="w", pady=(5, 10))

        # Manual create button (only show if prerequisites are met but files not created)
        self.create_manual_btn = ttk.Button(frame, text="🔧 Create Files Manually",
                                            command=self.create_files_manually)
        # Initially hidden, will be shown when appropriate

        # Auto-create files if all prerequisites are complete
        if self.all_prerequisites_complete():
            self.auto_create_files()
        else:
            # Show manual button if not auto-creating
            self.update_manual_button_visibility()

    def all_prerequisites_complete(self):
        """Check if all prerequisite steps (1-4) are complete"""
        # Check if skip_local_index is enabled to determine if PyIRC is required
        config = configparser.ConfigParser()
        config_file = Path(__file__).parent / "config.ini"

        try:
            config.read(config_file)
            skip_local_index = config.getboolean(
                'DEV', 'skip_local_index', fallback=False)
        except Exception:
            skip_local_index = False

        if skip_local_index:
            # When skipping local index, PyIRC is not required
            required_steps = ["folder", "venv", "library"]
        else:
            # Normal operation requires PyIRC
            required_steps = ["folder", "venv", "pyirc", "library"]

        return all(self.wizard.step_status.get(step, False) for step in required_steps)

    def get_waiting_message(self):
        """Get appropriate waiting message based on which steps are incomplete"""
        # Check if skip_local_index is enabled to determine if PyIRC is required
        config = configparser.ConfigParser()
        config_file = Path(__file__).parent / "config.ini"

        try:
            config.read(config_file)
            skip_local_index = config.getboolean(
                'DEV', 'skip_local_index', fallback=False)
        except Exception:
            skip_local_index = False

        incomplete_steps = []
        step_names = {
            "folder": "Step 1 (Folder)",
            "venv": "Step 2 (Virtual Environment)",
            "library": "Step 4 (Library)"
        }

        # Only include PyIRC if not skipping local index
        if not skip_local_index:
            step_names["pyirc"] = "Step 3 (PyIRC)"

        for step, name in step_names.items():
            if not self.wizard.step_status.get(step, False):
                incomplete_steps.append(name)

        if not incomplete_steps:
            return "✅ All prerequisites complete!"
        elif len(incomplete_steps) == 1:
            return f"⏸ Waiting for {incomplete_steps[0]} to complete..."
        else:
            return f"⏸ Waiting for steps: {', '.join(incomplete_steps)}"

    def update_manual_button_visibility(self):
        """Show or hide the manual create button based on current state"""
        if hasattr(self, 'create_manual_btn'):
            if (self.all_prerequisites_complete() and
                    not self.wizard.step_status.get("files", False)):
                self.create_manual_btn.pack(anchor="w", pady=(5, 5))
            else:
                self.create_manual_btn.pack_forget()

    def create_files_manually(self):
        """Create files manually with dialog"""
        # Update status to show we're creating files
        if self.status_label:
            self.status_label.config(
                text="🔧 Creating application files...", foreground="blue")

        # Small delay to show the status update
        self.wizard.after(100, self._perform_manual_creation)

    def _perform_manual_creation(self):
        """Perform the actual manual file creation"""
        # Check which files exist before creation
        install_dir = Path(self.wizard.install_path.get())
        existing_files = []
        for fname in self.required_files:
            file_path = install_dir / fname
            if file_path.exists():
                existing_files.append(fname)

        # Create the files
        self.create_files(show_dialog=True)

        # Provide feedback based on what happened
        if existing_files and len(existing_files) == len(self.required_files):
            # All files already existed
            if self.status_label:
                self.status_label.config(
                    text="ℹ️ All files already exist!", foreground="orange")
        elif existing_files:
            # Some files existed, some were created
            created_count = len(self.required_files) - len(existing_files)
            if self.status_label:
                self.status_label.config(
                    text=f"✅ Created {created_count} files, {len(existing_files)} already existed", foreground="green")
        else:
            # All files were newly created
            if self.status_label:
                self.status_label.config(
                    text=f"✅ Created all {len(self.required_files)} files successfully!", foreground="green")

        # Check if all files now exist and mark step as complete
        self._check_completion_after_manual_creation()

        self.update_manual_button_visibility()

    def _check_completion_after_manual_creation(self):
        """Check if Step 5 is now complete after manual file creation"""
        install_dir = Path(self.wizard.install_path.get())
        all_files_exist = all((install_dir / fname).exists()
                              for fname in self.required_files)

        if all_files_exist:
            # Mark step as complete
            self.wizard.step_status["files"] = True
            self.wizard.log(
                "Step 5 completed - Manual file creation successful")

            # Show completion message
            if self.success_label:
                self.success_label.config(
                    text=f"🎉 Setup Complete! run_app.pyw now exists - close this installer and double-click run_app.pyw to start {self.app_name}")

            # Update overall progress
            self.wizard.update_progress()

    def refresh_status(self):
        """Refresh the status display based on current step completion"""
        if hasattr(self, 'status_label') and self.status_label:
            if self.all_prerequisites_complete():
                # Don't auto-trigger if files are already created
                if not self.wizard.step_status.get("files", False):
                    self.auto_create_files()
            else:
                self.status_label.config(
                    text=self.get_waiting_message(), foreground="gray")

        # Update manual button visibility
        self.update_manual_button_visibility()

    def auto_create_files(self):
        """Automatically create required files"""
        if not self.all_prerequisites_complete():
            if self.status_label:
                self.status_label.config(
                    text=self.get_waiting_message(), foreground="gray")
            return

        # Check if auto-generation is enabled
        if not self.auto_generate_files:
            if self.status_label:
                self.status_label.config(
                    text="✅ Ready to create files (auto-generation disabled)", foreground="blue")
            # Show manual button since auto-generation is disabled
            self.update_manual_button_visibility()
            return

        # Update status
        if self.status_label:
            self.status_label.config(
                text="🔧 Creating application files...", foreground="blue")

        # Hide manual button since we're auto-creating
        if hasattr(self, 'create_manual_btn'):
            self.create_manual_btn.pack_forget()

        # Create files immediately
        self.wizard.after(500, self.create_files_silently)

    def create_files_silently(self):
        """Silently create files and show success message"""
        self.create_files(show_dialog=False)

    def create_files(self, show_dialog=True):
        """Create launcher files for the application"""
        install_dir = Path(self.wizard.install_path.get())

        # Template for run_app.pyw (main launcher)
        run_app_template = f'''"""
{self.app_name} Main Launcher
Upgrades library and runs the application
"""
import subprocess
import sys
from pathlib import Path
import configparser

def main():
    # Get paths
    app_dir = Path(__file__).parent
    venv_python = app_dir / "{self.venv_dir_name}" / "Scripts" / "python.exe"
    
    if not venv_python.exists():
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Python not found at {{venv_python}}")
        return
    
    # Load debug setting from launch config
    launch_config = configparser.ConfigParser()
    launch_config_file = app_dir / "launch_config.ini"
    debug_mode = False
    if launch_config_file.exists():
        launch_config.read(launch_config_file)
        debug_str = launch_config.get('Settings', 'debug', fallback='false')
        debug_mode = debug_str.lower() in ('true', '1', 'yes', 'on')
    
    # Windows flag to hide console (only if not in debug mode)
    CREATE_NO_WINDOW = 0x08000000
    creation_flags = 0 if debug_mode else CREATE_NO_WINDOW
    capture_output = not debug_mode  # Don't capture output if in debug mode
    
    try:
        # Step 1: Upgrade the library
        subprocess.run(
            [str(venv_python), "-m", "pip", "install", "--upgrade", "{self.library_name}"],
            capture_output=capture_output,
            creationflags=creation_flags
        )
        
        # Step 2: Load launch config
        config = configparser.ConfigParser()
        config_file = app_dir / "launch_config.ini"
        if config_file.exists():
            config.read(config_file)
            # Get launch_config as a dictionary
            launch_config = dict(config['DEFAULT']) if config.has_section('DEFAULT') else {{}}
        else:
            launch_config = {{}}
        
        # Step 3: Import and run the library
        import {self.library_name}
        {self.library_name}.run(launch_config)
        
    except Exception as e:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Failed to start application: {{e}}")

if __name__ == "__main__":
    main()
'''

        # Template for launch_config.ini
        launch_config_template = f'''[DEFAULT]
# Configuration settings for {self.app_name}
debug_mode = false



'''

        # Template for update.pyw (standalone updater)
        update_template = f'''"""
{self.app_name} Updater
Standalone updater utility
"""
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

def main():
    # Create update window
    root = tk.Tk()
    root.title("{self.app_name} Updater")
    root.geometry("400x200")
    root.resizable(False, False)
    
    # Center the window
    root.eval('tk::PlaceWindow . center')
    
    ttk.Label(root, text="Updating {self.app_name}...", font=("", 12)).pack(pady=20)
    
    progress = ttk.Progressbar(root, length=300, mode='indeterminate')
    progress.pack(pady=10)
    progress.start()
    
    status_label = ttk.Label(root, text="Starting update...")
    status_label.pack(pady=10)
    
    def update_library():
        app_dir = Path(__file__).parent
        venv_python = app_dir / "{self.venv_dir_name}" / "Scripts" / "python.exe"
        
        if not venv_python.exists():
            messagebox.showerror("Error", f"Python not found at {{venv_python}}")
            root.destroy()
            return
        
        try:
            status_label.config(text="Updating {self.library_name}...")
            root.update()
            
            # Load debug setting from launch config
            launch_config = configparser.ConfigParser()
            launch_config_file = app_dir / "launch_config.ini"
            debug_mode = False
            if launch_config_file.exists():
                launch_config.read(launch_config_file)
                debug_str = launch_config.get('Settings', 'debug', fallback='false')
                debug_mode = debug_str.lower() in ('true', '1', 'yes', 'on')
            
            # Use CREATE_NO_WINDOW only if not in debug mode
            creation_flags = 0 if debug_mode else 0x08000000
            capture_output = not debug_mode  # Don't capture output if in debug mode
            
            result = subprocess.run(
                [str(venv_python), "-m", "pip", "install", "--upgrade", "{self.library_name}"],
                capture_output=capture_output,
                text=True,
                creationflags=creation_flags
            )
            
            progress.stop()
            
            if result.returncode == 0:
                status_label.config(text="Update completed successfully!")
                messagebox.showinfo("Success", "Update completed successfully!")
            else:
                status_label.config(text="Update failed!")
                messagebox.showerror("Error", f"Update failed:\\n{{result.stderr}}")
            
            root.destroy()
            
        except Exception as e:
            progress.stop()
            status_label.config(text="Update failed!")
            messagebox.showerror("Error", f"Update failed: {{e}}")
            root.destroy()
    
    # Start update after window is shown
    root.after(1000, update_library)
    root.mainloop()

if __name__ == "__main__":
    main()
'''

        # Template for about.pyw (help page launcher)
        about_template = f'''"""
{self.app_name} About / Help
Opens the help page in the default web browser
"""
import webbrowser
import tkinter as tk
from tkinter import messagebox

def main():
    try:
        # Open help page in default browser
        webbrowser.open("{self.help_page}")
    except Exception as e:
        # Show error if browser fails to open
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Failed to open help page: {{e}}")

if __name__ == "__main__":
    main()
'''

        templates = {
            "run_app.pyw": run_app_template,
            "launch_config.ini": launch_config_template,
            "update.pyw": update_template,
            "about.pyw": about_template
        }

        created = []
        for fname in self.required_files:
            file_path = install_dir / fname
            if not file_path.exists():
                try:
                    file_path.write_text(
                        templates.get(fname, f"# {fname}\\n"))
                    created.append(fname)
                    self.wizard.log(f"Created file: {fname}")
                except Exception as e:
                    self.wizard.log(
                        f"Failed to create {fname}: {e}", "error")

        if created:
            if show_dialog:
                messagebox.showinfo("Files Created",
                                    f"Created {{len(created)}} file(s):\\n" + "\\n".join(created) +
                                    f"\\n\\nDouble-click run_app.pyw to run {self.app_name}!")
            else:
                # Silent mode - show success in UI
                if self.status_label:
                    self.status_label.config(
                        text="✅ Application files created successfully!", foreground="green")
                if self.success_label:
                    self.success_label.config(
                        text=f"🎉 Setup Complete! run_app.pyw now exists - close this installer and double-click run_app.pyw to start {self.app_name}")

                # Mark step as complete
                self.wizard.step_status["files"] = True
                self.wizard.update_progress()
                self.wizard.log(
                    f"Step 5 completed - Created {{len(created)}} files: {{', '.join(created)}}")
        else:
            # All files already exist
            if not show_dialog:
                if self.status_label:
                    self.status_label.config(
                        text="✅ All application files already exist!", foreground="green")
                if self.success_label:
                    self.success_label.config(
                        text=f"🎉 Complete! Click run_app.pyw in target folder to start {self.app_name}")

                self.wizard.step_status["files"] = True
                self.wizard.update_progress()
                self.wizard.log("Step 5 completed - All files already existed")

    def auto_detect(self):
        """Auto-detect if files should be created"""
        # Check DEV section for simulation first
        config = configparser.ConfigParser()
        config_file = Path(__file__).parent / "config.ini"

        try:
            config.read(config_file)
            if config.getboolean('DEV', 'simulate_files_complete', fallback=False):
                if hasattr(self, 'status_label') and self.status_label:
                    self.status_label.config(
                        text="✅ Application files (simulated)", foreground="orange")
                if hasattr(self, 'success_label') and self.success_label:
                    self.success_label.config(
                        text=f"🎉 Setup Complete (Simulated)! run_app.pyw would exist")
                self.wizard.step_status["files"] = True
                self.wizard.log("DEV: Simulating files creation completion")
                self.wizard.update_progress()
                return
        except Exception:
            pass  # Continue with normal detection if config read fails

        if self.all_prerequisites_complete():
            if hasattr(self, 'status_label'):
                self.auto_create_files()
