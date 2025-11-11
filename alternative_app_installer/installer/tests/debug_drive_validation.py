#!/usr/bin/env python3
"""
Debug script to test drive validation logic specifically
"""
from install_gui.steps.folder_step import GetFolderStep
import sys
from pathlib import Path
from configparser import ConfigParser

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))


def debug_drive_validation():
    """Debug the drive validation logic"""
    print("Debugging Drive Validation Logic")
    print("=" * 50)

    # Create test configuration
    config = ConfigParser()
    config.read('install_settings.ini')

    # Create shared state
    shared_state = {}

    # Create folder step instance
    folder_step = GetFolderStep(config, shared_state)

    print("Configuration check:")
    print(
        f"  lock_install_to_local_hard_drive: {config.getboolean('Step_Select_Folder', 'lock_install_to_local_hard_drive', fallback=False)}")
    print(
        f"  hard_drive_letter_restrictions: {config.get('Step_Select_Folder', 'hard_drive_letter_restrictions', fallback=None)}")

    # Test specific paths
    test_paths = [
        r"D:\TestApp",
        r"D:\Test\Path",
        r"C:\TestApp"
    ]

    for test_path in test_paths:
        print(f"\nTesting path: {test_path}")

        # Extract drive letter manually to debug
        path_obj = Path(test_path)
        drive_part = path_obj.parts[0]
        if ':' in drive_part:
            drive_letter = drive_part.rstrip(':\\').upper()
        else:
            drive_letter = "UNKNOWN"
        print(f"  Extracted drive letter: '{drive_letter}'")

        # Test our method
        is_allowed = folder_step._is_drive_allowed(test_path)
        print(f"  _is_drive_allowed result: {is_allowed}")

        # Test real-time validation
        print("  Real-time validation check:")
        folder_step._current_path = test_path
        folder_step._path_is_valid(test_path)

        if hasattr(folder_step, 'feedback_label') and folder_step.feedback_label:
            feedback_text = folder_step.feedback_label.text()
            print(f"  Feedback text: '{feedback_text}'")

        print("-" * 30)


if __name__ == "__main__":
    debug_drive_validation()
