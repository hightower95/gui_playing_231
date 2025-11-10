#!/usr/bin/env python3

"""
Test script to simulate folder dialog selection and trace validation
"""

import configparser
from install_gui.steps.folder_step import GetFolderStep
from PySide6.QtWidgets import QApplication
import sys
from pathlib import Path

# Add installer path to sys.path
installer_path = Path(__file__).parent
sys.path.insert(0, str(installer_path))

# Import PySide6 for GUI testing


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


def simulate_folder_selection():
    """Simulate what happens when user selects folder from dialog"""
    print("=== SIMULATING FOLDER DIALOG SELECTION ===")

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    config = create_test_config()
    shared_state = {}

    step = GetFolderStep(config, shared_state)

    # Create minimal UI to test the flow
    from PySide6.QtWidgets import QWidget, QVBoxLayout
    widget = QWidget()
    layout = QVBoxLayout()
    widget.setLayout(layout)

    # Initialize the step widgets
    step.create_widgets(widget, layout)

    print("Step initialized with widgets")
    print(f"Initial path: {step.path_input.text()}")
    print()

    # Simulate user selecting D: drive folder
    test_path = "D:\\SomeFolder"
    print(f"Simulating user selection of: {test_path}")

    # This is what happens when QFileDialog returns a path
    print("\n1. Setting path_input.setText()...")
    step.path_input.setText(test_path)
    print(f"   path_input.text() = {step.path_input.text()}")

    print("\n2. _on_path_changed() should be triggered...")
    # This should trigger automatically via signal, but let's call it manually too
    step._on_path_changed(test_path)
    print(f"   step._current_path = {step._current_path}")

    print("\n3. _validate_path_real_time() called...")
    step._path_is_valid(test_path)
    print(f"   Feedback label text: {step.feedback_label.text()}")

    print("\n4. Testing complete_step() validation...")
    can_complete = step.can_complete()
    print(f"   can_complete(): {can_complete}")

    if can_complete:
        # This should fail due to drive restrictions
        print("\n5. Attempting complete_step()...")
        result = step.complete_step()
        print(f"   complete_step() result: {result}")

        if result:
            print("   ERROR: Step completed successfully when it should have failed!")
        else:
            print("   GOOD: Step failed as expected")

    widget.show()
    print("\nGUI shown - check feedback label for D: path validation")

    # Don't run app.exec() to avoid blocking


if __name__ == "__main__":
    simulate_folder_selection()
