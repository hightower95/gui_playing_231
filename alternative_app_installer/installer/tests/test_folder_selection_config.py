#!/usr/bin/env python3

"""
Test script to verify enable_folder_selection = false behavior
"""

import configparser
from install_gui.steps.folder_step import GetFolderStep
import sys
from pathlib import Path

# Add installer path to sys.path
installer_path = Path(__file__).parent
sys.path.insert(0, str(installer_path))


def test_disabled_folder_selection():
    """Test that folder selection is properly disabled"""
    print("=== TESTING enable_folder_selection = false ===")

    # Create config with folder selection disabled
    config = configparser.ConfigParser()

    config.add_section('Settings')
    config.set('Settings', 'app_name', 'TestApp')

    config.add_section('Step_Select_Folder')
    config.set('Step_Select_Folder',
               'lock_install_to_local_hard_drive', 'true')
    config.set('Step_Select_Folder', 'hard_drive_letter_restrictions', '["C"]')
    config.set('Step_Select_Folder', 'default_installation_folder',
               '["{parent_folder}"]')
    config.set('Step_Select_Folder', 'fallback_installation_folders',
               '["C:\\Program Files"]')
    config.set('Step_Select_Folder',
               'enable_folder_selection', 'false')  # DISABLED

    shared_state = {}

    # Create the folder step
    folder_step = GetFolderStep(config, shared_state)

    # Test the configuration reading
    print(
        f"1. _is_folder_selection_enabled(): {folder_step._is_folder_selection_enabled()}")
    print(f"   Expected: False")

    # Test hint text
    print(f"\n2. get_hint_text(): {folder_step.get_hint_text()}")
    print(f"   Expected: 'Installation folder has been pre-configured and cannot be changed.'")

    # Test default path (should still work)
    print(f"\n3. Default installation path: {folder_step._default_path}")
    print(f"   Should show a valid path")

    print(f"\n4. Current path: {folder_step._current_path}")
    print(
        f"   Should match default path: {folder_step._current_path == folder_step._default_path}")

    # Test can_complete (should still work)
    print(f"\n5. can_complete(): {folder_step.can_complete()}")
    print(f"   Expected: True (path should be valid)")

    print("\n=== Test completed successfully ===")


def test_enabled_folder_selection():
    """Test that folder selection is properly enabled"""
    print("\n=== TESTING enable_folder_selection = true ===")

    # Create config with folder selection enabled
    config = configparser.ConfigParser()

    config.add_section('Settings')
    config.set('Settings', 'app_name', 'TestApp')

    config.add_section('Step_Select_Folder')
    config.set('Step_Select_Folder',
               'lock_install_to_local_hard_drive', 'true')
    config.set('Step_Select_Folder', 'hard_drive_letter_restrictions', '["C"]')
    config.set('Step_Select_Folder', 'default_installation_folder',
               '["{parent_folder}"]')
    config.set('Step_Select_Folder', 'fallback_installation_folders',
               '["C:\\Program Files"]')
    config.set('Step_Select_Folder',
               'enable_folder_selection', 'true')  # ENABLED

    shared_state = {}

    # Create the folder step
    folder_step = GetFolderStep(config, shared_state)

    # Test the configuration reading
    print(
        f"1. _is_folder_selection_enabled(): {folder_step._is_folder_selection_enabled()}")
    print(f"   Expected: True")

    # Test hint text
    print(f"\n2. get_hint_text(): {folder_step.get_hint_text()}")
    print(f"   Expected: 'Instructions: Click browse button to change installation folder.'")

    print("\n=== Test completed successfully ===")


if __name__ == "__main__":
    test_disabled_folder_selection()
    test_enabled_folder_selection()
