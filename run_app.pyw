"""
ProductivityApp Main Launcher
Upgrades library and runs the application using the virtual environment
"""
import subprocess
import sys
from pathlib import Path
import configparser
import os

def main():
    # Get paths
    app_dir = Path(__name__).parent
    venv_python = app_dir / ".test_venv" / "Scripts" / "python.exe"
    
    if not venv_python.exists():
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Python not found at {venv_python}")
        return
    
    # Load debug setting from launch config
    launch_config_parser = configparser.ConfigParser()
    launch_config_file = app_dir / "launch_config.ini"
    enable_log = False
    if launch_config_file.exists():
        launch_config_parser.read(launch_config_file)
        enable_log_str = launch_config_parser.get('Settings', 'enable_log', fallback='false')
        enable_log = enable_log_str.lower() in ('true', '1', 'yes', 'on')
    
    # Windows flag to hide console
    CREATE_NO_WINDOW = 0x08000000
    creation_flags = CREATE_NO_WINDOW
    
    try:
        # Step 1: Upgrade the library
        upgrade_result = subprocess.run(
            [str(venv_python), "-m", "pip", "install", "--upgrade", "requests"],
            capture_output=True,  # Always capture to check for errors
            text=True,
            creationflags=creation_flags
        )
        
        if upgrade_result.returncode != 0:
            error_msg = "Failed to upgrade library requests"
            if upgrade_result.stderr:
                error_msg += ": " + upgrade_result.stderr.strip()
            elif upgrade_result.stdout:
                error_msg += ": " + upgrade_result.stdout.strip()
            raise Exception(error_msg)
        
        # Step 2: Create a runner script that handles launch config  
        runner_script = '''
import sys
import configparser
from pathlib import Path

# Load launch config
app_dir = Path(__name__).parent
config = configparser.ConfigParser()
config_file = app_dir / "launch_config.ini"
launch_config = dict()
if config_file.exists():
    config.read(config_file)
    # Read from Settings section (preferred) or fall back to DEFAULT
    if config.has_section('DEFAULT'):
        launch_config = dict(config['DEFAULT'])

# Import and run the library
try:
    import requests
    requests.run(launch_config)

    print("Python executable: " + str(sys.executable))
    raise
except Exception as e:
    print("Runtime error: " + str(e))
    raise
'''
        
        # Step 3: Run the library using the venv Python with the runner script
        # Always capture output for logging purposes
        result = subprocess.run(
            [str(venv_python), "-c", runner_script],
            cwd=str(app_dir),  # Set working directory
            capture_output=True,  # Always capture for logging
            text=True,  # Decode output as text
            creationflags=creation_flags
        )
        
        # Comprehensive logging to file (only if enabled)
        if enable_log:
            log_file = app_dir / "last_run_log.txt"
            try:
                import datetime
                import platform
                with open(log_file, 'w', encoding='utf-8') as f:
                    # Header with timestamp
                    f.write("=" * 80 + "\\n")
                    f.write("=== ProductivityApp - COMPREHENSIVE RUN LOG ===\\n")
                    f.write("=== " + str(datetime.datetime.now()) + " ===\\n")
                    f.write("=" * 80 + "\\n\\n")
                    
                    # System Information
                    f.write("=== SYSTEM INFORMATION ===\\n")
                    f.write("Platform: " + platform.platform() + "\\n")
                    f.write("Python Version: " + platform.python_version() + "\\n")
                    f.write("Architecture: " + platform.machine() + "\\n")
                    f.write("Processor: " + platform.processor() + "\\n")
                    f.write("Working Directory: " + str(app_dir) + "\\n")
                    f.write("\\n")
                    
                    # Virtual Environment Information  
                    f.write("=== VIRTUAL ENVIRONMENT ===\\n")
                    f.write("Virtual Environment Path: " + str(venv_python) + "\\n")
                    f.write("Venv Exists: " + str(venv_python.exists()) + "\\n")
                    if venv_python.exists():
                        f.write("Venv Directory: " + str(venv_python.parent.parent) + "\\n")
                    else:
                        f.write("ERROR: Virtual environment not found!\\n")
                    f.write("\\n")
                    
                    # Configuration Information
                    f.write("=== CONFIGURATION ===\\n")
                    f.write("App Name: ProductivityApp\\n")
                    f.write("Library Name: requests\\n") 
                    f.write("Venv Directory Name: .test_venv\\n")

                    f.write("Launch Config File: " + str(launch_config_file) + "\\n")
                    f.write("Launch Config Exists: " + str(launch_config_file.exists()) + "\\n")
                    
                    # Read and log the actual launch config content
                    if launch_config_file.exists():
                        f.write("\\n--- Launch Config Content ---\\n")
                        try:
                            with open(launch_config_file, 'r', encoding='utf-8') as config_file:
                                f.write(config_file.read())
                        except Exception as e:
                            f.write("Error reading config file: " + str(e) + "\\n")
                        f.write("--- End Launch Config ---\\n")
                    f.write("\\n")
                    
                    # Execution Information
                    f.write("=== EXECUTION DETAILS ===\\n")
                    f.write("Exit Code: " + str(result.returncode) + "\\n")
                    f.write("Command: " + str(venv_python) + " -c <runner_script>\\n")
                    f.write("Working Directory: " + str(app_dir) + "\\n")
                    f.write("Creation Flags: " + str(creation_flags) + "\\n")
                    f.write("\\n")
                
                    # Runner Script Content
                    f.write("=== RUNNER SCRIPT ===\\n")
                    f.write(runner_script)
                    f.write("\\n=== END RUNNER SCRIPT ===\\n\\n")
                    
                    # Application Output - Always log captured output
                    f.write("=== APPLICATION OUTPUT ===\\n")
                    
                    # Always log stdout (captured in both debug and normal mode)
                    if hasattr(result, 'stdout') and result.stdout:
                        f.write("--- STDOUT ---\\n")
                        f.write(result.stdout)
                        f.write("\\n--- END STDOUT ---\\n\\n")
                    else:
                        f.write("--- STDOUT ---\\n")
                        f.write("(No stdout output)\\n\\n")
                    
                    # Always log stderr (captured in both debug and normal mode)  
                    if hasattr(result, 'stderr') and result.stderr:
                        f.write("--- STDERR ---\\n")
                        f.write(result.stderr)
                        f.write("\\n--- END STDERR ---\\n\\n")
                    else:
                        f.write("--- STDERR ---\\n")
                        f.write("(No stderr output)\\n\\n")
                    

                    
                    # Footer
                    f.write("=" * 80 + "\\n")
                    f.write("=== END OF LOG ===\\n")
                    f.write("=" * 80 + "\\n")
                    
            except Exception as log_error:
                print("Warning: Could not write comprehensive log file: " + str(log_error))

        
        # If there was an error, show details to user
        if result.returncode != 0:
            error_msg = "Application failed"
            error_details = ""
            
            # Collect error details
            if result.stderr:
                error_details = result.stderr.strip()
            elif result.stdout:
                error_details = result.stdout.strip()
            
            if error_details:
                error_msg += f":\n\n{error_details}"
            else:
                error_msg += f" with exit code: {result.returncode}"
            
            # Always show error to user via message box
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Application Error", error_msg)
            return
        
    except Exception as e:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Startup Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main()