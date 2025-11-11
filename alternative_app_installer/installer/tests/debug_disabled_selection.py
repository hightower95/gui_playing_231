#!/usr/bin/env python3

"""
Debug script to test folder selection when enable_folder_selection = false
"""

import configparser
from install_gui.steps.folder_step import GetFolderStep
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
import sys
from pathlib import Path

# Add installer path to sys.path
installer_path = Path(__file__).parent
sys.path.insert(0, str(installer_path))


def test_disabled_folder_selection_gui():
    """Test GUI behavior when folder selection is disabled"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

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

    # Create main window
    window = QWidget()
    window.setWindowTitle("Test DISABLED Folder Selection")
    window.setGeometry(100, 100, 600, 400)

    layout = QVBoxLayout()
    window.setLayout(layout)

    # Instructions
    instructions = QLabel("""
FOLDER SELECTION DISABLED TEST

When enable_folder_selection = false:
- Browse button should be DISABLED (grayed out)
- Path input should be READ-ONLY (grayed background)
- Clicking Browse should show info message, not file dialog
- Typing in path field should not work

Try the following:
1. Check if Browse button is disabled
2. Try clicking Browse button
3. Try typing in the path field
4. Check that the path is still valid for installation
""")
    instructions.setWordWrap(True)
    layout.addWidget(instructions)

    # Create the folder step
    shared_state = {}
    folder_step = GetFolderStep(config, shared_state)
    folder_step.create_widgets(window, layout)

    # Add test buttons
    test_layout = QVBoxLayout()

    def check_state():
        print("\n=== CHECKING DISABLED STATE ===")
        print(
            f"enable_folder_selection: {folder_step._is_folder_selection_enabled()}")
        print(
            f"Browse button enabled: {folder_step.browse_button.isEnabled()}")
        print(
            f"Browse button tooltip: '{folder_step.browse_button.toolTip()}'")
        print(f"Path input read-only: {folder_step.path_input.isReadOnly()}")
        print(f"Current path: {folder_step.path_input.text()}")
        print(f"Hint text: {folder_step.get_hint_text()}")

    def test_browse():
        print("\n=== TESTING BROWSE BUTTON ===")
        print("Calling _browse_for_folder()...")
        folder_step._browse_for_folder()

    def test_manual_path_change():
        print("\n=== TESTING MANUAL PATH CHANGE ===")
        old_path = folder_step.path_input.text()
        print(f"Current path: {old_path}")

        # Try to set a new path programmatically
        new_path = "D:\\TestFolder"
        print(f"Attempting to set path to: {new_path}")
        folder_step.path_input.setText(new_path)
        print(f"Path after setText: {folder_step.path_input.text()}")

        # Check if the change was processed
        print(f"Internal _current_path: {folder_step._current_path}")

        # Reset
        folder_step.path_input.setText(old_path)

    def test_complete():
        print("\n=== TESTING STEP COMPLETION ===")
        print(f"can_complete(): {folder_step.can_complete()}")

        if folder_step.can_complete():
            result = folder_step.complete_step()
            print(f"complete_step() result: {result}")
            if result:
                print("✅ Step completed successfully")
                print(f"Shared state: {folder_step.shared_state}")
            else:
                print("❌ Step completion failed")
        else:
            print("❌ Step cannot complete")

    check_btn = QPushButton("Check Current State")
    check_btn.clicked.connect(check_state)
    test_layout.addWidget(check_btn)

    browse_btn = QPushButton("Test Browse (should show message)")
    browse_btn.clicked.connect(test_browse)
    test_layout.addWidget(browse_btn)

    path_btn = QPushButton("Test Manual Path Change")
    path_btn.clicked.connect(test_manual_path_change)
    test_layout.addWidget(path_btn)

    complete_btn = QPushButton("Test Step Completion")
    complete_btn.clicked.connect(test_complete)
    test_layout.addWidget(complete_btn)

    layout.addLayout(test_layout)

    window.show()

    print("=== GUI LAUNCHED ===")
    print("Test that folder selection is truly disabled")
    check_state()

    app.exec()


if __name__ == "__main__":
    test_disabled_folder_selection_gui()
