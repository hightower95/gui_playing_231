"""
Base Step Class for Bootstrap Wizard
Provides common functionality for all setup steps
"""
import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
from .config_manager import config_manager


class BaseStep(ABC):
    """Abstract base class for all bootstrap setup steps"""

    def __init__(self, wizard):
        self.wizard = wizard
        self.config = config_manager
        self.status_label: Optional[ttk.Label] = None

        # Each step must define its unique key
        self.step_key = self.get_step_key()

    @abstractmethod
    def get_step_key(self) -> str:
        """Return the unique key for this step (e.g., 'folder', 'venv')"""
        pass

    @abstractmethod
    def build_ui(self, parent: ttk.Frame) -> None:
        """Build the UI for this step"""
        pass

    @abstractmethod
    def auto_detect(self) -> None:
        """Auto-detect if this step is already completed"""
        pass

    def update_status(self, message: str, color: str = "gray") -> None:
        """Update the status label with message and color"""
        if self.status_label:
            self.status_label.config(text=message, foreground=color)

    def mark_complete(self) -> None:
        """Mark this step as completed and update wizard progress"""
        self.wizard.step_status[self.step_key] = True
        self.wizard.update_progress()
        self.wizard.log(f"Step {self.step_key} completed")

    def mark_incomplete(self) -> None:
        """Mark this step as incomplete"""
        self.wizard.step_status[self.step_key] = False
        self.wizard.update_progress()

    def is_complete(self) -> bool:
        """Check if this step is marked as complete"""
        return self.wizard.step_status.get(self.step_key, False)

    def is_simulated(self) -> bool:
        """Check if this step is set to be simulated in DEV mode"""
        return self.config.is_step_simulated(self.step_key)

    def log(self, message: str, level: str = "info") -> None:
        """Log a message via the wizard"""
        self.wizard.log(f"[{self.step_key}] {message}", level)

    # Common UI component helpers

    def create_status_label(self, parent: ttk.Frame, initial_text: str = "⏸ Not run yet") -> ttk.Label:
        """Create a standardized status label"""
        self.status_label = ttk.Label(
            parent, text=initial_text, foreground="gray")
        self.status_label.pack(anchor="w", pady=(5, 0))
        return self.status_label

    def create_action_button(self, parent: ttk.Frame, text: str, command, enabled: bool = True) -> ttk.Button:
        """Create a standardized action button"""
        btn = ttk.Button(parent, text=text, command=command)
        if not enabled:
            btn.config(state=tk.DISABLED)
        btn.pack(anchor="w", pady=(0, 5))
        return btn

    def create_info_label(self, parent: ttk.Frame, text: str) -> ttk.Label:
        """Create a standardized info label"""
        label = ttk.Label(parent, text=text)
        label.pack(anchor="w", pady=(0, 5))
        return label

    # Common validation helpers

    def get_install_path(self) -> Path:
        """Get the installation path from wizard"""
        return Path(self.wizard.install_path.get())

    def get_venv_path(self) -> Path:
        """Get the virtual environment path"""
        install_path = self.get_install_path()
        venv_dir = self.config.get_venv_dir()
        return install_path / venv_dir

    def invalidate_path_dependent_steps(self) -> None:
        """
        Invalidate steps that depend on installation path.
        Should be called when installation folder changes.
        """
        # Steps that depend on installation path
        path_dependent_steps = ['venv', 'library', 'files']

        for step_key in path_dependent_steps:
            if self.wizard.step_status.get(step_key, False):
                self.wizard.step_status[step_key] = False
                self.log(f"Invalidated step '{step_key}' due to path change")

        # Update wizard progress to reflect changes
        self.wizard.update_progress()
        self.log("Path-dependent steps invalidated due to installation folder change")

        # Trigger auto-detection on invalidated steps to see if they're still valid
        self.wizard.after(100, self._trigger_path_dependent_revalidation)

    def _trigger_path_dependent_revalidation(self) -> None:
        """Trigger auto-detection on path-dependent steps after invalidation"""
        try:
            # Re-run auto-detection on steps that depend on paths
            if hasattr(self.wizard, 'venv_step'):
                self.wizard.venv_step.auto_detect()
            if hasattr(self.wizard, 'library_step'):
                self.wizard.library_step.auto_detect()
            if hasattr(self.wizard, 'files_step'):
                self.wizard.files_step.auto_detect()
            self.log("Re-validated path-dependent steps after folder change")
        except Exception as e:
            self.log(
                f"Error during path-dependent revalidation: {e}", "warning")

    def check_prerequisites(self) -> list:
        """
        Check if prerequisites for this step are met.
        Returns list of missing prerequisites.
        Override in subclasses as needed.
        """
        return []

    def validate_step(self) -> bool:
        """
        Validate that this step can be executed.
        Override in subclasses for step-specific validation.
        """
        prerequisites = self.check_prerequisites()
        if prerequisites:
            self.log(
                f"Prerequisites not met: {', '.join(prerequisites)}", "warning")
            return False
        return True
