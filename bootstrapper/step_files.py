"""Step 5: Verify Required Files"""
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox


class FilesStep:
    def __init__(self, wizard):
        self.wizard = wizard
        self.check_files_btn = None
        self.create_files_btn = None
        self.file_labels = {}
        self.required_files = ["start_program.bat", "update.bat", "config.yml"]

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
        """Create template files for missing required files"""
        install_dir = Path(self.wizard.install_path.get())

        templates = {
            "start_program.bat": "@echo off\ncd /d %~dp0\ncall .venv\\Scripts\\activate.bat\npython main.py\npause\n",
            "update.bat": "@echo off\ncd /d %~dp0\ncall .venv\\Scripts\\activate.bat\npip install --upgrade my_library\npause\n",
            "config.yml": "# Configuration file\napp_name: My Application\nversion: 1.0.0\n"
        }

        created = []
        for fname, lbl in self.file_labels.items():
            file_path = install_dir / fname
            if not file_path.exists():
                try:
                    file_path.write_text(templates.get(fname, f"# {fname}\n"))
                    lbl.config(text=f"✅ {fname} (created)", foreground="green")
                    created.append(fname)
                    self.wizard.log(f"Created file: {fname}")
                except Exception as e:
                    self.wizard.log(f"Failed to create {fname}: {e}", "error")

        if created:
            messagebox.showinfo("Files Created",
                                f"Created {len(created)} file(s):\n" + "\n".join(created))
            self.check_files()  # Re-check
