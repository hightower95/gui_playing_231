#!/usr/bin/env python3
"""
Test script to verify Step_Select_Folder configuration and drive restrictions
"""
from install_gui.steps.folder_step import GetFolderStep
import sys
from pathlib import Path
from configparser import ConfigParser

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))


def test_step_select_folder_config():
    """Test the Step_Select_Folder configuration features"""
    print("Testing Step_Select_Folder Configuration")
    print("=" * 60)

    # Create test configuration
    config = ConfigParser()
    config.read('install_settings.ini')

    # Create shared state
    shared_state = {}

    # Create folder step instance
    folder_step = GetFolderStep(config, shared_state)

    print("1. Configuration Section Reading:")
    print(f"   Config sections: {list(config.sections())}")
    print(
        f"   Has Step_Select_Folder: {'Step_Select_Folder' in config.sections()}")

    if 'Step_Select_Folder' in config.sections():
        print("   Step_Select_Folder options:")
        for option in config.options('Step_Select_Folder'):
            value = config.get('Step_Select_Folder', option)
            print(f"     {option}: {value}")

    print("\n2. Default Installation Path:")
    if hasattr(folder_step, '_current_path'):
        print(f"   Selected default path: {folder_step._current_path}")

        # Test drive validation
        drive_allowed = folder_step._is_drive_allowed(
            folder_step._current_path)
        print(f"   Drive allowed: {drive_allowed}")

        allowed_drives = folder_step._get_allowed_drives_display()
        print(f"   Allowed drives: {allowed_drives}")

    print("\n3. Drive Restriction Tests:")
    test_paths = [
        r"C:\Test\Path",
        r"D:\Test\Path",
        r"E:\Test\Path",
        r"Z:\Test\Path",
        r"\\network\path"  # Network path test
    ]

    for test_path in test_paths:
        try:
            is_allowed = folder_step._is_drive_allowed(test_path)
            path_obj = Path(test_path)
            drive_letter = path_obj.parts[0].rstrip(
                ':').upper() if path_obj.parts else "Unknown"
            print(
                f"   {test_path:20} -> Drive: {drive_letter:2} -> Allowed: {is_allowed}")
        except Exception as e:
            print(f"   {test_path:20} -> Error: {e}")

    print("\n4. Template Expansion Test:")
    test_templates = [
        "{parent_folder}",
        "C:\\Users\\{username}",
        "{parent_folder}\\MyApp"
    ]

    for template in test_templates:
        try:
            expanded = folder_step._expand_template_variables(template)
            print(f"   Template: {template:30} -> {expanded}")
        except Exception as e:
            print(f"   Template: {template:30} -> Error: {e}")

    print("\n5. Step Validation Test:")
    print(f"   Can complete step: {folder_step.can_complete()}")
    print(
        f"   Current path accessible: {folder_step._is_location_accessible_and_allowed(folder_step._current_path)}")

    print("\n✅ Test completed!")


if __name__ == "__main__":
    test_step_select_folder_config()
