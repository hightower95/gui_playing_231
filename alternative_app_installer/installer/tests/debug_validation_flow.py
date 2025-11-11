#!/usr/bin/env python3

"""
Debug script to trace validation flow and identify issues with drive restrictions
"""

import configparser
from install_gui.steps.folder_step import GetFolderStep
import sys
from pathlib import Path

# Add installer path to sys.path
installer_path = Path(__file__).parent
sys.path.insert(0, str(installer_path))


def create_test_config():
    """Create test configuration with drive restrictions"""
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

    return config


def test_validation_methods():
    """Test all validation methods with D: path"""
    print("=== VALIDATION FLOW DEBUGGING ===")

    config = create_test_config()
    shared_state = {}

    step = GetFolderStep(config, shared_state)

    test_path = "D:\\TestPath"
    print(f"Testing path: {test_path}")
    print()

    # Test individual validation methods
    print("1. _is_drive_allowed():")
    result1 = step._is_drive_allowed(test_path)
    print(f"   Result: {result1}")
    print()

    print("2. _is_location_accessible():")
    result2 = step._is_location_accessible(test_path)
    print(f"   Result: {result2}")
    print()

    print("3. _is_location_accessible_and_allowed() [first definition]:")
    # Check both definitions by calling them directly
    result3a = step._is_location_accessible(
        test_path) and step._is_drive_allowed(test_path)
    print(f"   Result: {result3a}")
    print()

    print("4. _is_location_accessible_and_allowed() [actual method]:")
    result3b = step._is_location_accessible_and_allowed(test_path)
    print(f"   Result: {result3b}")
    print()

    # Test high-level validation methods
    print("5. _validate_installation_path() [complete validation]:")
    # We can't easily test this without GUI, but let's check the drive part
    drive_check = step._is_drive_allowed(test_path)
    print(f"   Drive check within validation: {drive_check}")
    print()

    print("6. Method resolution order check:")
    print(
        f"   _is_location_accessible_and_allowed in dir(): {'_is_location_accessible_and_allowed' in dir(step)}")
    print(f"   Method object: {step._is_location_accessible_and_allowed}")
    print()

    # Test what happens in default folder selection
    print("7. Default folder selection:")
    default_folder = step._get_default_installation_folder()
    print(f"   Default folder: {default_folder}")
    print()


if __name__ == "__main__":
    test_validation_methods()
