
"""
Base Step Interface - Defines the contract for installation steps using native tkinter

Design Principles:
- Each step is responsible for one specific installation task
- Steps provide their own UI widgets and validation logic
- Steps communicate through shared state variables
- Simple interface makes steps easy to implement and test
- Uses only native Python libraries (tkinter)
"""
from abc import ABC, abstractmethod
from configparser import ConfigParser
from typing import Dict, Any, Optional
import tkinter as tk
from tkinter import ttk
import logging


class BaseStep(ABC):
    """
    Abstract base class for installation steps.

    Each installation step should inherit from this class and implement
    the required methods to define its behavior and UI.
    """

    def __init__(self, installation_settings: ConfigParser, shared_state: Dict[str, Any]):
        """Initialize the installation step

        Args:
            installation_settings: Configuration from install_settings.ini
            shared_state: Dictionary of state variables shared between steps
        """
        self.installation_settings = installation_settings
        self.shared_state = shared_state
        self.is_active = False
        self._completed = False

        # Completion state change callback - called when can_complete status changes
        self.completion_state_changed_callback = None

    # ========================================================================
    # Required Methods (must be implemented by subclasses)
    # ========================================================================

    @abstractmethod
    def get_title(self) -> str:
        """Get the title for this step

        Returns:
            Human-readable title for the step (e.g., "Select Installation Folder")
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Get the description for this step

        Returns:
            Detailed description of what this step does
        """
        pass

    @abstractmethod
    def complete_step(self) -> bool:
        """Attempt to complete this step

        This method should:
        1. Validate user input
        2. Perform the step's main action
        3. Update shared state variables
        4. Return True if successful, False otherwise

        Returns:
            True if step completed successfully, False otherwise
        """
        pass

    # ========================================================================
    # Optional Methods (can be overridden by subclasses)
    # ========================================================================

    def get_hint_text(self) -> str:
        """Get hint text to help the user complete this step

        Returns:
            Helpful hint text, or empty string if no hint needed
        """
        return ""

    def can_complete(self) -> bool:
        """Check if the step can be completed in its current state

        Returns:
            True if the Complete Step button should be enabled
        """
        return True

    def create_widgets(self, parent_frame: tk.Frame):
        """Create UI widgets for this step

        Override this method to add custom widgets to the step frame.

        Args:
            parent_frame: The parent tkinter frame to add components to
        """
        # Default implementation - no custom widgets
        pass

    def set_active(self):
        """Called when this step becomes the active step"""
        self.is_active = True
        logging.info(f"Entering step: {self.get_title()}")

    def set_inactive(self):
        """Called when this step is no longer active"""
        self.is_active = False
        logging.info(f"Leaving step: {self.get_title()}")
        # Call cleanup if implemented by subclass
        if hasattr(self, 'cleanup_widgets'):
            self.cleanup_widgets()

    def cancel_step(self):
        """Called when the installation is cancelled

        Override this method to perform cleanup if needed.
        """
        pass

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def update_shared_state(self, key: str, value: Any):
        """Update a shared state variable

        Args:
            key: State variable name
            value: New value for the state variable
        """
        logging.debug(f"Step '{self.get_title()}': Setting shared state {key} = {value}")
        self.shared_state[key] = value

    def get_shared_state(self, key: str, default: Any = None) -> Any:
        """Get a shared state variable value

        Args:
            key: State variable name
            default: Default value if key doesn't exist

        Returns:
            Value of the state variable, or default if not found
        """
        return self.shared_state.get(key, default)

    def mark_completed(self):
        """Mark this step as completed and notify completion state change"""
        old_can_complete = self.can_complete()
        self._completed = True
        new_can_complete = self.can_complete()
        
        logging.info(f"Step '{self.get_title()}': Marked as completed")

        # Notify if completion state changed
        if old_can_complete != new_can_complete:
            self._notify_completion_state_changed()

    def is_completed(self) -> bool:
        """Check if this step has been completed

        Returns:
            True if step is completed, False otherwise
        """
        return self._completed

    def set_completion_state_changed_callback(self, callback):
        """Set the callback to be called when completion state changes

        Args:
            callback: Function to call when can_complete() result changes
        """
        self.completion_state_changed_callback = callback

    def _notify_completion_state_changed(self):
        """Notify listeners that the completion state has changed"""
        if self.completion_state_changed_callback:
            try:
                self.completion_state_changed_callback(self.can_complete())
            except Exception as e:
                print(f"Error in completion state changed callback: {e}")

    def notify_completion_state_changed(self):
        """Public method for steps to manually trigger completion state change notification"""
        self._notify_completion_state_changed()
