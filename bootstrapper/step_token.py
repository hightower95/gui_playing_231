"""Step 3: Configure Token"""
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import configparser


class TokenStep:
    def __init__(self, wizard):
        self.wizard = wizard
        self.token = wizard.pyirc_token
        self.token_status = None
        self.token_url = self.load_config()

    def load_config(self):
        """Load configuration from config.ini"""
        config = configparser.ConfigParser()
        config_file = Path(__file__).parent / "config.ini"

        try:
            config.read(config_file)
            return config.get('URLs', 'token_url', fallback='https://example.com')
        except Exception as e:
            self.wizard.log(f"Failed to read config.ini: {e}", "warning")
            return 'https://example.com'

    def build_ui(self, parent):
        """Build the UI for token configuration"""
        frame = ttk.Frame(parent)
        frame.pack(fill="x")

        # Instructions and button to open URL
        instruction_frame = ttk.Frame(frame)
        instruction_frame.pack(fill="x", pady=(0, 5))

        ttk.Label(instruction_frame,
                  text="Get your token from the website:").pack(side="left")
        ttk.Button(instruction_frame, text="Open Token URL",
                   command=self.open_token_url).pack(side="left", padx=(5, 0))

        # Token entry
        ttk.Label(frame, text="Paste your token below:").pack(
            anchor="w", pady=(5, 5))

        token_frame = ttk.Frame(frame)
        token_frame.pack(fill="x", pady=(0, 5))

        ttk.Entry(token_frame, textvariable=self.token,
                  width=60).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(token_frame, text="Save Token",
                   command=self.save_token).pack(side="left")

        self.token_status = ttk.Label(
            frame, text="⏸ Not configured", foreground="gray")
        self.token_status.pack(anchor="w")

    def open_token_url(self):
        """Open the token URL in browser"""
        try:
            webbrowser.open(self.token_url)
            self.wizard.log(f"Opened token URL: {self.token_url}")
        except Exception as e:
            self.wizard.log(f"Failed to open URL: {e}", "error")
            messagebox.showerror("Error", f"Failed to open URL: {e}")

    def save_token(self):
        """Validate and save the token"""
        if not self.wizard.step_status["venv"]:
            messagebox.showwarning("Step 2 Required",
                                   "Please complete Step 2 (Create venv) first.")
            return

        token = self.token.get().strip()
        install_dir = Path(self.wizard.install_path.get())

        try:
            if not token:
                self.token_status.config(
                    text="❌ Token is empty", foreground="red")
                self.wizard.step_status["pyirc"] = False
                return

            # Save token to a config file
            config_file = install_dir / ".pyirc"
            config_file.write_text(f"token={token}\n")
            self.wizard.log(f"Token saved to {config_file}")

            self.token_status.config(text="✅ Token saved", foreground="green")
            self.wizard.step_status["pyirc"] = True

        except Exception as e:
            self.wizard.log(f"Token save failed: {e}", "error")
            self.token_status.config(
                text=f"❌ Save failed: {e}", foreground="red")
            self.wizard.step_status["pyirc"] = False

        finally:
            self.wizard.update_progress()

    def auto_detect(self):
        """Auto-detect if token is already configured"""
        install_dir = Path(self.wizard.install_path.get())
        token_file = install_dir / ".pyirc"

        if token_file.exists():
            self.token_status.config(
                text="✅ Token already configured", foreground="green")
            self.wizard.step_status["pyirc"] = True
            self.wizard.log("Auto-detected token config")
