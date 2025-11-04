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
