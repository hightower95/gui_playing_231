#!/usr/bin/env python3

"""
Test script to launch the actual GUI and check D: drive behavior
"""

import configparser
from install_gui.steps.folder_step import GetFolderStep
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
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


def main():
    app = QApplication(sys.argv)

    # Create main window
    window = QWidget()
    window.setWindowTitle("Test Drive Validation")
    window.setGeometry(100, 100, 600, 400)

    layout = QVBoxLayout()
    window.setLayout(layout)

    # Instructions
    instructions = QLabel("""
DRIVE VALIDATION TEST

Instructions:
1. Try typing 'D:\\TestPath' in the path field
2. Try using Browse button and navigate to D: drive
3. Watch the feedback label for warnings
4. Try clicking the Complete button

Expected: Should show "Path must be on allowed drive: C:" warning
""")
    instructions.setWordWrap(True)
    layout.addWidget(instructions)

    # Create the folder step
    config = create_test_config()
    shared_state = {}

    folder_step = GetFolderStep(config, shared_state)
    folder_step.create_widgets(window, layout)

    # Add complete button to test validation
    complete_button = QPushButton("Test Complete Step")

    def test_complete():
        print(f"\nTesting complete_step()...")
        print(f"Current path: {folder_step.path_input.text()}")
        print(f"can_complete(): {folder_step.can_complete()}")

        result = folder_step.complete_step()
        print(f"complete_step() result: {result}")

        if result:
            print("✅ Step completed - path is valid")
        else:
            print("❌ Step failed - path is invalid")

    complete_button.clicked.connect(test_complete)
    layout.addWidget(complete_button)

    # Status display
    status_label = QLabel("Watch feedback below...")
    layout.addWidget(status_label)

    window.show()

    print("GUI launched - Test drive validation behavior:")
    print("1. Type 'D:\\TestPath' in the input field")
    print("2. Watch for immediate feedback")
    print("3. Click 'Test Complete Step' button")
    print("4. Try Browse button and select D: drive folder")

    app.exec()


if __name__ == "__main__":
    main()
