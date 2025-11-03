"""Step 5: Verify Required Files"""
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import configparser


class FilesStep:
    def __init__(self, wizard):
        self.wizard = wizard
        self.check_files_btn = None
        self.create_files_btn = None
        self.file_labels = {}
        self.required_files = ["start_app.pyw", "update_app.bat"]
        self.app_name = self.load_app_name()

    def load_app_name(self):
        """Load app name from config.ini"""
        config = configparser.ConfigParser()
        config_file = Path(__file__).parent / "config.ini"

        try:
            config.read(config_file)
            return config.get('Settings', 'app_name', fallback='My Application')
        except Exception:
            return 'My Application'

    def build_ui(self, parent):
        """Build the UI for file verification"""
        frame = ttk.Frame(parent)
        frame.pack(fill="x")

        self.check_files_btn = ttk.Button(frame, text="Check Files",
                                          command=self.check_files)
        self.check_files_btn.pack(anchor="w", pady=(0, 5))

        for fname in self.required_files:
            lbl = ttk.Label(frame, text=f"⏸ {fname}", foreground="gray")
            lbl.pack(anchor="w")
            self.file_labels[fname] = lbl

        # Add "Create missing files" button
        self.create_files_btn = ttk.Button(frame, text="Create Missing Files",
                                           command=self.create_files, state=tk.DISABLED)
        self.create_files_btn.pack(anchor="w", pady=(5, 0))

    def check_files(self):
        """Check if required files exist"""
        if not self.wizard.step_status["library"]:
            messagebox.showwarning("Step 4 Required",
                                   "Please complete Step 4 (Install library) first.")
            return

        install_dir = Path(self.wizard.install_path.get())
        all_present = True
        missing_files = []

        for fname, lbl in self.file_labels.items():
            file_path = install_dir / fname
            exists = file_path.exists()
            if exists:
                lbl.config(text=f"✅ {fname}", foreground="green")
                self.wizard.log(f"File found: {fname}")
            else:
                lbl.config(text=f"❌ {fname} (missing)", foreground="red")
                self.wizard.log(f"File missing: {fname}", "warning")
                all_present = False
                missing_files.append(fname)

        self.wizard.step_status["files"] = all_present

        if not all_present:
            self.create_files_btn.config(state=tk.NORMAL)
        else:
            self.create_files_btn.config(state=tk.DISABLED)

        self.wizard.update_progress()

    def create_files(self):
        """Create launcher files for the application"""
        install_dir = Path(self.wizard.install_path.get())

        # Get the library path from the library step
        library_path = self.wizard.library_step.main_library_path
        library_name = library_path.name

        # Template for start_app.pyw (GUI launcher, no console)
        start_app_template = f'''"""
{self.app_name} Launcher
Auto-updates and starts the application without console window
"""
import subprocess
import sys
from pathlib import Path

def main():
    # Get paths
    install_dir = Path(__file__).parent
    venv_python = install_dir / ".venv" / "Scripts" / "python.exe"
    
    if not venv_python.exists():
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Python not found at {{venv_python}}")
        return
    
    # Windows flag to hide console
    CREATE_NO_WINDOW = 0x08000000
    
    try:
        # Step 1: Update the library (silent, in background)
        subprocess.run(
            [str(venv_python), "-m", "pip", "install", "--upgrade", "-e", str(install_dir / "{library_name}")],
            capture_output=True,
            creationflags=CREATE_NO_WINDOW
        )
        
        # Step 2: Start the application
        subprocess.run(
            [str(venv_python), "-m", "{library_name}"],
            creationflags=CREATE_NO_WINDOW
        )
    except Exception as e:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Failed to start application: {{e}}")

if __name__ == "__main__":
    main()
'''

        # Template for update_app.bat (console updater for manual updates)
        update_app_template = f'''@echo off
echo Updating {self.app_name}...
cd /d "%~dp0"
call .venv\\Scripts\\activate.bat
pip install --upgrade pip
pip install --upgrade -e "{library_name}"
echo.
echo Update complete!
pause
'''

        templates = {{
            "start_app.pyw": start_app_template,
            "update_app.bat": update_app_template
        }}

        created = []
        for fname, lbl in self.file_labels.items():
            file_path = install_dir / fname
            if not file_path.exists():
                try:
                    file_path.write_text(
                        templates.get(fname, f"# {{fname}}\\n"))
                    lbl.config(
                        text=f"✅ {{fname}} (created)", foreground="green")
                    created.append(fname)
                    self.wizard.log(f"Created file: {{fname}}")
                except Exception as e:
                    self.wizard.log(
                        f"Failed to create {{fname}}: {{e}}", "error")

        if created:
            messagebox.showinfo("Files Created",
                                f"Created {{len(created)}} file(s):\\n" + "\\n".join(created) +
                                "\\n\\nDouble-click start_app.pyw to run the application!")
            self.check_files()  # Re-check
