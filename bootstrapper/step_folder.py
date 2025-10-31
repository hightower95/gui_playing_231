"""Step 1: Select Installation Folder"""
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog


class FolderStep:
    def __init__(self, wizard):
        self.wizard = wizard
        self.install_path = wizard.install_path
        self.folder_status = None

    def build_ui(self, parent):
        """Build the UI for folder selection"""
        frame = ttk.Frame(parent)
        frame.pack(fill="x")

        ttk.Label(frame, text="Select or confirm installation folder:").pack(
            anchor="w", pady=(0, 5))

        entry_frame = ttk.Frame(frame)
        entry_frame.pack(fill="x", pady=(0, 5))

        ttk.Entry(entry_frame, textvariable=self.install_path,
                  width=70).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(entry_frame, text="Browse...",
                   command=self.browse_folder).pack(side="left")

        self.folder_status = ttk.Label(
            frame, text="⏸ Not validated", foreground="gray")
        self.folder_status.pack(anchor="w", pady=(5, 0))

    def browse_folder(self):
        """Open folder browser dialog"""
        folder = filedialog.askdirectory(
            initialdir=self.install_path.get(),
            title="Select Installation Folder")
        if folder:
            self.install_path.set(folder)
            self.wizard.log(f"Folder selected: {folder}")
            self.validate()

    def validate(self):
        """Validate the selected folder"""
        folder = Path(self.install_path.get())
        try:
            if folder.exists() and folder.is_dir():
                self.folder_status.config(
                    text="✅ Folder OK", foreground="green")
                self.wizard.step_status["folder"] = True
                self.wizard.log(f"Folder validated: {folder}")
            else:
                # Try to create the folder
                folder.mkdir(parents=True, exist_ok=True)
                self.folder_status.config(
                    text="✅ Folder created", foreground="green")
                self.wizard.step_status["folder"] = True
                self.wizard.log(f"Folder created: {folder}")
        except Exception as e:
            self.folder_status.config(
                text=f"❌ Invalid folder: {str(e)}", foreground="red")
            self.wizard.step_status["folder"] = False
            self.wizard.log(f"Folder validation failed: {e}", "error")
        self.wizard.update_progress()

    def auto_detect(self):
        """Auto-detect if folder exists"""
        folder = Path(self.install_path.get())
        if folder.exists():
            self.validate()
