"""
My Application Updater
Standalone updater utility
"""
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

def main():
    # Create update window
    root = tk.Tk()
    root.title("My Application Updater")
    root.geometry("400x200")
    root.resizable(False, False)
    
    # Center the window
    root.eval('tk::PlaceWindow . center')
    
    ttk.Label(root, text="Updating My Application...", font=("", 12)).pack(pady=20)
    
    progress = ttk.Progressbar(root, length=300, mode='indeterminate')
    progress.pack(pady=10)
    progress.start()
    
    status_label = ttk.Label(root, text="Starting update...")
    status_label.pack(pady=10)
    
    def update_library():
        app_dir = Path(__file__).parent
        venv_python = app_dir / ".test_venv" / "Scripts" / "python.exe"
        
        if not venv_python.exists():
            messagebox.showerror("Error", f"Python not found at {venv_python}")
            root.destroy()
            return
        
        try:
            status_label.config(text="Updating requests...")
            root.update()
            
            # Load debug setting from bootstrap config
            bootstrap_config = configparser.ConfigParser()
            bootstrap_config_file = app_dir / "bootstrapper" / "config.ini"
            debug_mode = False
            if bootstrap_config_file.exists():
                bootstrap_config.read(bootstrap_config_file)
                debug_str = bootstrap_config.get('Settings', 'debug', fallback='false')
                debug_mode = debug_str.lower() in ('true', '1', 'yes', 'on')
            
            # Use CREATE_NO_WINDOW only if not in debug mode
            creation_flags = 0 if debug_mode else 0x08000000
            capture_output = not debug_mode  # Don't capture output if in debug mode
            
            result = subprocess.run(
                [str(venv_python), "-m", "pip", "install", "--upgrade", "requests"],
                capture_output=capture_output,
                text=True,
                creationflags=creation_flags
            )
            
            progress.stop()
            
            if result.returncode == 0:
                status_label.config(text="Update completed successfully!")
                messagebox.showinfo("Success", "Update completed successfully!")
            else:
                status_label.config(text="Update failed!")
                messagebox.showerror("Error", f"Update failed:\n{result.stderr}")
            
            root.destroy()
            
        except Exception as e:
            progress.stop()
            status_label.config(text="Update failed!")
            messagebox.showerror("Error", f"Update failed: {e}")
            root.destroy()
    
    # Start update after window is shown
    root.after(1000, update_library)
    root.mainloop()

if __name__ == "__main__":
    main()
