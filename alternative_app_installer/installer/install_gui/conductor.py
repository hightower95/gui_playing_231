"""
Install Conductor - Manages the sequence and flow of installation steps

Design Principles:
- Knows the complete sequence of installation steps
- Manages step transitions and state
- Provides interface for GUI to get current step and advance
- Maintains installation state variables shared between steps
"""
from configparser import ConfigParser
from typing import List, Dict, Any, Optional

from .steps import GetFolderStep, CreateVenvStep


class InstallConductor:
    """
    Orchestrates the installation process by managing step sequence and state.

    The Conductor pattern separates installation logic from GUI presentation,
    making the process easier to understand, test, and troubleshoot.
    """

    def __init__(self, installation_settings: ConfigParser):
        """Initialize the installation conductor

        Args:
            installation_settings: Configuration loaded from install_settings.ini
        """
        self.installation_settings = installation_settings

        # Shared state variables that steps can read/write
        # Only contains validated, accepted values from completed steps
        self._install_state_variables: Dict[str, Any] = {
            "valid_installation_path": "",
            "library_installed": False,
            "scripts_generated": False,
        }

        # Initialize all steps
        self._initialize_steps()

        # Set up step sequence and start with first step
        self._current_step_index = 0
        self._activate_current_step()

    def _initialize_steps(self):
        """Initialize all installation steps in order"""
        self._folderStep = GetFolderStep(
            self.installation_settings, self._install_state_variables)
        self._createVenvStep = CreateVenvStep(
            self.installation_settings, self._install_state_variables)

        # Define the complete installation sequence
        self._step_sequence: List = [
            self._folderStep,
            # Additional steps will be added here:
            # self._tokenSetupStep,
            self._createVenvStep,
            # self._installDependenciesStep,
            # self._generateRunScriptsStep,
        ]

    def get_current_step(self):
        """Get the currently active installation step

        Returns:
            Current step object that the GUI should display
        """
        if self._current_step_index < len(self._step_sequence):
            return self._step_sequence[self._current_step_index]
        return None

    def get_step_info(self) -> Dict[str, Any]:
        """Get information about the current step for GUI display

        Returns:
            Dictionary containing step title, description, and progress info
        """
        current_step = self.get_current_step()
        if not current_step:
            return {
                "title": "Installation Complete",
                "description": "All installation steps have been completed successfully.",
                "step_number": len(self._step_sequence),
                "total_steps": len(self._step_sequence),
                "can_complete": True,
                "can_cancel": False,
            }

        return {
            "title": current_step.get_title(),
            "description": current_step.get_description(),
            "hint_text": current_step.get_hint_text(),
            "step_number": self._current_step_index + 1,
            "total_steps": len(self._step_sequence),
            "can_complete": current_step.can_complete(),
            "can_cancel": True,
        }

    def complete_current_step(self) -> bool:
        """Attempt to complete the current step and advance to next

        Returns:
            True if step completed successfully and advanced, False otherwise
        """
        current_step = self.get_current_step()
        if not current_step:
            return False

        # Try to complete the current step
        if current_step.complete_step():
            # Step completed successfully, deactivate current step
            current_step.set_inactive()

            # Advance to next step
            self._current_step_index += 1
            self._activate_current_step()
            return True

        return False

    def cancel_installation(self) -> bool:
        """Cancel the installation process

        Returns:
            True if cancellation was successful
        """
        # Allow current step to clean up if needed
        current_step = self.get_current_step()
        if current_step and hasattr(current_step, 'cancel_step'):
            current_step.cancel_step()

        return True

    def is_installation_complete(self) -> bool:
        """Check if all installation steps have been completed

        Returns:
            True if installation is complete, False if more steps remain
        """
        return self._current_step_index >= len(self._step_sequence)

    def get_installation_state(self) -> Dict[str, Any]:
        """Get the current installation state variables

        Returns:
            Dictionary of state variables shared between steps
        """
        return self._install_state_variables.copy()

    def _activate_current_step(self):
        """Activate the current step in the sequence"""
        current_step = self.get_current_step()
        if current_step:
            current_step.set_active()

    # Legacy method for backward compatibility
    def installation_finished(self) -> bool:
        """Legacy method - check if installation is complete

        Returns:
            True if installation is finished
        """
        return self.is_installation_complete()
