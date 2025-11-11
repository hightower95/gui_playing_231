#!/usr/bin/env python3

"""
Test script to verify enable_folder_selection with actual install_settings.ini
"""

from install_gui.steps.folder_step import GetFolderStep
import sys
from pathlib import Path
import configparser

# Add installer path to sys.path
installer_path = Path(__file__).parent
sys.path.insert(0, str(installer_path))


def test_with_actual_config():
    """Test with the actual install_settings.ini file"""
    print("=== TESTING WITH ACTUAL install_settings.ini ===")

    # Load the actual config file
    config_path = Path(__file__).parent / "install_settings.ini"
    print(f"Loading config from: {config_path}")

    if not config_path.exists():
        print("ERROR: install_settings.ini not found!")
        return

    config = configparser.ConfigParser()
    config.read(config_path)

    # Show current settings
    print(f"\nCurrent settings in file:")
    try:
        enable_selection = config.getboolean(
            'Step_Select_Folder', 'enable_folder_selection', fallback=True)
        print(f"  enable_folder_selection = {enable_selection}")

        lock_to_local = config.getboolean(
            'Step_Select_Folder', 'lock_install_to_local_hard_drive', fallback=False)
        print(f"  lock_install_to_local_hard_drive = {lock_to_local}")

        restrictions = config.get(
            'Step_Select_Folder', 'hard_drive_letter_restrictions', fallback=None)
        print(f"  hard_drive_letter_restrictions = {restrictions}")

        default_folder = config.get(
            'Step_Select_Folder', 'default_installation_folder', fallback=None)
        print(f"  default_installation_folder = {default_folder}")

    except Exception as e:
        print(f"  Error reading settings: {e}")

    # Create folder step with actual config
    shared_state = {}
    folder_step = GetFolderStep(config, shared_state)

    print(f"\nFolder step behavior:")
    print(
        f"  _is_folder_selection_enabled(): {folder_step._is_folder_selection_enabled()}")
    print(f"  get_hint_text(): {folder_step.get_hint_text()}")
    print(f"  Default path: {folder_step._default_path}")
    print(f"  Current path: {folder_step._current_path}")
    print(f"  can_complete(): {folder_step.can_complete()}")

    # Test drive validation
    print(f"\nDrive validation test:")
    test_paths = ["C:\\TestPath", "D:\\TestPath"]
    for test_path in test_paths:
        is_allowed = folder_step._is_drive_allowed(test_path)
        print(f"  {test_path} -> Allowed: {is_allowed}")


def test_enable_false():
    """Test by temporarily changing enable_folder_selection to false"""
    print("\n=== TESTING WITH enable_folder_selection = false ===")

    # Load config and modify it
    config_path = Path(__file__).parent / "install_settings.ini"
    config = configparser.ConfigParser()
    config.read(config_path)

    # Temporarily set to false
    config.set('Step_Select_Folder', 'enable_folder_selection', 'false')

    # Test with modified config
    shared_state = {}
    folder_step = GetFolderStep(config, shared_state)

    print(
        f"  _is_folder_selection_enabled(): {folder_step._is_folder_selection_enabled()}")
    print(f"  get_hint_text(): {folder_step.get_hint_text()}")
    print(f"  Should be disabled and show pre-configured message")


if __name__ == "__main__":
    test_with_actual_config()
    test_enable_false()
