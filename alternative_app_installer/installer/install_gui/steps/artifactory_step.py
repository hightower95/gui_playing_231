
"""
Artifactory Configuration Step - Handles token input and pip configuration validation

This step handles:
- Displaying Artifactory configuration instructions
- Allowing user to open Artifactory webpage and guides
- Multi-line text input for pip configuration
- Validating the pip configuration format
- Saving configuration to .pyirc file
- Uses only native Python libraries (tkinter)
"""
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import configparser
from pathlib import Path
import logging

from .base_step import BaseStep
from ..utilities.pyirc_bootstrapper import (
    pip_exists_with_correct_sections,
    get_howto_configure_index_url,
    is_valid_index_url_value,
    get_pip_config,
    save_pip_config
)


class ArtifactorySetupStep(BaseStep):
    """Artifactory Configuration Step - Handles token input and pip configuration validation."""

    def __init__(self, installation_settings, shared_state):
        super().__init__(installation_settings, shared_state)

        # Configuration URLs
        self.token_url = self.installation_settings.get(
            'Step_Artifactory', 'token_url', fallback='https://example.com/get-token')
        self.guide_url = self.installation_settings.get(
            'Step_Artifactory', 'guide_url', fallback='https://example.com/help')

        # Instructions text
        self.howto_instructions = get_howto_configure_index_url()

        # UI components (will be set in create_widgets)
        self.url_entry = None
        self.index_url_status = None
        self.token_status = None
        self.showing_placeholder = False

        # State
        self._is_configured = False

    # ========================================================================
    # Required BaseStep Methods
    # ========================================================================

    def get_title(self) -> str:
        return "Configure Artifactory"

    def get_description(self) -> str:
        return "Set up access to your organization's private package repository"

    def get_hint_text(self) -> str:
        return "Follow the instructions to get your Artifactory configuration"

    def can_complete(self) -> bool:
        """Check if step can be completed"""
        return self._is_configured or pip_exists_with_correct_sections()

    def create_widgets(self, parent_frame: tk.Frame):
        """Build the UI for Artifactory configuration"""
        frame = ttk.Frame(parent_frame)
        frame.pack(fill="both", expand=True)

        # Check if already configured
        if self._check_existing_configuration():
            return

        # Instructions section
        instruction_frame = ttk.Frame(frame)
        instruction_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(instruction_frame, text="Artifactory Configuration Required:",
                  font=("Arial", 10, "bold")).pack(anchor="w")

        # Button row
        button_frame = ttk.Frame(instruction_frame)
        button_frame.pack(fill="x", pady=(5, 0))

        # How-to button with tooltip
        howto_btn = ttk.Button(button_frame, text="How To Configure",
                               command=self._show_instructions)
        howto_btn.pack(side="left", padx=(0, 5))
        self._create_tooltip(howto_btn, self.howto_instructions)

        ttk.Button(button_frame, text="Open Artifactory",
                   command=self._open_token_url).pack(side="left", padx=(0, 5))

        ttk.Button(button_frame, text="Open Guide",
                   command=self._open_guide_url).pack(side="left")

        # Input section
        input_frame = ttk.LabelFrame(
            frame, text="Pip Configuration", padding=10)
        input_frame.pack(fill="both", expand=True, pady=(0, 15))

        ttk.Label(input_frame, text="Paste the full text from the first section of 'Install'",
                  font=("Arial", 9)).pack(anchor="w", pady=(0, 5))

        # Text entry with scrollbar
        text_frame = ttk.Frame(input_frame)
        text_frame.pack(fill="both", expand=True)

        self.url_entry = tk.Text(text_frame, height=4, width=80, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(
            text_frame, orient="vertical", command=self.url_entry.yview)
        self.url_entry.configure(yscrollcommand=scrollbar.set)

        self.url_entry.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Setup placeholder text
        self.placeholder_text = "[global]\nindex-url = https://u3uajiojdwaoijdwadkawkdi9218jhn@example.com/artifactory/api/pypi/common-pypi/simple"
        self._setup_placeholder()

        # Bind events
        self.url_entry.bind('<KeyRelease>', self._validate_url_input)
        self.url_entry.bind('<FocusIn>', self._on_entry_focus_in)
        self.url_entry.bind('<FocusOut>', self._on_entry_focus_out)
        self.url_entry.bind('<Button-1>', self._on_entry_click)

        # Status labels
        status_frame = ttk.Frame(frame)
        status_frame.pack(fill="x")

        self.index_url_status = ttk.Label(
            status_frame, text="⏸ Not configured", foreground="gray")
        self.index_url_status.pack(anchor="w", pady=(5, 2))

        self.token_status = ttk.Label(status_frame, text="", foreground="gray")
        self.token_status.pack(anchor="w")

        # Initial validation
        self._validate_url_input()

    def complete_step(self) -> bool:
        """Complete the Artifactory configuration step"""
        logging.info("Artifactory step: Attempting to complete step")

        if self._is_configured or pip_exists_with_correct_sections():
            # Already configured - just save state
            logging.info(
                "Artifactory step: Already configured, marking as complete")
            self.update_shared_state("artifactory_configured", True)
            self.mark_completed()
            return True

        # Check if placeholder is still showing
        if hasattr(self, 'showing_placeholder') and self.showing_placeholder:
            logging.warning(
                "Artifactory step: User has not replaced placeholder text")
            messagebox.showwarning(
                "No Input",
                "Please replace the example text with your actual Artifactory configuration.")
            return False

        # Get and validate input
        pyirc_entry_value = self.url_entry.get("1.0", tk.END).strip()
        logging.debug(
            f"Artifactory step: User input received (length: {len(pyirc_entry_value)} chars)")

        is_valid, error_msg = is_valid_index_url_value(pyirc_entry_value)

        if not is_valid:
            logging.error(
                f"Artifactory step: Invalid configuration - {error_msg}")
            messagebox.showerror("Invalid Configuration", error_msg)
            return False

        logging.info(
            "Artifactory step: Configuration validation successful, saving to .pyirc")

        # Save configuration
        try:
            config = get_pip_config(create_if_not_exists=True)
            temp_config = configparser.ConfigParser()
            temp_config.read_string(pyirc_entry_value)

            # Remove existing index-url if present
            if config.has_option('global', 'index-url'):
                existing_url = config.get('global', 'index-url')
                logging.info(
                    f"Artifactory step: Overwriting existing index-url: {existing_url[:50]}...")
                config.remove_option('global', 'index-url')

            # Merge parsed configuration
            for section_name in temp_config.sections():
                if not config.has_section(section_name):
                    config.add_section(section_name)

                for key, value in temp_config[section_name].items():
                    config.set(section_name, key, value)

            # Save configuration
            if save_pip_config(config):
                self._is_configured = True
                self.update_shared_state("artifactory_configured", True)
                self.mark_completed()

                if self.token_status:
                    self.token_status.config(
                        text="✅ Artifactory configured successfully", foreground="green")

                messagebox.showinfo("Success",
                                    "Artifactory has been configured successfully!\n"
                                    "Pip will now use your private package repository.")
                return True
            else:
                raise Exception("Failed to save pip configuration")

        except Exception as e:
            error_msg = f"Configuration failed: {str(e)}"
            if self.token_status:
                self.token_status.config(
                    text=f"❌ {error_msg[:50]}", foreground="red")
            messagebox.showerror("Configuration Error", error_msg)
            return False

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _check_existing_configuration(self) -> bool:
        """Check if Artifactory is already configured and update UI accordingly"""
        # Check simulation mode first
        if self._check_simulation_mode():
            return True

        # Check actual configuration
        if pip_exists_with_correct_sections():
            self._is_configured = True
            self._show_configured_state()
            self.update_shared_state("artifactory_configured", True)
            self.mark_completed()
            return True

        return False

    def _check_simulation_mode(self) -> bool:
        """Check if simulation mode is enabled"""
        try:
            if self.installation_settings.getboolean('DEV', 'simulate_artifactory_complete', fallback=False):
                self._is_configured = True
                self._show_simulated_state()
                self.update_shared_state("artifactory_configured", True)
                self.mark_completed()
                return True
        except Exception:
            pass
        return False

    def _show_configured_state(self):
        """Show that Artifactory is already configured"""
        # Create simple label instead of full UI
        label = ttk.Label(self.parent if hasattr(self, 'parent') else None,
                          text="✅ Artifactory already configured",
                          foreground="green", font=("Arial", 10, "bold"))
        if label.master:
            label.pack(anchor="w", pady=(0, 5))

    def _show_simulated_state(self):
        """Show simulated configuration state"""
        # Create simple label for simulation
        label = ttk.Label(self.parent if hasattr(self, 'parent') else None,
                          text="✅ Artifactory (simulated)",
                          foreground="orange", font=("Arial", 10, "bold"))
        if label.master:
            label.pack(anchor="w", pady=(0, 5))

    def _setup_placeholder(self):
        """Setup the placeholder text in the entry widget"""
        self.url_entry.insert("1.0", self.placeholder_text)
        self.url_entry.config(foreground="gray")
        self.showing_placeholder = True

    def _on_entry_focus_in(self, event):
        """Handle focus in - remove placeholder if present"""
        if self.showing_placeholder:
            self.url_entry.delete("1.0", tk.END)
            self.url_entry.config(foreground="black")
            self.showing_placeholder = False

    def _on_entry_focus_out(self, event):
        """Handle focus out - restore placeholder if empty"""
        content = self.url_entry.get("1.0", tk.END).strip()
        if not content:
            self.url_entry.insert("1.0", self.placeholder_text)
            self.url_entry.config(foreground="gray")
            self.showing_placeholder = True

    def _on_entry_click(self, event):
        """Handle mouse click - clear placeholder if present"""
        if self.showing_placeholder:
            self.url_entry.delete("1.0", tk.END)
            self.url_entry.config(foreground="black")
            self.showing_placeholder = False

    def _validate_url_input(self, event=None):
        """Validate the index-url as user types"""
        if not self.index_url_status:
            return

        # Skip validation if showing placeholder
        if hasattr(self, 'showing_placeholder') and self.showing_placeholder:
            self._is_configured = False
            self.index_url_status.config(
                text="⏸ Enter configuration", foreground="gray")
            self.notify_completion_state_changed()
            return

        url = self.url_entry.get("1.0", tk.END).strip()

        if not url:
            self._is_configured = False
            self.index_url_status.config(
                text="⏸ Enter configuration", foreground="gray")
            self.notify_completion_state_changed()
            return

        is_valid, error_msg = is_valid_index_url_value(url)

        if is_valid:
            self._is_configured = True
            self.index_url_status.config(
                text="✅ Valid configuration", foreground="green")
        else:
            self._is_configured = False
            self.index_url_status.config(
                text=f"❌ {error_msg}", foreground="red")

        self.notify_completion_state_changed()

    def _show_instructions(self):
        """Show detailed instructions in a popup"""
        messagebox.showinfo(
            "Artifactory Configuration Instructions", self.howto_instructions)

    def _open_token_url(self):
        """Open the Artifactory token URL"""
        try:
            logging.info(
                f"Artifactory step: Opening token URL: {self.token_url}")
            webbrowser.open(self.token_url)
        except Exception as e:
            logging.error(f"Artifactory step: Failed to open token URL: {e}")
            messagebox.showerror("Error", f"Failed to open URL: {e}")

    def _open_guide_url(self):
        """Open the Artifactory guide URL"""
        try:
            logging.info(
                f"Artifactory step: Opening guide URL: {self.guide_url}")
            webbrowser.open(self.guide_url)
        except Exception as e:
            logging.error(f"Artifactory step: Failed to open guide URL: {e}")
            messagebox.showerror("Error", f"Failed to open URL: {e}")

    def _create_tooltip(self, widget, text):
        """Create a tooltip that shows on hover"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            tooltip.configure(background="lightyellow")

            # Create a frame for better layout
            frame = ttk.Frame(tooltip)
            frame.pack(padx=5, pady=5)

            # Multi-line text support with improved formatting
            lines = text.split('\n')
            for line in lines:
                if line.strip():
                    label = tk.Label(frame, text=line, background="lightyellow",
                                     font=("Consolas", 9), justify="left", anchor="w")
                    label.pack(anchor="w", fill="x")
                else:
                    # Add spacing for empty lines
                    spacer = tk.Label(
                        frame, text="", background="lightyellow", height=1)
                    spacer.pack()

            # Add border to the whole tooltip
            tooltip.configure(relief="solid", borderwidth=1)
            widget.tooltip = tooltip

        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
