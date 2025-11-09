"""Step 1: Select Installation Folder"""
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog
from .base_step import BaseStep
from .constants import *


class FolderStep(BaseStep):
    def __init__(self, wizard):
        super().__init__(wizard)
        self.install_path = wizard.install_path
        # Track the last validated path to detect changes
        self._last_validated_path = None

    def get_step_key(self) -> str:
        return STEP_FOLDER

    def build_ui(self, parent):
        """Build the UI for folder selection"""
        frame = ttk.Frame(parent)
        frame.pack(fill="x")

        self.create_info_label(frame, "Select or confirm installation folder:")

        entry_frame = ttk.Frame(frame)
        entry_frame.pack(fill="x", pady=PADDING_SMALL)

        ttk.Entry(entry_frame, textvariable=self.install_path,
                  width=ENTRY_WIDTH).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(entry_frame, text=BTN_BROWSE,
                   command=self.browse_folder).pack(side="left")

        self.create_status_label(frame, STATUS_NOT_VALIDATED)

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
        current_path = str(folder)

        # Check if path actually changed from last validation
        path_changed = self._last_validated_path is not None and self._last_validated_path != current_path

        self.log("=== FOLDER VALIDATION ===")
        self.log(f"[FOLDER] Validating path: {current_path}")
        self.log(
            f"[FOLDER] Previous validated path: {self._last_validated_path}")
        self.log(f"[FOLDER] Path changed: {path_changed}")

        try:
            if folder.exists() and folder.is_dir():
                self.update_status(STATUS_FOLDER_OK, COLOR_GREEN)
                self.mark_complete()
                self.log(f"[FOLDER] ✅ Folder validated: {folder}")
            else:
                # Try to create the folder
                self.log(f"[FOLDER] Creating folder: {folder}")
                folder.mkdir(parents=True, exist_ok=True)
                self.update_status("✅ Folder created", COLOR_GREEN)
                self.mark_complete()
                self.log(f"[FOLDER] ✅ Folder created: {folder}")

            # If path changed, invalidate dependent steps
            if path_changed:
                self.log(
                    f"[FOLDER] 🔄 Installation path changed from '{self._last_validated_path}' to '{current_path}'")
                self.log(
                    f"[FOLDER] This will affect venv path: {self.get_venv_path()}")
                self.invalidate_path_dependent_steps()

            # Update tracked path
            self._last_validated_path = current_path
            self.log(f"[FOLDER] Updated tracked path to: {current_path}")

        except Exception as e:
            self.update_status(f"❌ Invalid folder: {str(e)}", COLOR_RED)
            self.mark_incomplete()
            self.log(f"[FOLDER] ❌ Folder validation failed: {e}", "error")

    def auto_detect(self):
        """Auto-detect if folder exists"""
        # Check DEV section for simulation first
        if self.is_simulated():
            self.update_status("✅ Folder selected (simulated)", COLOR_ORANGE)
            self.mark_complete()
            self.log("DEV: Simulating folder selection completion")
            # Set tracked path for simulation
            self._last_validated_path = str(Path(self.install_path.get()))
            return

        folder = Path(self.install_path.get())
        if folder.exists():
            self.validate()
