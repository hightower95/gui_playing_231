"""
Logging utilities for upgrade events and application logging
"""
import os
import platform
from datetime import datetime
from pathlib import Path
from typing import Any


def log_upgrade_event(app_dir: Path, event_type: str, **kwargs):
    """Log upgrade events to upgrade_history.log"""
    try:
        log_file = app_dir / "upgrade_history.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Format event data
        event_data = " | ".join([str(k) + "=" + str(v) for k, v in kwargs.items()])
        log_entry = timestamp + " | " + event_type + " | " + event_data + "\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception:
        pass  # Silent fail for logging


def write_comprehensive_log(app_dir: Path, config: dict, venv_python: Path, result: Any, runner_script: str):
    """Write comprehensive application log with all details"""
    log_file = app_dir / "last_run_log.txt"
    launch_config_file = app_dir / "launch_config.ini"
    
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            # Header with timestamp
            f.write("=" * 80 + "\n")
            f.write("=== ProductivityApp - COMPREHENSIVE RUN LOG ===\n")
            f.write("=== " + str(datetime.now()) + " ===\n")
            f.write("=" * 80 + "\n\n")
            
            # System Information
            f.write("=== SYSTEM INFORMATION ===\n")
            f.write("Platform: " + platform.platform() + "\n")
            f.write("Python Version: " + platform.python_version() + "\n")
            f.write("Architecture: " + platform.machine() + "\n")
            f.write("Processor: " + platform.processor() + "\n")
            f.write("Working Directory: " + str(app_dir) + "\n")
            f.write("\n")
            
            # Virtual Environment Information  
            f.write("=== VIRTUAL ENVIRONMENT ===\n")
            f.write("Virtual Environment Path: " + str(venv_python) + "\n")
            f.write("Venv Exists: " + str(venv_python.exists()) + "\n")
            if venv_python.exists():
                f.write("Venv Directory: " + str(venv_python.parent.parent) + "\n")
            else:
                f.write("ERROR: Virtual environment not found!\n")
            f.write("\n")
            
            # Configuration Information
            f.write("=== CONFIGURATION ===\n")
            for key, value in config.items():
                f.write(f"{key}: {value}\n")
            f.write("Launch Config File: " + str(launch_config_file) + "\n")
            f.write("Launch Config Exists: " + str(launch_config_file.exists()) + "\n")
            
            # Read and log the actual launch config content
            if launch_config_file.exists():
                f.write("\n--- Launch Config Content ---\n")
                try:
                    with open(launch_config_file, 'r', encoding='utf-8') as config_file:
                        f.write(config_file.read())
                except Exception as e:
                    f.write("Error reading config file: " + str(e) + "\n")
                f.write("--- End Launch Config ---\n")
            f.write("\n")
            
            # Upgrade History
            f.write("=== UPGRADE HISTORY ===\n")
            upgrade_history_file = app_dir / "upgrade_history.log"
            if upgrade_history_file.exists():
                try:
                    with open(upgrade_history_file, 'r', encoding='utf-8') as history_file:
                        recent_lines = history_file.readlines()[-10:]  # Last 10 events
                        f.write("--- Recent Upgrade Events ---\n")
                        for line in recent_lines:
                            f.write(line)
                        f.write("--- End Upgrade History ---\n")
                except Exception as e:
                    f.write("Error reading upgrade history: " + str(e) + "\n")
            else:
                f.write("No upgrade history file found\n")
            f.write("\n")
            
            # Execution Information
            f.write("=== EXECUTION DETAILS ===\n")
            f.write("Exit Code: " + str(result.returncode) + "\n")
            f.write("Command: " + str(venv_python) + " -c <runner_script>\n")
            f.write("Working Directory: " + str(app_dir) + "\n")
            f.write("\n")
            
            # Runner Script Content
            f.write("=== RUNNER SCRIPT ===\n")
            f.write(runner_script)
            f.write("\n=== END RUNNER SCRIPT ===\n\n")
            
            # Application Output
            f.write("=== APPLICATION OUTPUT ===\n")
            
            if hasattr(result, 'stdout') and result.stdout:
                f.write("--- STDOUT ---\n")
                f.write(result.stdout)
                f.write("\n--- END STDOUT ---\n\n")
            else:
                f.write("--- STDOUT ---\n")
                f.write("(No stdout output)\n\n")
            
            if hasattr(result, 'stderr') and result.stderr:
                f.write("--- STDERR ---\n")
                f.write(result.stderr)
                f.write("\n--- END STDERR ---\n\n")
            else:
                f.write("--- STDERR ---\n")
                f.write("(No stderr output)\n\n")
            
            # Footer
            f.write("=" * 80 + "\n")
            f.write("=== END OF LOG ===\n")
            f.write("=" * 80 + "\n")
            
    except Exception as log_error:
        print("Warning: Could not write comprehensive log file: " + str(log_error))