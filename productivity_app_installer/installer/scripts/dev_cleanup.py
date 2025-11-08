"""
Bootstrap Development Cleanup Tool
Removes files created during development/testing of the bootstrap installer
"""

from tkinter import messagebox, ttk
import tkinter as tk
import os
import shutil
from pathlib import Path
import configparser
import sys
from constants import BOOTSTRAP_CONFIG_FILE, REQUIRED_FILES, DEFAULT_VENV_DIR


class BootstrapCleanup:


class BootstrapCleanup:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.project_dir = self.script_dir.parent.parent
        self.files_to_remove = []
        self.dirs_to_remove = []
        self.venv_dir_name = self.get_venv_dir_name()
        self.app_name = self.get_app_name()
        self.load_config()
        self.identify_cleanup_targets()

    def get_venv_dir_name(self):
        """Load venv directory name from installation_settings.ini"""
        config = configparser.ConfigParser()
        config_file = self.script_dir.parent / BOOTSTRAP_CONFIG_FILE

        try:
            config.read(config_file)
            return config.get('Paths', 'venv_dir', fallback=DEFAULT_VENV_DIR)
        except Exception:
            return DEFAULT_VENV_DIR

    def get_app_name(self):
        """Load app name from installation_settings.ini"""
        config = configparser.ConfigParser()
        config_file = self.script_dir.parent / BOOTSTRAP_CONFIG_FILE

        try:
            config.read(config_file)
            return config.get('Settings', 'app_name', fallback='My Application')
        except Exception:
            return 'My Application'

    def load_config(self):
        """Load configuration to understand what was created"""
        config = configparser.ConfigParser()
        config_file = self.script_dir.parent / "installation_settings.ini"

        try:
            config.read(config_file)
            self.app_name = config.get(
                'Settings', 'app_name', fallback='My Application')
            self.library_name = config.get(
                'Dependencies', 'core_libraries', fallback='productivity_app')
        except Exception as e:
            print(f"Warning: Could not read installation_settings.ini: {e}")
            self.app_name = 'My Application'
            self.library_name = 'productivity_app'

    def identify_cleanup_targets(self):
        """Identify all files and directories that should be cleaned up"""

        # Files created in project root by Step 5
        project_files = REQUIRED_FILES.copy()

        # Directories created by bootstrap process
        project_dirs = [
            self.venv_dir_name  # Virtual environment from Step 2
        ]

        # Check which files actually exist
        for file in project_files:
            file_path = self.project_dir / file
            if file_path.exists():
                self.files_to_remove.append(file_path)

        # Check which directories actually exist
        for dir_name in project_dirs:
            dir_path = self.project_dir / dir_name
            if dir_path.exists():
                self.dirs_to_remove.append(dir_path)

        # for dir_name in bootstrapper_dirs:
        #     dir_path = self.script_dir / dir_name
        #     if dir_path.exists():
        #         self.dirs_to_remove.append(dir_path)

        # Also check for any .pyc files or other Python cache
        for pyc_file in self.script_dir.rglob("*.pyc"):
            self.files_to_remove.append(pyc_file)

    def show_cleanup_gui(self):
        """Show GUI with cleanup options"""
        root = tk.Tk()
        root.title(f"{self.app_name} - Bootstrap Cleanup")
        root.geometry("600x500")
        root.resizable(True, True)

        # Title
        title_label = tk.Label(root, text="Bootstrap Cleanup Tool",
                               font=("Segoe UI", 14, "bold"))
        title_label.pack(pady=10)

        info_label = tk.Label(root, text="The following files and directories will be removed:",
                              font=("Segoe UI", 10))
        info_label.pack(pady=5)

        # Create scrollable list
        frame = ttk.Frame(root)
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Listbox with scrollbar
        listbox_frame = ttk.Frame(frame)
        listbox_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set,
                             font=("Consolas", 9))
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=listbox.yview)

        # Populate list
        if self.files_to_remove or self.dirs_to_remove:
            listbox.insert(tk.END, "FILES TO REMOVE:")
            for file_path in self.files_to_remove:
                relative_path = file_path.relative_to(self.project_dir.parent)
                listbox.insert(tk.END, f"  📄 {relative_path}")

            if self.dirs_to_remove:
                listbox.insert(tk.END, "")
                listbox.insert(tk.END, "DIRECTORIES TO REMOVE:")
                for dir_path in self.dirs_to_remove:
                    relative_path = dir_path.relative_to(
                        self.project_dir.parent)
                    listbox.insert(tk.END, f"  📁 {relative_path}")
        else:
            listbox.insert(tk.END, "✅ No bootstrap files found to clean up!")

        # Buttons
        button_frame = ttk.Frame(root)
        button_frame.pack(pady=20)

        if self.files_to_remove or self.dirs_to_remove:
            cleanup_btn = ttk.Button(button_frame, text="🗑️ Clean Up All",
                                     command=lambda: self.perform_cleanup(root))
            cleanup_btn.pack(side="left", padx=10)

        cancel_btn = ttk.Button(button_frame, text="Cancel",
                                command=root.destroy)
        cancel_btn.pack(side="left", padx=10)

        # Warning message
        if self.files_to_remove or self.dirs_to_remove:
            warning_label = tk.Label(root,
                                     text="⚠️ Warning: This action cannot be undone!",
                                     fg="red", font=("Segoe UI", 10, "bold"))
            warning_label.pack(pady=5)

        root.mainloop()

    def perform_cleanup(self, root):
        """Perform the actual cleanup"""
        result = messagebox.askyesno("Confirm Cleanup",
                                     f"Are you sure you want to remove {len(self.files_to_remove)} files "
                                     f"and {len(self.dirs_to_remove)} directories?\n\n"
                                     "This action cannot be undone!")

        if not result:
            return

        # Create progress window
        progress_window = tk.Toplevel(root)
        progress_window.title("Cleaning Up...")
        progress_window.geometry("400x150")
        progress_window.resizable(False, False)
        progress_window.grab_set()  # Make it modal

        # Center the progress window
        progress_window.transient(root)
        progress_window.geometry(
            "+%d+%d" % (root.winfo_rootx() + 100, root.winfo_rooty() + 100))

        status_label = ttk.Label(progress_window, text="Starting cleanup...",
                                 font=("Segoe UI", 10))
        status_label.pack(pady=20)

        progress = ttk.Progressbar(
            progress_window, length=350, mode='determinate')
        progress.pack(pady=10)

        total_items = len(self.files_to_remove) + len(self.dirs_to_remove)
        progress['maximum'] = total_items

        errors = []
        completed = 0

        try:
            # Remove files
            for file_path in self.files_to_remove:
                status_label.config(text=f"Removing file: {file_path.name}")
                progress_window.update()

                try:
                    file_path.unlink()
                    print(f"Removed file: {file_path}")
                except Exception as e:
                    errors.append(f"Failed to remove file {file_path}: {e}")

                completed += 1
                progress['value'] = completed
                progress_window.update()

            # Remove directories
            for dir_path in self.dirs_to_remove:
                status_label.config(
                    text=f"Removing directory: {dir_path.name}")
                progress_window.update()

                try:
                    shutil.rmtree(dir_path)
                    print(f"Removed directory: {dir_path}")
                except Exception as e:
                    errors.append(
                        f"Failed to remove directory {dir_path}: {e}")

                completed += 1
                progress['value'] = completed
                progress_window.update()

            progress_window.destroy()

            # Show results
            if errors:
                error_msg = "Cleanup completed with errors:\n\n" + \
                    "\n".join(errors)
                messagebox.showwarning(
                    "Cleanup Completed with Errors", error_msg)
            else:
                messagebox.showinfo("Cleanup Completed",
                                    f"Successfully removed {len(self.files_to_remove)} files "
                                    f"and {len(self.dirs_to_remove)} directories!")

            root.destroy()

        except Exception as e:
            progress_window.destroy()
            messagebox.showerror(
                "Cleanup Failed", f"An error occurred during cleanup: {e}")

    def run_console_cleanup(self):
        """Run cleanup in console mode"""
        print(f"\n{self.app_name} - Bootstrap Cleanup Tool")
        print("=" * 50)

        if not self.files_to_remove and not self.dirs_to_remove:
            print("✅ No bootstrap files found to clean up!")
            return

        print(
            f"\nFound {len(self.files_to_remove)} files and {len(self.dirs_to_remove)} directories to remove:")

        print("\nFILES:")
        for file_path in self.files_to_remove:
            relative_path = file_path.relative_to(self.project_dir.parent)
            print(f"  📄 {relative_path}")

        print("\nDIRECTORIES:")
        for dir_path in self.dirs_to_remove:
            relative_path = dir_path.relative_to(self.project_dir.parent)
            print(f"  📁 {relative_path}")

        print(
            f"\n⚠️ Warning: This will permanently delete {len(self.files_to_remove) + len(self.dirs_to_remove)} items!")

        confirm = input("\nProceed with cleanup? (y/N): ").strip().lower()

        if confirm != 'y':
            print("Cleanup cancelled.")
            return

        print("\nPerforming cleanup...")
        errors = []

        # Remove files
        for file_path in self.files_to_remove:
            try:
                file_path.unlink()
                print(f"✅ Removed: {file_path.name}")
            except Exception as e:
                errors.append(f"❌ Failed to remove {file_path}: {e}")

        # Remove directories
        for dir_path in self.dirs_to_remove:
            try:
                shutil.rmtree(dir_path)
                print(f"✅ Removed: {dir_path.name}/")
            except Exception as e:
                errors.append(f"❌ Failed to remove {dir_path}: {e}")

        if errors:
            print(f"\n⚠️ Cleanup completed with {len(errors)} errors:")
            for error in errors:
                print(f"  {error}")
        else:
            print(
                f"\n🎉 Cleanup completed successfully! Removed {len(self.files_to_remove) + len(self.dirs_to_remove)} items.")


def main():
    """Main entry point"""
    cleanup = BootstrapCleanup()

    # Check if running with GUI or console
    if len(sys.argv) > 1 and sys.argv[1] in ['--console', '-c']:
        cleanup.run_console_cleanup()
    else:
        try:
            cleanup.show_cleanup_gui()
        except Exception as e:
            print(f"GUI failed, falling back to console mode: {e}")
            cleanup.run_console_cleanup()


if __name__ == "__main__":
    main()
