

"""
Install GUI - Simple installation wizard interface using native tkinter

Design Principles:
- Provides a clean frame for each installation step
- Handles step navigation (Next/Cancel buttons)
- Displays step information and progress
- Delegates all installation logic to the InstallConductor
- Uses only native Python libraries (tkinter)
"""
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

from .conductor import InstallConductor


class InstallGUI(tk.Tk):
    """
    Simple installation wizard GUI using native tkinter.

    The GUI is responsible only for presentation and user interaction,
    while all installation logic is handled by the InstallConductor.
    """

    def __init__(self, installation_settings):
        """Initialize the installation GUI

        Args:
            installation_settings: Configuration from install_settings.ini
        """
        super().__init__()
        self.installation_settings = installation_settings

        # Create the conductor to manage installation steps
        self.conductor = InstallConductor(installation_settings)

        # Setup the GUI
        self.setup_ui()
        self.refresh_step_display()

    def setup_ui(self):
        """Setup the main installation wizard interface"""
        self.title("Application Installer")
        self.geometry("840x700")
        self.resizable(False, False)

        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Header section
        self.create_header_section(main_frame)

        # Progress section
        self.create_progress_section(main_frame)

        # Step content frame (where each step displays its UI)
        self.create_step_frame(main_frame)

        # Navigation buttons
        self.create_navigation_section(main_frame)

    def create_header_section(self, parent):
        """Create the header with title and description"""
        # Title
        self.title_label = ttk.Label(parent, text="Installing Application",
                                     font=("Arial", 16, "bold"))
        self.title_label.pack(pady=(0, 5))

        # Description
        self.description_label = ttk.Label(
            parent, text="Setting up your application...")
        self.description_label.pack(pady=(0, 15))

    def create_progress_section(self, parent):
        """Create the step indicator combined with title"""
        # Combined title and step progress frame
        title_progress_frame = ttk.Frame(parent)
        title_progress_frame.pack(fill="x", pady=(0, 10))

        # Title
        self.step_title_label = ttk.Label(title_progress_frame, text="Step Title",
                                          font=("Arial", 14, "bold"))
        self.step_title_label.pack(side="left")

        # Step progress label
        self.progress_label = ttk.Label(
            title_progress_frame, text="Step 1 of 5")
        self.progress_label.pack(side="right")

        # Progress bar
        self.progress_bar = ttk.Progressbar(parent, mode='determinate')
        self.progress_bar.pack(fill="x", pady=(0, 15))

    def create_step_frame(self, parent):
        """Create the frame where individual steps display their content"""
        # Step frame with border
        self.step_frame = ttk.LabelFrame(
            parent, text="Step Content", padding=15)
        self.step_frame.pack(fill="both", expand=True, pady=(0, 15))

        # Hint text area
        self.hint_label = ttk.Label(self.step_frame, text="",
                                    font=("Arial", 9, "italic"),
                                    wraplength=800)
        self.hint_label.pack(fill="x", pady=(0, 10))

        # Content area where steps can add their widgets
        self.step_content_frame = ttk.Frame(self.step_frame)
        self.step_content_frame.pack(fill="both", expand=True)

    def create_navigation_section(self, parent):
        """Create the navigation buttons (Complete Step / Cancel)"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x")

        # Cancel button (on left)
        self.cancel_button = ttk.Button(button_frame, text="Cancel Installation",
                                        command=self.cancel_installation)
        self.cancel_button.pack(side="left")

        # Complete step button (on right - primary action)
        self.complete_button = ttk.Button(button_frame, text="Complete Step",
                                          command=self.complete_current_step)
        self.complete_button.pack(side="right")

    def refresh_step_display(self):
        """Refresh the display to show current step information"""
        step_info = self.conductor.get_step_info()

        # Update header
        self.title_label.config(text="Installing Application")
        self.description_label.config(text=step_info.get(
            "description", "Setting up your application..."))

        # Update step title and progress
        self.step_title_label.config(text=step_info.get("title", "Step"))
        step_num = step_info.get("step_number", 1)
        total_steps = step_info.get("total_steps", 1)
        self.progress_label.config(text=f"Step {step_num} of {total_steps}")

        progress_percent = int((step_num / total_steps) * 100)
        self.progress_bar['value'] = progress_percent

        # Update hint text
        hint_text = step_info.get("hint_text", "")
        self.hint_label.config(text=hint_text)
        if hint_text:
            self.hint_label.pack(fill="x", pady=(0, 10))
        else:
            self.hint_label.pack_forget()

        # Clear and populate step content FIRST
        self.clear_step_content()
        self.populate_step_content()

        # Update button states AFTER widgets are created and step is initialized
        # Get fresh step info after widget creation
        step_info = self.conductor.get_step_info()
        can_complete = step_info.get("can_complete", False)
        self.complete_button.config(
            state="normal" if can_complete else "disabled")

        can_cancel = step_info.get("can_cancel", True)
        self.cancel_button.config(state="normal" if can_cancel else "disabled")

        # Update button text for final step
        if self.conductor.is_installation_complete():
            self.complete_button.config(text="Finish")
        else:
            self.complete_button.config(text="Complete Step")

    def clear_step_content(self):
        """Clear the step content area and properly tear down previous step components"""
        # Get current step before clearing to call cleanup if available
        current_step = self.conductor.get_current_step()
        if current_step and hasattr(current_step, 'cleanup_widgets'):
            current_step.cleanup_widgets()

        # Remove all widgets from step content frame
        for widget in self.step_content_frame.winfo_children():
            widget.destroy()

        # Force update
        self.step_content_frame.update()

    def populate_step_content(self):
        """Populate the step content area with current step's widgets"""
        current_step = self.conductor.get_current_step()
        if current_step and hasattr(current_step, 'create_widgets'):
            # Let the step create its own widgets in the provided frame
            current_step.create_widgets(self.step_content_frame)
        else:
            # Default content if step doesn't provide widgets
            default_label = ttk.Label(self.step_content_frame,
                                      text="Step content will appear here...")
            default_label.pack(expand=True)

    def complete_current_step(self):
        """Handle Complete Step button click"""
        if self.conductor.is_installation_complete():
            # Installation is complete, close the installer
            self.finish_installation()
            return

        # Try to complete the current step
        success = self.conductor.complete_current_step()

        if success:
            # Step completed, refresh display for next step
            self.refresh_step_display()

            # Check if installation is now complete
            if self.conductor.is_installation_complete():
                self.show_completion_message()
        else:
            # Step could not be completed, show error
            messagebox.showwarning(
                "Step Incomplete",
                "Please complete all required fields before proceeding to the next step."
            )

    def cancel_installation(self):
        """Handle Cancel Installation button click"""
        reply = messagebox.askyesno(
            "Cancel Installation",
            "Are you sure you want to cancel the installation?"
        )

        if reply:
            self.conductor.cancel_installation()
            self.destroy()

    def show_completion_message(self):
        """Show installation completion message"""
        messagebox.showinfo(
            "Installation Complete",
            "The application has been installed successfully!\n\nYou can now close this installer."
        )

    def finish_installation(self):
        """Finish the installation and close the installer"""
        self.destroy()

    def launch(self):
        """Launch the installation GUI"""
        self.mainloop()
        return True


def launch_installer_gui(installation_settings):
    """Launch the installer GUI application

    Args:
        installation_settings: Configuration from install_settings.ini

    Returns:
        bool: True if installation completed successfully, False otherwise
    """
    # Create and show installer GUI
    installer_gui = InstallGUI(installation_settings)
    installer_gui.launch()

    # Return success based on whether installation completed
    return installer_gui.conductor.is_installation_complete()
