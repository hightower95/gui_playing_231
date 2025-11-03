"""Step 3: Configure PyIRC"""
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import configparser
from pyirc_bootstrapper import (
    pip_exists_with_correct_sections,
    get_howto_configure_index_url,
    is_valid_index_url_value,
    get_pip_config,
    save_pip_config
)


class TokenStep:
    """PyIRC Configuration Step - Handles token input and pip configuration validation."""

    def __init__(self, parent):
        self.parent = parent
        self.wizard = parent  # Reference to main wizard
        self.token_var = None
        self.url_var = None
        self.config = configparser.ConfigParser()

        # Initialize UI variables
        self.index_url = tk.StringVar()
        self.token_url = self.load_config()
        self.howto_instructions = get_howto_configure_index_url()

        # UI components (will be set in build_ui)
        self.url_entry = None
        self.index_url_status = None
        self.token_status = None

    def load_config(self):
        """Load configuration from config.ini"""
        config = configparser.ConfigParser()
        config_file = Path(__file__).parent / "config.ini"

        try:
            config.read(config_file)
            return config.get('URLs', 'token_url', fallback='https://example.com')
        except Exception as e:
            # Log error if wizard is available, otherwise just return default
            if hasattr(self, 'wizard'):
                self.wizard.log(f"Failed to read config.ini: {e}", "warning")
            return 'https://example.com'

    def build_ui(self, parent):
        """Build the UI for PyIRC configuration"""
        frame = ttk.Frame(parent)
        frame.pack(fill="x")

        # Check if pip config already exists
        if pip_exists_with_correct_sections():
            # Already configured
            ttk.Label(frame, text="✅ PyIRC already configured",
                      foreground="green", font=("", 10, "bold")).pack(anchor="w", pady=(0, 5))
            self.wizard.step_status["pyirc"] = True
            self.wizard.update_progress()  # Update progress when step is detected as complete
            return

        # Instructions section with tooltip
        instruction_frame = ttk.Frame(frame)
        instruction_frame.pack(fill="x", pady=(0, 5))

        ttk.Label(instruction_frame, text="PyIRC Configuration Required:").pack(
            side="left")

        # How-to button with tooltip
        howto_btn = ttk.Button(instruction_frame, text="How To Configure",
                               command=self.show_instructions)
        howto_btn.pack(side="left", padx=(5, 0))

        # Tooltip for hover
        self.create_tooltip(howto_btn, self.howto_instructions)

        ttk.Button(instruction_frame, text="Open Artifactory",
                   command=self.open_token_url).pack(side="left", padx=(5, 0))

        # Index URL entry
        ttk.Label(frame, text="Paste the full text from the first section of 'Install'").pack(
            anchor="w", pady=(10, 5))

        url_frame = ttk.Frame(frame)
        url_frame.pack(fill="x", pady=(0, 5))

        # Use Text widget for multi-line input
        self.url_entry = tk.Text(url_frame, height=2, width=80, wrap=tk.WORD)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.url_entry.bind('<KeyRelease>', self.validate_url_input)

        ttk.Button(url_frame, text="Save",
                   command=self.configure_pyirc).pack(side="left")

        # Status labels
        self.index_url_status = ttk.Label(
            frame, text="⏸ Not configured", foreground="gray")
        self.index_url_status.pack(anchor="w", pady=(2, 0))

        self.token_status = ttk.Label(frame, text="", foreground="gray")
        self.token_status.pack(anchor="w")

    def create_tooltip(self, widget, text):
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
                if line.strip():  # Skip empty lines for display
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

    def show_instructions(self):
        """Show detailed instructions in a popup"""
        messagebox.showinfo(
            "PyIRC Configuration Instructions", self.howto_instructions)

    def open_token_url(self):
        """Open the PyIRC website"""
        try:
            webbrowser.open(self.token_url)
            self.wizard.log(f"Opened PyIRC URL: {self.token_url}")
        except Exception as e:
            self.wizard.log(f"Failed to open URL: {e}", "error")
            messagebox.showerror("Error", f"Failed to open URL: {e}")

    def validate_url_input(self, event=None):
        """Validate the index-url as user types"""
        # Get text from Text widget (different from Entry widget)
        url = self.url_entry.get("1.0", tk.END).strip()

        if not url:
            self.index_url_status.config(
                text="⏸ Enter index-url", foreground="gray")
            return

        is_valid, error_msg = is_valid_index_url_value(url)

        if is_valid:
            self.index_url_status.config(
                text="✅ Valid index-url", foreground="green")
        else:
            self.index_url_status.config(
                text=f"❌ {error_msg}", foreground="red")

    def configure_pyirc(self):
        """Configure PyIRC with the provided index-url"""
        if not self.wizard.step_status["venv"]:
            messagebox.showwarning("Step 2 Required",
                                   "Please complete Step 2 (Create venv) first.")
            return

        # Get text from Text widget

        pyirc_entry_value = self.url_entry.get("1.0", tk.END).strip()

        # Validate URL
        is_valid, error_msg = is_valid_index_url_value(pyirc_entry_value)
        if not is_valid:
            messagebox.showerror("Invalid URL", error_msg)
            return

        try:
            # Get or create pip config
            config = get_pip_config(create_if_not_exists=True)
            # Parse the pyirc_entry_value as a config string
            temp_config = configparser.ConfigParser()
            temp_config.read_string(pyirc_entry_value)

            if config.has_option('global', 'index-url'):
                self.wizard.log(
                    f"Overwriting existing index-url ({config.get('global', 'index-url')}) from section [global]")
                config.remove_option('global', 'index-url')
            # Merge the parsed config with existing config
            for section_name in temp_config.sections():
                if not config.has_section(section_name):
                    config.add_section(section_name)

                for key, value in temp_config[section_name].items():
                    config.set(section_name, key, value)
            # Add the [global] section with index-url
            # if not config.has_section('global'):
            #     config.add_section('global')

            # config.set('global', 'index-url', url)

            # Save the configuration
            if save_pip_config(config):
                self.wizard.log(
                    f"PyIRC configured with index-url: {pyirc_entry_value}")
                self.token_status.config(
                    text="✅ PyIRC configured successfully", foreground="green")
                self.wizard.step_status["pyirc"] = True
                self.wizard.update_progress()

                messagebox.showinfo("Success",
                                    "PyIRC has been configured successfully!\n"
                                    "Pip will now use your private package repository.")
            else:
                raise Exception("Failed to save pip configuration")

        except Exception as e:
            self.wizard.log(f"PyIRC configuration failed: {e}", "error")
            self.token_status.config(
                text=f"❌ Configuration failed: {str(e)[:50]}", foreground="red")
            self.wizard.step_status["pyirc"] = False

    def auto_detect(self):
        """Auto-detect if PyIRC is already configured"""
        if pip_exists_with_correct_sections():
            # Don't rebuild UI if already shown as configured
            if hasattr(self, 'token_status') and self.token_status:
                self.token_status.config(
                    text="✅ PyIRC already configured", foreground="green")
            self.wizard.step_status["pyirc"] = True
            self.wizard.log("Auto-detected PyIRC configuration")
            # Update progress to reflect the completed step
            self.wizard.update_progress()
