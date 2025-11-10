#!/usr/bin/env python3

"""
Comprehensive test to verify folder selection is blocked when enabled_folder_selection = false
"""

import configparser
from install_gui.steps.folder_step import GetFolderStep
from PySide6.QtWidgets import QApplication
import sys
from pathlib import Path

# Add installer path to sys.path
installer_path = Path(__file__).parent
sys.path.insert(0, str(installer_path))


def test_folder_selection_blocking():
    """Test that folder selection is truly blocked"""
    print("=== COMPREHENSIVE FOLDER SELECTION BLOCKING TEST ===")

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    # Create config with folder selection DISABLED
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
    folder_step = GetFolderStep(config, shared_state)

    # Create minimal UI widgets to test
    from PySide6.QtWidgets import QWidget, QVBoxLayout
    widget = QWidget()
    layout = QVBoxLayout()
    folder_step.create_widgets(widget, layout)

    original_path = folder_step._default_path
    print(f"1. Original default path: {original_path}")
    print(f"2. Current path input text: {folder_step.path_input.text()}")
    print(f"3. Input is read-only: {folder_step.path_input.isReadOnly()}")
    print(f"4. Browse button enabled: {folder_step.browse_button.isEnabled()}")

    # Test 1: Try to change path via setText (programmatic)
    print(f"\n=== TEST 1: Programmatic Path Change ===")
    malicious_path = "D:\\MaliciousPath"
    print(f"Attempting to set path to: {malicious_path}")

    folder_step.path_input.setText(malicious_path)
    print(f"Path after setText: {folder_step.path_input.text()}")
    print(f"Internal _current_path: {folder_step._current_path}")
    print(f"Expected: Should be reverted to original path")

    # Test 2: Try to bypass via _on_path_changed directly
    print(f"\n=== TEST 2: Direct Method Call ===")
    print(f"Calling _on_path_changed('{malicious_path}') directly...")
    folder_step._on_path_changed(malicious_path)
    print(f"Path after direct call: {folder_step.path_input.text()}")
    print(f"Internal _current_path: {folder_step._current_path}")

    # Test 3: Try to browse for folder
    print(f"\n=== TEST 3: Browse Function Call ===")
    print("Calling _browse_for_folder()...")
    try:
        folder_step._browse_for_folder()
        print("Browse function completed (should have shown info dialog)")
    except Exception as e:
        print(f"Browse function error: {e}")

    # Test 4: Try to complete with modified path
    print(f"\n=== TEST 4: Step Completion with Path Verification ===")
    # Force set a malicious path to test completion validation
    folder_step.path_input.setText(malicious_path)
    print(f"Forced path to: {folder_step.path_input.text()}")

    # Try to complete
    can_complete = folder_step.can_complete()
    print(f"can_complete(): {can_complete}")

    if can_complete:
        print("Attempting complete_step()...")
        result = folder_step.complete_step()
        print(f"complete_step() result: {result}")
        print(f"Final path after completion: {folder_step.path_input.text()}")
        print(f"Shared state: {shared_state}")

    # Test 5: Verify all blocking mechanisms
    print(f"\n=== TEST 5: Final Verification ===")
    final_path = folder_step.path_input.text()
    print(f"Final path in input: {final_path}")
    print(f"Is final path same as original: {final_path == original_path}")
    print(f"Path validation result: {folder_step._path_is_valid(final_path)}")

    if final_path == original_path:
        print("✅ SUCCESS: Folder selection properly blocked")
    else:
        print("❌ FAILURE: User was able to change folder selection")
        print(f"   Expected: {original_path}")
        print(f"   Got: {final_path}")


def test_with_actual_installer_config():
    """Test with the actual installer config"""
    print(f"\n=== TEST WITH ACTUAL INSTALLER CONFIG ===")

    config_path = Path(__file__).parent / "install_settings.ini"
    if not config_path.exists():
        print("Installer config not found")
        return

    config = configparser.ConfigParser()
    config.read(config_path)

    # Check current setting
    enable_selection = config.getboolean(
        'Step_Select_Folder', 'enable_folder_selection', fallback=True)
    print(f"Current enable_folder_selection: {enable_selection}")

    if enable_selection:
        print("Config has folder selection enabled - test with disabled setting")
        config.set('Step_Select_Folder', 'enable_folder_selection', 'false')

    shared_state = {}
    folder_step = GetFolderStep(config, shared_state)

    from PySide6.QtWidgets import QWidget, QVBoxLayout
    widget = QWidget()
    layout = QVBoxLayout()
    folder_step.create_widgets(widget, layout)

    print(
        f"Folder selection enabled: {folder_step._is_folder_selection_enabled()}")
    print(f"Browse button enabled: {folder_step.browse_button.isEnabled()}")
    print(f"Path input read-only: {folder_step.path_input.isReadOnly()}")
    print(f"Default installation path: {folder_step._default_path}")


if __name__ == "__main__":
    test_folder_selection_blocking()
    test_with_actual_installer_config()
